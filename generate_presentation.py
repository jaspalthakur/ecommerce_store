import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Color Palette
    C_NAVY = RGBColor(15, 23, 42)      # #0F172A
    C_INDIGO = RGBColor(79, 70, 229)   # #4F46E5
    C_LIGHT_BG = RGBColor(248, 250, 252) # #F8FAFC
    C_WHITE = RGBColor(255, 255, 255)
    C_GOLD = RGBColor(245, 158, 11)    # #F59E0B
    C_TEXT = RGBColor(30, 41, 59)      # #1E293B
    C_MUTED = RGBColor(100, 116, 139)  # #64748B
    C_CARD_BG = RGBColor(255, 255, 255)
    C_CARD_BORDER = RGBColor(226, 232, 240)
    C_EMERALD = RGBColor(16, 185, 129)

    def set_bg(slide, color):
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = color

    def add_header(slide, title_text, category_text="SHOPEASY PLATFORM OVERVIEW"):
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.5), Inches(0.35))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.size = Pt(11)
        p_cat.font.bold = True
        p_cat.font.color.rgb = C_INDIGO

        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.8), Inches(11.5), Inches(0.7))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(24)
        p_title.font.bold = True
        p_title.font.color.rgb = C_NAVY

    def create_card(slide, left, top, width, height, title, points, accent_color=C_INDIGO):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = C_WHITE
        shape.line.color.rgb = C_CARD_BORDER
        shape.line.width = Pt(1.5)

        # Header accent bar
        bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, Inches(0.08))
        bar.fill.solid()
        bar.fill.fore_color.rgb = accent_color
        bar.line.fill.background()

        tb = slide.shapes.add_textbox(left + Inches(0.25), top + Inches(0.18), width - Inches(0.5), height - Inches(0.3))
        tf = tb.text_frame
        tf.word_wrap = True

        p_head = tf.paragraphs[0]
        p_head.text = title
        p_head.font.size = Pt(15)
        p_head.font.bold = True
        p_head.font.color.rgb = C_NAVY
        p_head.space_after = Pt(10)

        for pt in points:
            p = tf.add_paragraph()
            p.text = "• " + pt
            p.font.size = Pt(11.5)
            p.font.color.rgb = C_TEXT
            p.space_after = Pt(6)

    # ==========================================
    # SLIDE 1: Title Slide
    # ==========================================
    s1 = prs.slides.add_slide(blank_layout)
    set_bg(s1, C_NAVY)

    # Decorative banner box
    decor = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.2), Inches(3.2), Inches(0.45))
    decor.fill.solid()
    decor.fill.fore_color.rgb = C_INDIGO
    decor.line.fill.background()
    tf_dec = decor.text_frame
    p_dec = tf_dec.paragraphs[0]
    p_dec.text = "✨ ENTERPRISE PROJECT REPORT"
    p_dec.font.size = Pt(11)
    p_dec.font.bold = True
    p_dec.font.color.rgb = C_WHITE
    p_dec.alignment = PP_ALIGN.CENTER

    tb_t = s1.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11), Inches(2.2))
    tf_t = tb_t.text_frame
    tf_t.word_wrap = True
    p_main = tf_t.paragraphs[0]
    p_main.text = "ShopEasy E-Commerce"
    p_main.font.size = Pt(46)
    p_main.font.bold = True
    p_main.font.color.rgb = C_WHITE

    p_sub = tf_t.add_paragraph()
    p_sub.text = "Full-Stack Web Application Architecture, Implementation & Deployment"
    p_sub.font.size = Pt(20)
    p_sub.font.color.rgb = C_GOLD
    p_sub.space_before = Pt(8)

    p_desc = tf_t.add_paragraph()
    p_desc.text = "A production-grade retail platform featuring real-time inventory, intelligent checkout,\nverified reviews, custom invoicing, role-based security, and 24/7 cloud availability."
    p_desc.font.size = Pt(13)
    p_desc.font.color.rgb = RGBColor(203, 213, 225)
    p_desc.space_before = Pt(14)

    # Highlights Footer Bar
    stats_data = [
        ("Stack", "Flask 3 + SQLite + SQLAlchemy"),
        ("Features", "Wishlist, Reviews, Dynamic Coupons"),
        ("Design", "Dark/Light Modes + Responsive CSS"),
        ("Live Deployment", "Render WSGI + Cloudflare Tunnel")
    ]
    stat_w = Inches(2.7)
    for i, (label, val) in enumerate(stats_data):
        st_box = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8) + i * Inches(2.95), Inches(5.6), Inches(2.75), Inches(1.2))
        st_box.fill.solid()
        st_box.fill.fore_color.rgb = RGBColor(30, 41, 59)
        st_box.line.color.rgb = RGBColor(51, 65, 85)
        st_tf = st_box.text_frame
        st_tf.word_wrap = True
        p_lbl = st_tf.paragraphs[0]
        p_lbl.text = label.upper()
        p_lbl.font.size = Pt(10)
        p_lbl.font.bold = True
        p_lbl.font.color.rgb = C_GOLD
        p_val = st_tf.add_paragraph()
        p_val.text = val
        p_val.font.size = Pt(12)
        p_val.font.bold = True
        p_val.font.color.rgb = C_WHITE
        p_val.space_before = Pt(4)

    # ==========================================
    # SLIDE 2: Executive Summary & Problem Solution
    # ==========================================
    s2 = prs.slides.add_slide(blank_layout)
    set_bg(s2, C_LIGHT_BG)
    add_header(s2, "Executive Summary & Core Objectives", "Strategic Context")

    create_card(s2, Inches(0.8), Inches(1.7), Inches(3.6), Inches(5.2),
        "Market Challenges", [
            "Traditional e-commerce templates are often bloated with heavy third-party dependencies.",
            "High shopping cart abandonment rates caused by friction during checkout & authentication.",
            "Lack of responsive dark mode, live search, and verified customer review transparency.",
            "Complex deployment workflows requiring expensive database and hosting configurations."
        ], C_GOLD)

    create_card(s2, Inches(4.7), Inches(1.7), Inches(3.6), Inches(5.2),
        "The ShopEasy Solution", [
            "Lightweight, clean monolithic architecture powered by Python Flask 3.0 & SQLAlchemy ORM.",
            "Atomic stock-management preventing overselling with immediate inventory synchronization.",
            "Smart promotions engine supporting promo coupons (WELCOME10, SAVE20) and free delivery tier.",
            "One-click demo onboarding with pre-seeded Customer & Administrator credentials."
        ], C_INDIGO)

    create_card(s2, Inches(8.6), Inches(1.7), Inches(3.6), Inches(5.2),
        "Business Impact & Metrics", [
            "100% Mobile & Desktop Responsive via custom CSS design system (Plus Jakarta Sans).",
            "Zero client-side build pipeline required; lightning fast first contentful paint (<300ms).",
            "Complete order lifecycle management: Pending -> Processing -> Shipped -> Delivered.",
            "Integrated printable official tax invoices with instant window.print() support."
        ], C_EMERALD)

    # ==========================================
    # SLIDE 3: System Architecture & Tech Stack
    # ==========================================
    s3 = prs.slides.add_slide(blank_layout)
    set_bg(s3, C_LIGHT_BG)
    add_header(s3, "System Architecture & Technology Stack", "Technical Foundation")

    create_card(s3, Inches(0.8), Inches(1.7), Inches(2.7), Inches(5.2),
        "Backend Core", [
            "Flask 3.0.0: Microframework handling routing, sessions, context processors.",
            "Flask-Login 0.6.3: User session state & access control guards.",
            "Werkzeug 3.0.1: Secure scrypt/PBKDF2 password hashing.",
            "Gunicorn 22.0.0: High-performance WSGI production server."
        ], C_INDIGO)

    create_card(s3, Inches(3.75), Inches(1.7), Inches(2.7), Inches(5.2),
        "Database Layer", [
            "Flask-SQLAlchemy 3.1.1: High-level Python ORM abstraction.",
            "SQLite 3: Zero-configuration ACID development database.",
            "Relational Models: Users, Products, Categories, Cart, Orders, Wishlist, Reviews.",
            "Cascade delete & constraint integrity across items."
        ], C_EMERALD)

    create_card(s3, Inches(6.7), Inches(1.7), Inches(2.7), Inches(5.2),
        "Frontend & UI/UX", [
            "Jinja2: Server-side component templating with base inheritance.",
            "Custom CSS3: Tokens, flexbox, CSS grids & CSS variables.",
            "Dark/Light Theme: Real-time switcher with localStorage state.",
            "Vanilla JS: Debounced live search, modal views & toast dismiss."
        ], C_GOLD)

    create_card(s3, Inches(9.65), Inches(1.7), Inches(2.7), Inches(5.2),
        "Infrastructure", [
            "Render Cloud: Production containerized deployment pipeline.",
            "Procfile: Explicit WSGI entry point binding.",
            "Cloudflare Tunnel: Real-time public HTTPS tunnel.",
            "Git & GitHub: Distributed version control with master CI."
        ], C_NAVY)

    # ==========================================
    # SLIDE 4: Customer Experience & Interactive Features
    # ==========================================
    s4 = prs.slides.add_slide(blank_layout)
    set_bg(s4, C_LIGHT_BG)
    add_header(s4, "Customer Journey & Modern Shopping UX", "Frontend Experience")

    create_card(s4, Inches(0.8), Inches(1.7), Inches(3.6), Inches(5.2),
        "Discovery & Search", [
            "Live Search API (/api/search): Debounced instant dropdown preview with thumbnail & price.",
            "Categorized catalog: Filter by Electronics, Apparel, Books, and Home.",
            "Sorting controls: Price Ascending/Descending, Newest, Name A-Z.",
            "Storefront filters: Max Price threshold and In-Stock Only toggle."
        ], C_INDIGO)

    create_card(s4, Inches(4.7), Inches(1.7), Inches(3.6), Inches(5.2),
        "Interaction & Wishlist", [
            "Quick View Modal: Instant product inspection without navigating away from the page.",
            "Wishlist Toggle: Save favorite products with persistent heart button indicators.",
            "Multi-Angle Gallery: High-resolution angle switching (Front, Profile, Lifestyle, Detail).",
            "Auto-dismissing Toast Notifications for immediate feedback on cart actions."
        ], C_GOLD)

    create_card(s4, Inches(8.6), Inches(1.7), Inches(3.6), Inches(5.2),
        "Trust & Transparency", [
            "Verified Customer Reviews: 1 to 5 star rating picker with verified buyer badge.",
            "Dynamic rating aggregation calculating real-time averages.",
            "Prominent warranty & guarantee badges (30-day money back, 1-year warranty).",
            "Customer Profile center (/profile) with address book pre-fill."
        ], C_EMERALD)

    # ==========================================
    # SLIDE 5: Cart, Checkout & Pricing Engine
    # ==========================================
    s5 = prs.slides.add_slide(blank_layout)
    set_bg(s5, C_LIGHT_BG)
    add_header(s5, "Shopping Cart, Promo Engine & Checkout", "Transaction Flow")

    create_card(s5, Inches(0.8), Inches(1.7), Inches(5.6), Inches(5.2),
        "Intelligent Cart & Promotions Engine", [
            "Session-backed discount codes engine supporting percentage and free shipping vouchers:",
            "  • WELCOME10 -> 10% discount on order subtotal",
            "  • SAVE20 -> 20% discount for special promotional events",
            "  • FREESHIP -> Automatic waiver of standard shipping charges",
            "Dynamic Free Shipping Progress Bar: Real-time visual progress tracker toward the $50 free shipping goal.",
            "Quantity adjustments with atomic stock ceiling guards preventing over-ordering.",
            "One-click 'Move to Cart' from Wishlist for rapid conversion."
        ], C_INDIGO)

    create_card(s5, Inches(6.8), Inches(1.7), Inches(5.6), Inches(5.2),
        "Streamlined Checkout & Order Processing", [
            "Two-column structured checkout with live order summary and itemized thumbnail review.",
            "Pre-populated shipping address: Seamlessly loaded from user's saved account profile.",
            "Interactive payment selector: Credit Card (with realistic field simulation), PayPal, and Cash on Delivery.",
            "Atomic transaction processing in SQLAlchemy:",
            "  1. Validation of customer shipping details.",
            "  2. Verification of live stock availability.",
            "  3. Atomic order creation & inventory decrement.",
            "  4. Immediate redirect to live visual order tracking."
        ], C_EMERALD)

    # ==========================================
    # SLIDE 6: Order Fulfillment & Invoicing
    # ==========================================
    s6 = prs.slides.add_slide(blank_layout)
    set_bg(s6, C_LIGHT_BG)
    add_header(s6, "Order Tracking & Official Tax Invoicing", "Post-Purchase Experience")

    create_card(s6, Inches(0.8), Inches(1.7), Inches(5.6), Inches(5.2),
        "Visual 4-Stage Fulfillment Tracker", [
            "Interactive milestone tracker on order detail page (/orders/<id>):",
            "  • Stage 1: Order Placed & Confirmed",
            "  • Stage 2: Processing & Packing in Warehouse",
            "  • Stage 3: Dispatched & In-Transit (Shipped)",
            "  • Stage 4: Delivered to Customer",
            "Order History filtering tabs: Filter purchases by status (Pending, Processing, Shipped, Delivered).",
            "Detailed recipient breakdown including customer contact, shipping address, and itemized receipt."
        ], C_GOLD)

    create_card(s6, Inches(6.8), Inches(1.7), Inches(5.6), Inches(5.2),
        "Official Printable Tax Invoice (/orders/<id>/invoice)", [
            "Dedicated, professional print-optimized invoice layout for corporate and retail customers.",
            "Features included:",
            "  • Company brand header & unique invoice number (#INV-0000X)",
            "  • Billed to & Shipped to address verification",
            "  • Itemized product description, unit cost, quantities, and totals",
            "  • Subtotal, shipping, discounts, and total paid",
            "Print-optimized CSS (@media print): Automatically strips navigation, buttons, and backgrounds for clean PDF/paper printing."
        ], C_NAVY)

    # ==========================================
    # SLIDE 7: Admin Command Center
    # ==========================================
    s7 = prs.slides.add_slide(blank_layout)
    set_bg(s7, C_LIGHT_BG)
    add_header(s7, "Admin Command Center & Operations", "Store Administration")

    create_card(s7, Inches(0.8), Inches(1.7), Inches(3.6), Inches(5.2),
        "Store Analytics KPIs", [
            "Real-time business performance dashboard cards:",
            "  • Total Revenue ($ USD) from fulfilled & active orders.",
            "  • Order Count tracking total completed checkouts.",
            "  • Active Products across all catalog categories.",
            "  • Registered Users database count.",
            "Gated security with @admin_required decorator preventing unauthorized access."
        ], C_INDIGO)

    create_card(s7, Inches(4.7), Inches(1.7), Inches(3.6), Inches(5.2),
        "Inventory Management", [
            "Real-time inventory table displaying ID, Category, Price, and Stock units.",
            "One-Click Quick Restock: Instant '+15 Stock' pill button to replenish inventory immediately.",
            "Add Product form: Instant creation of new products with name, price, stock, category, and image URL.",
            "Cascading delete protection removing cart items associated with deleted products."
        ], C_GOLD)

    create_card(s7, Inches(8.6), Inches(1.7), Inches(3.6), Inches(5.2),
        "Fulfillment Workflow", [
            "Recent Orders audit log displaying Customer Name, Email, Total, and Timestamp.",
            "Inline Status Dropdown: Admin can update order fulfillment states in real-time:",
            "  Pending -> Processing -> Shipped -> Delivered -> Cancelled.",
            "Direct link to full order details and customer shipping records."
        ], C_EMERALD)

    # ==========================================
    # SLIDE 8: Database Architecture & Security
    # ==========================================
    s8 = prs.slides.add_slide(blank_layout)
    set_bg(s8, C_LIGHT_BG)
    add_header(s8, "Database Schema & Security Framework", "Data Integrity")

    create_card(s8, Inches(0.8), Inches(1.7), Inches(5.6), Inches(5.2),
        "Relational Schema Design", [
            "User: id, email (unique), name, password_hash, is_admin, default_address, phone, created_at.",
            "Category: id, name, slug (unique) with relationship to Products.",
            "Product: id, name, price, stock, description, image_url, category_id.",
            "CartItem: id, user_id, product_id, quantity with UniqueConstraint(user_id, product_id).",
            "Order & OrderItem: id, user_id, total, status, shipping_address, item snapshot records.",
            "WishlistItem: id, user_id, product_id with UniqueConstraint(user_id, product_id).",
            "Review: id, user_id, product_id, rating (1-5), comment, created_at."
        ], C_INDIGO)

    create_card(s8, Inches(6.8), Inches(1.7), Inches(5.6), Inches(5.2),
        "Security & Integrity Controls", [
            "Authentication Security: Passwords salted and hashed with Werkzeug scrypt/PBKDF2.",
            "Role-Based Access Control (RBAC): Admin views guarded by @admin_required wrapper.",
            "Ownership Authorization: Customer cart, order, and profile routes strictly verify current_user.id.",
            "Input Sanitation: Type checking, minimum address length, and email format validation.",
            "Database Concurrency: Stock checked and decremented atomically inside database commit block."
        ], C_NAVY)

    # ==========================================
    # SLIDE 9: Deployment & DevOps Architecture
    # ==========================================
    s9 = prs.slides.add_slide(blank_layout)
    set_bg(s9, C_LIGHT_BG)
    add_header(s9, "Deployment Pipeline & High Availability", "DevOps & Cloud")

    create_card(s9, Inches(0.8), Inches(1.7), Inches(3.6), Inches(5.2),
        "Local Development", [
            "Python virtual environment (venv) with strict version pinning.",
            "SQLite file-based database for zero-config local testing.",
            "Environment configuration through python-dotenv (.env).",
            "Instant hot-reloading development server on port 5000."
        ], C_GOLD)

    create_card(s9, Inches(4.7), Inches(1.7), Inches(3.6), Inches(5.2),
        "Render Production Cloud", [
            "Automatic CI/CD deployment triggered upon git push to master branch.",
            "Gunicorn WSGI production server executing 'gunicorn app:app'.",
            "Automatic database & seed initialization on startup hook.",
            "Free SSL certificate & custom domain routing."
        ], C_INDIGO)

    create_card(s9, Inches(8.6), Inches(1.7), Inches(3.6), Inches(5.2),
        "Cloudflare Edge Tunnel", [
            "Zero-trust reverse proxy tunneling local server to edge network.",
            "Globally accessible HTTPS public URL for cross-device mobile testing.",
            "QUIC protocol transport with DNS pre-checks.",
            "Protection against DDoS attacks and origin exposure."
        ], C_EMERALD)

    # ==========================================
    # SLIDE 10: Conclusion & Future Roadmap
    # ==========================================
    s10 = prs.slides.add_slide(blank_layout)
    set_bg(s10, C_NAVY)

    tb_end = s10.shapes.add_textbox(Inches(0.8), Inches(1.0), Inches(11.5), Inches(1.2))
    tf_end = tb_end.text_frame
    p_e1 = tf_end.paragraphs[0]
    p_e1.text = "Project Summary & Future Roadmap"
    p_e1.font.size = Pt(36)
    p_e1.font.bold = True
    p_e1.font.color.rgb = C_WHITE

    p_e2 = tf_end.add_paragraph()
    p_e2.text = "ShopEasy delivers an elegant, fast, and feature-rich commerce foundation ready for enterprise scaling."
    p_e2.font.size = Pt(16)
    p_e2.font.color.rgb = C_GOLD
    p_e2.space_before = Pt(6)

    # 3 Summary Boxes
    boxes = [
        ("Key Accomplishments", [
            "Built full customer journey from search to checkout.",
            "Modern UI with Dark Mode, Wishlist, and Reviews.",
            "Comprehensive Admin Command Center with fulfillment control.",
            "Successfully deployed to Render & Cloudflare edge."
        ], C_INDIGO),
        ("Engineering Excellence", [
            "Modular SQLAlchemy ORM with clean separation of concerns.",
            "Zero-build frontend with high performance and accessibility.",
            "Atomic order placement and inventory integrity.",
            "Automated database seeding and WSGI production readiness."
        ], C_EMERALD),
        ("Future Roadmap", [
            "Stripe / Razorpay live payment gateway integration.",
            "PostgreSQL migration for high-concurrency scaling.",
            "Email notification dispatch via SendGrid/SES.",
            "Mobile App API via Flask-RESTful / GraphQL endpoints."
        ], C_GOLD)
    ]

    for i, (b_title, b_pts, b_col) in enumerate(boxes):
        b_shape = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8) + i * Inches(3.9), Inches(2.6), Inches(3.7), Inches(4.2))
        b_shape.fill.solid()
        b_shape.fill.fore_color.rgb = RGBColor(30, 41, 59)
        b_shape.line.color.rgb = b_col
        b_shape.line.width = Pt(1.5)

        tb = s10.shapes.add_textbox(Inches(1.0) + i * Inches(3.9), Inches(2.8), Inches(3.3), Inches(3.8))
        tf = tb.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = b_title
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = C_WHITE
        p.space_after = Pt(10)

        for pt in b_pts:
            p_pt = tf.add_paragraph()
            p_pt.text = "• " + pt
            p_pt.font.size = Pt(12)
            p_pt.font.color.rgb = RGBColor(226, 232, 240)
            p_pt.space_after = Pt(6)

    output_path = "ShopEasy_Project_Presentation.pptx"
    prs.save(output_path)
    print(f"✅ Generated PowerPoint deck successfully: {output_path}")

if __name__ == "__main__":
    create_deck()
