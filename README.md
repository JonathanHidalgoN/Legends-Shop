# 🛒 Legends-Shop

**Legends-Shop** is a full-stack web application designed to simulate an e-commerce experience, built with a modern backend and frontend stack. The goal is to showcase cloud-native backend development skills, scalable architecture, and cost-effective deployment strategies.

## 🚀 Features

- **FastAPI** backend with full REST API support
- **PostgreSQL** database via Azure PostgreSQL Flexible Server
- **Dockerized** deployment for consistent local and cloud environments
- **Cloud-native integration** with:
  - Azure Blob Storage
  - Azure Key Vault
  - Azure web app
  - Azure VNET
  - Azure postgres flexible server
- **Logging and monitoring** using Prometheus, Loki, and Grafana
- **Frontend** powered by **Next.js (TypeScript)** and deployed on Vercel
- CI/CD-friendly architecture, designed for easy extension

## 📦 Tech Stack

| Layer     | Technologies |
|-----------|--------------|
| Backend   | FastAPI, SQLAlchemy, Alembic |
| Database  | PostgreSQL (via Neon in dev) |
| Frontend  | Next.js, TypeScript |
| DevOps    | Docker, GitHub Actions |
| Monitoring | Prometheus, Grafana, Loki |
| Auth      | OAuth2 / JWT |  

## 🧠 Purpose

This project is part of a long-term plan. It serves as a learning platform and demonstration of:

- Cost-efficient backend design with real-world practices
- Infrastructure observability and secure secret management

## 🐳 Getting Started

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Node.js (for frontend)

### Local Development

```bash
# Clone the repo
git clone https://github.com/JonathanHidalgoN/Legends-Shop.git
cd Legends-Shop

# Start services
docker-compose up --build
Visit:

http://localhost:8000 for API

http://localhost:3000 for frontend

☁️ Deployment
The app is designed to deploy on:

Azure for backend and cloud services

Vercel for frontend

Render/Neon for dev PostgreSQL when Azure is nott used
```
🛣️ Roadmap
🧱 Phase 1: Infrastructure & Setup
✅ Set up Docker Compose configuration for backend, frontend, and PostgreSQL.

✅ Implement League of Legends API data-fetching class to pull updated items.

✅ Integrate Alembic for database migrations.

✅ Implement database session management using async context managers.

✅ Move database table logic into modular, asynchronous functions.

✅ Standardize environment variables in .env and docker-compose.yml.

🔧 Phase 2: Backend API Foundations
✅ Implement item-related API endpoints.

✅ Add field validation (e.g., email format) using pydantic models.

✅ Establish layered architecture:
Request Validation → Business Logic Class → Atomic DB Functions.

✅ Add structured logging with standardized middleware for API calls.

✅ Use custom exceptions for clear and modular error handling.

✅ Implement security headers middleware.

✅ Add logging decorators with JSON structure.

✅ Add rate limiting using decorators and slowapi.

✅ Create random data seeding utility class.

🧪 Phase 3: Testing & Quality Assurance
✅ Add unit testing for backend business logic with mocking.

✅ Add unit testing for API endpoints.

✅ Add integration tests using SQLite as the test database.

✅ Create requirements.lock file for dependency management.

🔐 Phase 4: Authentication & Authorization
✅ Add OAuth2 + JWT token authentication.

✅ Implement Depends-based dependency injection for authorization logic.

✅ Implement profile feature (API + business logic).

🛍️ Phase 5: Core E-commerce Features
✅ Implement ordering logic following established backend architecture.

✅ Add delivery dates logic.

✅ Add location-based logic.

✅ Add review generation and fake user data on system init.

✅ Implement backend lifespan event that:

Detects previous system initialization

Updates item data

Loads items into DB

Generates locations, users, orders, and reviews

Marks initialization complete

🌐 Phase 6: Frontend Development (Next.js)
✅ Create a modular and styled base UI with a custom color palette.

✅ Design layout using Amazon as a visual reference.

✅ Build reusable components and pages:

Home / Items

Orders

Logic Debugging

Profile

Location

Delivery Dates

✅ Add React Context for static data (items, effects, tags).

✅ Mirror backend interfaces in frontend using TypeScript.

✅ Standardize API request functions using typed response interfaces.

✅ Create custom error pages (404, 500, etc.)

🧪 Phase 7: Deployment, CI/CD & Observability
✅ Deploy backend (Render), frontend (Vercel), and database (Neon).

✅ Add GitHub Actions workflows for backend and frontend CI.

✅ Add Grafana + Loki + Prometheus stack for monitoring and observability.

✅ Add HD image fetching and storage to /public directory.
