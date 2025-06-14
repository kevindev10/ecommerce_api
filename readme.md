# Ecommerce API

A modern, full-featured FastAPI backend for an e-commerce platform.  
This project supports user registration with email confirmation, authentication, business and product management, file uploads, and more—all powered by SQLAlchemy and Pydantic.

---

## 🚀 Features

- **User Registration & Authentication**  
  Secure signup, login, and JWT-based authentication.

- **Email Confirmation**  
  Sends verification emails on registration.

- **Business Management**  
  Each user automatically gets a business profile.

- **Product CRUD**  
  Add, update, delete, and view products linked to businesses.

- **Image Uploads**  
  Upload profile and product images, with automatic resizing.

- **SQLAlchemy ORM**  
  Robust, production-ready database interactions.

- **Pydantic Validation**  
  Strong data validation and serialization.

- **Background Tasks**  
  Email sending handled asynchronously.

- **CORS Support**  
  Ready for frontend integration.

---

## 🏗️ Project Structure

```
ecommerce_api/
├── main.py
├── models.py
├── schemas.py
├── authentication.py
├── database.py
├── config.py
├── emails.py
├── static/
│   └── images/
├── templates/
│   └── verification.html
├── requirements.txt
└── .env
```

---

## ⚡ Getting Started

### Prerequisites

- Python 3.8+
- pip

### Installation

1. **Clone the repository**
    ```bash
    git clone https://github.com/kevindev10/ecommerce_api
    cd ecommerce_api
    ```

2. **Create and activate a virtual environment**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

3. **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4. **Set up your `.env` file**  
   Copy `.env.example` to `.env` and fill in your secrets and DB config.

5. **Run the app**
    ```bash
    uvicorn main:app --reload
    ```

6. **Visit the interactive docs**  
   [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🛠️ API Endpoints

- `POST /registration` — Register a new user (sends confirmation email)
- `GET /verification` — Verify email via token
- `POST /token` — Obtain JWT token (login)
- `POST /user/me` — Get current user profile
- `POST /uploadfile/profile` — Upload profile image
- `POST /uploadfile/product/{id}` — Upload product image
- `POST /products` — Add a new product
- `GET /products` — List all products
- `GET /products/{id}` — Get product details (with business info)
- `PUT /products/{id}` — Update a product
- `DELETE /products/{id}` — Delete a product
- `PUT /business/{id}` — Update business details

---

## 📝 Notes

- **Email sending** uses background tasks; configure your SMTP settings in `.env`.
- **Image uploads** are stored in `static/images/` and resized to 200x200 pixels.
- **Business auto-creation**: Each new user automatically gets a business profile.
- **JWT secret**: Set your `SECRET` in `.env` for secure token handling.

---

## 🧩 Extending & Refactoring

- The codebase is ready to be split into routers and CRUD modules for maintainability.
- You can easily add new features or endpoints as needed.
- For production, consider adding Alembic for migrations and more granular permissions.

---

## 📄 License

MIT

---

**Built with [FastAPI](https://fastapi.tiangolo.com/) and ❤️ by Kevin**