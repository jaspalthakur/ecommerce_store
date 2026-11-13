import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, abort, session, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
from models import db, User, Product, Category, CartItem, Order, OrderItem, WishlistItem, Review

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-me")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///store.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return wrapper


# ---------- CONTEXT PROCESSOR ----------
@app.context_processor
def inject_global_data():
    cart_count = 0
    wishlist_count = 0
    wishlist_ids = set()
    if current_user.is_authenticated:
        cart_count = db.session.query(db.func.sum(CartItem.quantity)).filter_by(
            user_id=current_user.id
        ).scalar() or 0
        wishlist_items = WishlistItem.query.filter_by(user_id=current_user.id).all()
        wishlist_count = len(wishlist_items)
        wishlist_ids = {item.product_id for item in wishlist_items}
    return {
        "cart_count": cart_count,
        "wishlist_count": wishlist_count,
        "user_wishlist_ids": wishlist_ids
    }


# ---------- PUBLIC ROUTES ----------
@app.route("/")
def index():
    q = request.args.get("q", "").strip()
    cat_slug = request.args.get("category")
    sort = request.args.get("sort", "newest")
    max_price = request.args.get("max_price")
    in_stock = request.args.get("in_stock")
    
    query = Product.query
    if q:
        query = query.filter(Product.name.ilike(f"%{q}%") | Product.description.ilike(f"%{q}%"))
    if cat_slug:
        query = query.join(Category).filter(Category.slug == cat_slug)
    if max_price:
        try:
            query = query.filter(Product.price <= float(max_price))
        except ValueError:
            pass
    if in_stock == "1":
        query = query.filter(Product.stock > 0)
        
    if sort == "price_asc":
        query = query.order_by(Product.price.asc())
    elif sort == "price_desc":
        query = query.order_by(Product.price.desc())
    elif sort == "name_asc":
        query = query.order_by(Product.name.asc())
    else:
        query = query.order_by(Product.created_at.desc())
        
    products = query.all()
    categories = Category.query.all()
    return render_template("index.html", products=products, categories=categories,
                           q=q, active_cat=cat_slug, sort=sort,
                           max_price=max_price, in_stock=in_stock)


@app.route("/product/<int:pid>")
def product_detail(pid):
    product = db.session.get(Product, pid) or abort(404)
    related = Product.query.filter(
        Product.category_id == product.category_id,
        Product.id != product.id
    ).limit(4).all()
    reviews = Review.query.filter_by(product_id=pid).order_by(Review.created_at.desc()).all()
    return render_template("product.html", product=product, related_products=related, reviews=reviews)


@app.route("/product/<int:pid>/review", methods=["POST"])
@login_required
def add_review(pid):
    product = db.session.get(Product, pid) or abort(404)
    rating = int(request.form.get("rating", 5))
    comment = request.form.get("comment", "").strip()
    if not comment:
        flash("Please provide a review comment.", "danger")
        return redirect(url_for("product_detail", pid=pid))
    
    review = Review(
        user_id=current_user.id,
        product_id=pid,
        rating=max(1, min(5, rating)),
        comment=comment
    )
    db.session.add(review)
    db.session.commit()
    flash("Thank you! Your verified review has been posted.", "success")
    return redirect(url_for("product_detail", pid=pid))


# ---------- LIVE SEARCH API ----------
@app.route("/api/search")
def api_search():
    q = request.args.get("q", "").strip()
    if not q or len(q) < 2:
        return jsonify([])
    products = Product.query.filter(
        Product.name.ilike(f"%{q}%") | Product.description.ilike(f"%{q}%")
    ).limit(6).all()
    results = [{
        "id": p.id,
        "name": p.name,
        "price": p.price,
        "image_url": p.image_url,
        "category": p.category.name if p.category else ""
    } for p in products]
    return jsonify(results)


# ---------- WISHLIST ----------
@app.route("/wishlist")
@login_required
def wishlist():
    items = WishlistItem.query.filter_by(user_id=current_user.id).all()
    return render_template("wishlist.html", items=items)


@app.route("/wishlist/toggle/<int:pid>", methods=["POST"])
@login_required
def toggle_wishlist(pid):
    product = db.session.get(Product, pid) or abort(404)
    item = WishlistItem.query.filter_by(user_id=current_user.id, product_id=pid).first()
    if item:
        db.session.delete(item)
        db.session.commit()
        flash(f"Removed {product.name} from your wishlist.", "info")
    else:
        db.session.add(WishlistItem(user_id=current_user.id, product_id=pid))
        db.session.commit()
        flash(f"Saved {product.name} to your wishlist ❤️", "success")
    return redirect(request.referrer or url_for("index"))


@app.route("/wishlist/move-to-cart/<int:pid>", methods=["POST"])
@login_required
def wishlist_move_to_cart(pid):
    product = db.session.get(Product, pid) or abort(404)
    if product.stock <= 0:
        flash("This product is currently out of stock.", "warning")
        return redirect(url_for("wishlist"))
        
    WishlistItem.query.filter_by(user_id=current_user.id, product_id=pid).delete()
    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=pid).first()
    if cart_item:
        cart_item.quantity = min(cart_item.quantity + 1, product.stock)
    else:
        db.session.add(CartItem(user_id=current_user.id, product_id=pid, quantity=1))
    db.session.commit()
    flash(f"Moved {product.name} to your cart!", "success")
    return redirect(url_for("cart"))


# ---------- AUTH ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        name = request.form.get("name", "").strip()
        password = request.form.get("password", "")
        if not email or not name or len(password) < 6:
            flash("Please fill all fields. Password must be 6+ chars.", "danger")
            return redirect(url_for("register"))
        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "danger")
            return redirect(url_for("register"))
        user = User(email=email, name=name)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash("Welcome! Your account is created.", "success")
        return redirect(url_for("index"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user, remember=True)
            flash(f"Welcome back, {user.name}!", "success")
            return redirect(request.args.get("next") or url_for("index"))
        flash("Invalid email or password.", "danger")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.", "info")
    return redirect(url_for("index"))


# ---------- USER PROFILE ----------
@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        default_address = request.form.get("default_address", "").strip()
        if not name:
            flash("Name cannot be empty.", "danger")
            return redirect(url_for("profile"))
        current_user.name = name
        current_user.phone = phone
        current_user.default_address = default_address
        db.session.commit()
        flash("Your profile and shipping details have been updated!", "success")
        return redirect(url_for("profile"))
    return render_template("profile.html")


# ---------- CART & CHECKOUT HELPERS ----------
def calculate_cart_totals(items):
    subtotal = sum(i.product.price * i.quantity for i in items)
    coupon = session.get("coupon")
    discount = 0.0
    if coupon == "WELCOME10":
        discount = round(subtotal * 0.10, 2)
    elif coupon == "SAVE20":
        discount = round(subtotal * 0.20, 2)
        
    shipping = 0.0 if (subtotal - discount >= 50.0 or coupon == "FREESHIP" or subtotal == 0) else 5.00
    total = max(0.0, round(subtotal - discount + shipping, 2))
    return {
        "subtotal": subtotal,
        "discount": discount,
        "shipping": shipping,
        "total": total,
        "coupon": coupon
    }


# ---------- CART ----------
@app.route("/cart")
@login_required
def cart():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    totals = calculate_cart_totals(items)
    return render_template("cart.html", items=items, totals=totals)


@app.route("/cart/add/<int:pid>", methods=["POST"])
@login_required
def add_to_cart(pid):
    product = db.session.get(Product, pid) or abort(404)
    if product.stock <= 0:
        flash("Out of stock.", "warning")
        return redirect(request.referrer or url_for("index"))
    qty = int(request.form.get("quantity", 1))
    item = CartItem.query.filter_by(user_id=current_user.id, product_id=pid).first()
    if item:
        item.quantity = min(item.quantity + qty, product.stock)
    else:
        item = CartItem(user_id=current_user.id, product_id=pid,
                        quantity=min(qty, product.stock))
        db.session.add(item)
    db.session.commit()
    flash(f"Added {product.name} to your cart.", "success")
    return redirect(request.referrer or url_for("index"))


@app.route("/cart/update/<int:item_id>", methods=["POST"])
@login_required
def update_cart(item_id):
    item = db.session.get(CartItem, item_id) or abort(404)
    if item.user_id != current_user.id:
        abort(403)
    qty = int(request.form.get("quantity", 1))
    if qty <= 0:
        db.session.delete(item)
        flash("Item removed from cart.", "info")
    else:
        item.quantity = min(qty, item.product.stock)
        flash("Cart updated.", "info")
    db.session.commit()
    return redirect(url_for("cart"))


@app.route("/cart/remove/<int:item_id>", methods=["POST"])
@login_required
def remove_from_cart(item_id):
    item = db.session.get(CartItem, item_id) or abort(404)
    if item.user_id != current_user.id:
        abort(403)
    db.session.delete(item)
    db.session.commit()
    flash("Item removed.", "info")
    return redirect(url_for("cart"))


@app.route("/cart/apply-coupon", methods=["POST"])
@login_required
def apply_coupon():
    code = request.form.get("coupon_code", "").strip().upper()
    if code in ["WELCOME10", "SAVE20", "FREESHIP"]:
        session["coupon"] = code
        flash(f"Coupon '{code}' applied successfully!", "success")
    else:
        flash("Invalid promo code. Try WELCOME10 (10% off), SAVE20 (20% off), or FREESHIP.", "danger")
    return redirect(url_for("cart"))


@app.route("/cart/remove-coupon", methods=["POST"])
@login_required
def remove_coupon():
    session.pop("coupon", None)
    flash("Coupon removed.", "info")
    return redirect(url_for("cart"))


# ---------- CHECKOUT ----------
@app.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not items:
        flash("Your cart is empty.", "warning")
        return redirect(url_for("index"))
    totals = calculate_cart_totals(items)

    if request.method == "POST":
        address = request.form.get("address", "").strip()
        if len(address) < 10:
            flash("Please provide a valid shipping address.", "danger")
            return redirect(url_for("checkout"))

        # Stock check
        for i in items:
            if i.quantity > i.product.stock:
                flash(f"Not enough stock for {i.product.name}.", "danger")
                return redirect(url_for("cart"))

        order = Order(user_id=current_user.id, total=totals["total"], shipping_address=address)
        db.session.add(order)
        db.session.flush()

        for i in items:
            db.session.add(OrderItem(
                order_id=order.id, product_id=i.product.id,
                product_name=i.product.name, price=i.product.price,
                quantity=i.quantity
            ))
            i.product.stock -= i.quantity
            db.session.delete(i)

        if not current_user.default_address:
            current_user.default_address = address

        session.pop("coupon", None)
        db.session.commit()
        flash(f"Order #{order.id} placed successfully!", "success")
        return redirect(url_for("order_detail", oid=order.id))

    return render_template("checkout.html", items=items, totals=totals, default_address=current_user.default_address or "")


# ---------- ORDERS ----------
@app.route("/orders")
@login_required
def orders():
    status_filter = request.args.get("status")
    query = Order.query.filter_by(user_id=current_user.id)
    if status_filter and status_filter in ["pending", "processing", "shipped", "delivered", "cancelled"]:
        query = query.filter_by(status=status_filter)
    my_orders = query.order_by(Order.created_at.desc()).all()
    return render_template("orders.html", orders=my_orders, active_status=status_filter)


@app.route("/orders/<int:oid>")
@login_required
def order_detail(oid):
    order = db.session.get(Order, oid) or abort(404)
    if order.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    return render_template("order_detail.html", order=order)


@app.route("/orders/<int:oid>/invoice")
@login_required
def order_invoice(oid):
    order = db.session.get(Order, oid) or abort(404)
    if order.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    return render_template("invoice.html", order=order)


# ---------- ADMIN ----------
@app.route("/admin")
@login_required
@admin_required
def admin():
    stats = {
        "products": Product.query.count(),
        "orders": Order.query.count(),
        "users": User.query.count(),
        "revenue": db.session.query(db.func.coalesce(db.func.sum(Order.total), 0)).scalar(),
    }
    products = Product.query.order_by(Product.id.desc()).all()
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    return render_template("admin.html", stats=stats, products=products,
                           orders=recent_orders, categories=Category.query.all())


@app.route("/admin/product/add", methods=["POST"])
@login_required
@admin_required
def admin_add_product():
    name = request.form.get("name", "").strip()
    price = float(request.form.get("price", 0))
    stock = int(request.form.get("stock", 0))
    desc = request.form.get("description", "").strip()
    image = request.form.get("image_url", "").strip()
    cat_id = request.form.get("category_id") or None
    if not name or price <= 0:
        flash("Invalid product data.", "danger")
        return redirect(url_for("admin"))
    db.session.add(Product(name=name, price=price, stock=stock,
                           description=desc, image_url=image,
                           category_id=int(cat_id) if cat_id else None))
    db.session.commit()
    flash("Product added.", "success")
    return redirect(url_for("admin"))


@app.route("/admin/product/<int:pid>/delete", methods=["POST"])
@login_required
@admin_required
def admin_delete_product(pid):
    p = db.session.get(Product, pid) or abort(404)
    CartItem.query.filter_by(product_id=pid).delete()
    db.session.delete(p)
    db.session.commit()
    flash("Product deleted.", "info")
    return redirect(url_for("admin"))


@app.route("/admin/order/<int:oid>/status", methods=["POST"])
@login_required
@admin_required
def admin_update_order_status(oid):
    order = db.session.get(Order, oid) or abort(404)
    new_status = request.form.get("status")
    if new_status in ["pending", "processing", "shipped", "delivered", "cancelled"]:
        order.status = new_status
        db.session.commit()
        flash(f"Order #{order.id} status changed to '{new_status}'.", "success")
    return redirect(url_for("admin"))


@app.route("/admin/product/<int:pid>/stock", methods=["POST"])
@login_required
@admin_required
def admin_restock_product(pid):
    p = db.session.get(Product, pid) or abort(404)
    added = int(request.form.get("add_stock", 10))
    p.stock += added
    db.session.commit()
    flash(f"Restocked '{p.name}' (+{added} units). Current stock: {p.stock}", "success")
    return redirect(url_for("admin"))


@app.route("/admin/product/<int:pid>/edit", methods=["POST"])
@login_required
@admin_required
def admin_edit_product(pid):
    p = db.session.get(Product, pid) or abort(404)
    p.name = request.form.get("name", p.name).strip()
    p.price = float(request.form.get("price", p.price))
    p.stock = int(request.form.get("stock", p.stock))
    p.image_url = request.form.get("image_url", p.image_url).strip()
    p.description = request.form.get("description", p.description).strip()
    cat_id = request.form.get("category_id")
    if cat_id:
        p.category_id = int(cat_id)
    db.session.commit()
    flash(f"Updated product '{p.name}' successfully.", "success")
    return redirect(url_for("admin"))


# ---------- ERROR HANDLERS ----------
@app.errorhandler(403)
def forbidden(e):
    return render_template("error.html", code=403, msg="Access denied"), 403


@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", code=404, msg="Page not found"), 404


# ---------- SEED ----------
def seed_data():
    if Category.query.count() > 0:
        return
    cats = [Category(name="Electronics", slug="electronics"),
            Category(name="Clothing", slug="clothing"),
            Category(name="Books", slug="books"),
            Category(name="Home", slug="home")]
    db.session.add_all(cats)
    db.session.flush()

    products = [
        Product(name="Wireless Headphones", price=89.99, stock=25,
                description="Premium noise-cancelling over-ear headphones.",
                image_url="https://picsum.photos/seed/headphones/600/400",
                category_id=cats[0].id),
        Product(name="Smart Watch", price=149.00, stock=15,
                description="Track fitness, heart rate, and notifications.",
                image_url="https://picsum.photos/seed/watch/600/400",
                category_id=cats[0].id),
        Product(name="Cotton T-Shirt", price=19.99, stock=100,
                description="Soft 100% organic cotton t-shirt.",
                image_url="https://picsum.photos/seed/tshirt/600/400",
                category_id=cats[1].id),
        Product(name="Denim Jacket", price=69.50, stock=30,
                description="Classic blue denim jacket, unisex.",
                image_url="https://picsum.photos/seed/jacket/600/400",
                category_id=cats[1].id),
        Product(name="Python Programming Book", price=39.99, stock=50,
                description="Complete guide to Python for beginners and pros.",
                image_url="https://picsum.photos/seed/pythonbook/600/400",
                category_id=cats[2].id),
        Product(name="The Art of Clean Code", price=29.99, stock=40,
                description="Best practices for maintainable code.",
                image_url="https://picsum.photos/seed/cleancode/600/400",
                category_id=cats[2].id),
        Product(name="Ceramic Mug Set", price=24.99, stock=60,
                description="Set of 4 handcrafted ceramic mugs.",
                image_url="https://picsum.photos/seed/mugs/600/400",
                category_id=cats[3].id),
        Product(name="Scented Candle", price=14.99, stock=80,
                description="Lavender soy wax candle, 40hr burn.",
                image_url="https://picsum.photos/seed/candle/600/400",
                category_id=cats[3].id),
    ]
    db.session.add_all(products)

    admin = User(email="admin@store.com", name="Admin", is_admin=True)
    admin.set_password("admin123")
    customer = User(email="user@store.com", name="Jane Doe")
    customer.set_password("user123")
    db.session.add_all([admin, customer])
    db.session.commit()
    print("✅ Seeded demo data. Admin: admin@store.com / admin123")


# Initialize database schema and initial seed data on startup (for both local and production WSGI)
with app.app_context():
    db.create_all()
    seed_data()


if __name__ == "__main__":
    app.run(debug=True, port=5000)
