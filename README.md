# 🛍️ ShopEasy — Flask E-Commerce Store

A full-stack e-commerce web application built with **Flask**, **SQLite**, and vanilla **HTML/CSS/JS**.

## 📁 Project Structure

```
ecommerce_store/
├── app.py              # Main Flask application & routes
├── models.py           # SQLAlchemy database models
├── requirements.txt    # Python dependencies
├── templates/          # Jinja2 HTML templates
│   ├── base.html
│   ├── index.html
│   ├── product.html
│   ├── cart.html
│   ├── checkout.html
│   ├── login.html
│   ├── register.html
│   ├── orders.html
│   ├── order_detail.html
│   ├── admin.html
│   └── error.html
└── static/
    └── style.css       # Responsive CSS styles
```

## 🚀 Quick Start

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python app.py
```

Open **http://localhost:5000**

## 🔑 Demo Credentials

| Role     | Email              | Password  |
|----------|--------------------|-----------|
| Customer | `user@store.com`   | `user123` |
| Admin    | `admin@store.com`  | `admin123`|

## ✅ Features

- 🔐 **Authentication** — Register, login, hashed passwords (Werkzeug), session management
- 🛒 **Shopping Cart** — Add/update/remove items, real-time cart count, stock limits
- 📦 **Product Catalog** — Categories, search, product detail pages
- 💳 **Checkout** — Address validation, atomic stock decrement, order creation
- 📋 **Order History** — User order list and detail view
- 👨‍💼 **Admin Panel** — Add/delete products, view stats (revenue, users, orders)
- 🔒 **Security** — Admin role guard, ownership checks, CSRF-safe forms
- 📱 **Responsive UI** — Mobile-friendly grid layouts

## 🔧 Production Checklist

1. Set a strong `SECRET_KEY` in a `.env` file:
   ```
   SECRET_KEY=<random-64-char-string>
   ```
2. Switch to PostgreSQL/MySQL for production database
3. Use **Flask-Migrate** (Alembic) for schema migrations
4. Integrate a real payment gateway (e.g., **Stripe**)
5. Deploy with **Gunicorn + Nginx** or on **Render/Railway/Fly.io**
6. Add HTTPS, rate-limiting (`Flask-Limiter`), and CSRF protection (`Flask-WTF`)

## 🛠️ Built With

- [Flask](https://flask.palletsprojects.com/) — Web framework
- [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/) — ORM
- [Flask-Login](https://flask-login.readthedocs.io/) — Session management
- [SQLite](https://www.sqlite.org/) — Development database
- [Werkzeug](https://werkzeug.palletsprojects.com/) — Password hashing
