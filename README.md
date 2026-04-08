# E-Commerce Platform

Multi-vendor marketplace with buyer, seller, and admin portals.

## Tech Stack

Python FastAPI + SQLAlchemy + PostgreSQL + React + Redis + MinIO + Celery

## Features

- **Multi-vendor marketplace**
- **Buyer portal**:  browse, cart, checkout, orders, reviews
- **Seller portal**:  product management, orders, analytics
- **Admin portal**:  users, categories, commissions, payouts
- **Product variants (size, color)**
- **Inventory management with warehouse support**
- **Coupon system**
- **Payment integration**
- **Order tracking with shipments**
- **Search with filters**
- **Review system with helpful votes**

## Setup

### Using Docker (Recommended)

```bash
docker-compose up
```

### Manual Setup

**Backend:**
```bash
cd backend
pip install -r requirements.txt
# Set environment variables (copy .env.example to .env)
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Seed Data:**
```bash
cd backend
python -m scripts.seed_admin
python -m scripts.seed_sample_data
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

| Variable | Description | Default |
|----------|-------------|---------|
| MONGODB_URI / DATABASE_URL | Database connection string | localhost |
| JWT_SECRET | Secret key for JWT tokens | (required) |
| CORS_ORIGINS | Allowed frontend origins | http://localhost:3000 |
| SMTP_HOST | SMTP server for emails | (optional) |
| SMTP_PORT | SMTP port | 587 |
| SMTP_USER | SMTP username | (optional) |
| SMTP_PASS | SMTP password | (optional) |

## Default Login

- **Admin:** admin@ecommerce.local / admin123

## License

MIT License — Copyright (c) 2026 Humanoid Maker (www.humanoidmaker.com)
