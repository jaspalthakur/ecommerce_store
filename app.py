import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
from models import db, User, Product, Category, CartItem, Order, OrderItem

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
def inject_cart_count():
    count = 0
    if current_user.is_authenticated:
        count = db.session.query(db.func.sum(CartItem.quantity)).filter_by(
            user_id=current_user.id
        ).scalar() or 0
    return {"cart_count": count}


# ---------- PUBLIC ROUTES ----------
@app.route("/")
def index():
    q = request.args.get("q", "").strip()
    cat_slug = request.args.get("category")
    query = Product.query
    if q:
        query = query.filter(Product.name.ilike(f"%{q}%"))
    if cat_slug:
        query = query.join(Category).filter(Category.slug == cat_slug)
    products = query.order_by(Product.created_at.desc()).all()
    categories = Category.query.all()
    return render_template("index.html", products=products, categories=categories,
                           q=q, active_cat=cat_slug)


@app.route("/product/<int:pid>")
def product_detail(pid):
    product = db.session.get(Product, pid) or abort(404)
    return render_template("product.html", product=product)


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


# ---------- CART ----------
@app.route("/cart")
@login_required
def cart():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(i.product.price * i.quantity for i in items)
    return render_template("cart.html", items=items, total=total)


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
    flash(f"Added {product.name} to cart.", "success")
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
    else:
        item.quantity = min(qty, item.product.stock)
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


# ---------- CHECKOUT ----------
@app.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not items:
        flash("Your cart is empty.", "warning")
        return redirect(url_for("index"))
    total = sum(i.product.price * i.quantity for i in items)

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

        order = Order(user_id=current_user.id, total=total, shipping_address=address)
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

        db.session.commit()
        flash(f"Order #{order.id} placed! (Demo mode — no real payment charged)", "success")
        return redirect(url_for("order_detail", oid=order.id))

    return render_template("checkout.html", items=items, total=total)


# ---------- ORDERS ----------
@app.route("/orders")
@login_required
def orders():
    my_orders = Order.query.filter_by(user_id=current_user.id)\
        .order_by(Order.created_at.desc()).all()
    return render_template("orders.html", orders=my_orders)


@app.route("/orders/<int:oid>")
@login_required
def order_detail(oid):
    order = db.session.get(Order, oid) or abort(404)
    if order.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    return render_template("order_detail.html", order=order)


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


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        seed_data()
    app.run(debug=True, port=5000)
