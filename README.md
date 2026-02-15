# Logistics Service API

A FastAPI-based logistics management system for managing products and orders with inventory tracking.

## Features

- **Product Management**: Create, retrieve, update, and list products with stock tracking
- **Order Management**: Create orders with automatic inventory deduction, status management, and filtering
- **Inventory Control**: Pessimistic locking to prevent overselling during concurrent order creation
- **Order Filtering**: Search orders by product name, status, and date range with pagination
- **Database Migrations**: Alembic for schema version control

## Technology Stack

- **Framework**: FastAPI 0.115.0
- **Database**: PostgreSQL 16
- **ORM**: SQLAlchemy 2.0.34
- **Migrations**: Alembic 1.13.2
- **Server**: Uvicorn
- **Testing**: Pytest, HTTPX

## Running the Application

### Prerequisites

- Docker and Docker Compose installed
- (Alternative) Python 3.11+ for local development

### Option 1: Docker (Recommended)

1. **Clone the repository and navigate to the project directory**:
   ```bash
   cd logistics-service
   ```

2. **Start the application**:
   ```bash
   docker-compose up --build
   ```

   This will:
   - Start PostgreSQL on port 5432
   - Run database migrations automatically
   - Start the API server on port 8000

3. **Access the API**:
   - API Base URL: `http://localhost:8000`
   - Interactive API Docs: `http://localhost:8000/docs`
   - Alternative Docs: `http://localhost:8000/redoc`

4. **Stop the application**:
   ```bash
   docker-compose down
   ```

   To also remove volumes (database data):
   ```bash
   docker-compose down -v
   ```

### Option 2: Local Development

1. **Create and activate a virtual environment**:
   ```bash
   python -m venv .venv
   .venv\Scripts\Activate.ps1    # Windows PowerShell
   # or
   source .venv/bin/activate      # Linux/Mac
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables** (create `.env` file):
   ```env
   DATABASE_URL=postgresql+psycopg2://postgres:Himosh1020@localhost:5432/logistics_db
   ```

4. **Ensure PostgreSQL is running**, then run migrations:
   ```bash
   alembic upgrade head
   ```

5. **Start the development server**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## API Endpoints

### Products

- `POST /products` - Create a new product
- `GET /products/{product_id}` - Get product by ID
- `GET /products` - List all products with pagination
- `PATCH /products/{product_id}` - Update product (name, price, stock)

### Orders

- `POST /orders` - Create a new order (deducts inventory)
- `GET /orders/{order_id}` - Get order by ID with items
- `GET /orders` - List all orders with pagination
- `GET /orders/search` - Search/filter orders by product name, status, and date range
- `PATCH /orders/{order_id}/status` - Update order status (Pending → Shipped/Cancelled)

### Status Transitions

- **Pending** → Shipped or Cancelled
- **Shipped** → (terminal state)
- **Cancelled** → (terminal state)

## Running Tests

### With Docker

```bash
# Run tests inside the API container
docker-compose exec api pytest

# Run with coverage
docker-compose exec api pytest --cov=app --cov-report=term-missing

# Run specific test file
docker-compose exec api pytest tests/test_orders.py -v
```

### Local Environment

```bash
# Ensure virtual environment is activated
pytest

# With coverage report
pytest --cov=app --cov-report=html

# Verbose output
pytest -v

# Run specific tests
pytest tests/test_orders.py::test_create_order -v
```

### Test Structure

Tests should be organized as:
```
tests/
├── __init__.py
├── conftest.py           # Shared fixtures (test DB, client)
├── test_products.py      # Product endpoint tests
├── test_orders.py        # Order endpoint tests
└── test_services.py      # Business logic tests
```

## Design Decisions & Trade-offs

### 1. Concurrency Handling

**Decision**: Used PostgreSQL row-level locking with `SELECT ... FOR UPDATE` in the order creation flow.

**Rationale**:
- Prevents race conditions when multiple users order the same product simultaneously
- Ensures inventory cannot go negative even under high concurrency
- Transactions automatically rollback on errors, maintaining data consistency

**Trade-off**: 
- Pessimistic locking can reduce throughput under extreme load (competing transactions wait)
- Alternative (optimistic locking with version numbers) would be faster but require retry logic
- For a logistics system, correctness (never oversell) is more critical than maximum throughput

### 2. Order Status Transitions

**Decision**: Implemented a state machine with `ALLOWED_TRANSITIONS` dictionary to enforce valid status changes.

**Rationale**:
- Prevents invalid transitions (e.g., Shipped → Pending)
- Makes business rules explicit and maintainable
- Centralized validation logic

**Trade-off**:
- More rigid than a fully flexible status system
- Adding new statuses requires code changes (not configuration)
- Acceptable for this scope; could be moved to database configuration for larger systems


### 3. Database Schema Decisions

**Decision**: Store `price_at_time_of_order` in order_item rather than calculating from current product price.

**Rationale**:
- Historical prices must be preserved for accounting/audit purposes
- Product prices change over time; orders should reflect price when purchased
- Essential for financial accuracy

**Trade-off**: 
- Slight data duplication, but necessary
- No alternative that maintains data integrity

## Project Structure

```
logistics-service/
├── alembic/                    # Database migrations
│   └── versions/
├── app/
│   ├── main.py                # FastAPI application entry point
│   ├── api/
│   │   ├── deps.py           # Dependency injection (database session)
│   │   └── routes/           # API endpoint handlers
│   ├── core/
│   │   └── config.py         # Configuration management
│   ├── db/
│   │   ├── base.py           # SQLAlchemy base
│   │   └── session.py        # Database session factory
│   ├── models/               # SQLAlchemy ORM models
│   ├── schemas/              # Pydantic request/response models
│   └── services/             # Business logic layer
├── scripts/
│   └── entrypoint.sh         # Docker container startup script
├── docker-compose.yml        # Docker orchestration
├── Dockerfile               # Container image definition
└── requirements.txt         # Python dependencies
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |

## Health Check

```bash
curl http://localhost:8000/health
# Response: {"status":"ok"}
```

## License

MIT
