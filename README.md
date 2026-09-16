# AI-Powered Vehicle Service Centre Knowledge and Booking Assistant

An AI-powered vehicle service centre management and knowledge assistant built with **FastAPI, PostgreSQL, SQLAlchemy, pgvector, RAG, Sentence Transformers, Groq, JWT authentication, WebSockets, and HTML/CSS/JavaScript**.

The system combines traditional vehicle-service management with an AI knowledge assistant. Customers can manage their vehicles, book services, view service history, and ask questions. Staff and administrators can manage bookings, technicians, job cards, and approved knowledge documents. The AI assistant retrieves information from approved service documents and can optionally use an LLM to generate natural-language answers.

---

## 1. Project Title

**AI-Powered Vehicle Service Centre Knowledge and Booking Assistant**

---

## 2. Problem Statement

Traditional vehicle service centres often depend on manual record keeping, staff knowledge, paper-based job cards, and disconnected customer communication.

This creates several problems:

* Customers cannot easily access their vehicle service information.
* Service bookings may be difficult to manage.
* Technicians need to manually search service information.
* Service history may not be easily accessible.
* Knowledge stored in manuals and documents is difficult to search.
* Customers may receive inconsistent answers to common service questions.
* Sensitive customer and vehicle information requires proper authorization.
* Dangerous vehicle problems require safety-aware responses rather than unrestricted repair instructions.

This project provides a centralized service-management platform with an AI-powered knowledge assistant.

---

## 3. Objectives

The main objectives are:

1. Provide secure user authentication.
2. Implement role-based access control.
3. Manage customers and their vehicles.
4. Manage service types and technicians.
5. Provide vehicle service booking.
6. Manage technician job cards.
7. Maintain vehicle service history.
8. Upload and process approved knowledge documents.
9. Split documents into searchable chunks.
10. Generate embeddings using a CPU-compatible model.
11. Store embeddings using PostgreSQL and pgvector.
12. Implement Retrieval-Augmented Generation (RAG).
13. Prevent the AI from fabricating unsupported service information.
14. Detect potentially dangerous vehicle situations.
15. Support Groq-based LLM responses.
16. Provide retrieval-only fallback mode.
17. Provide REST APIs.
18. Provide WebSocket-based chat.
19. Provide a browser-based chat interface.
20. Provide automated testing.

---

# 4. Features

## Authentication

* User registration
* Password hashing
* Login
* JWT access tokens
* Current-user validation
* Protected endpoints
* Active/inactive user checking

## Role-Based Access Control

Supported roles include:

* `CUSTOMER`
* `STAFF`
* `ADMIN`

Access to sensitive operations is restricted according to the user's role.

## Customer Management

* Customer profile management
* Phone number
* Address
* User ownership relationship

## Vehicle Management

* Vehicle registration number
* Make
* Model
* Year
* Additional vehicle details
* Customer ownership validation

## Service Management

* Service types
* Service descriptions
* Base prices
* Service duration

## Booking Management

* Vehicle service bookings
* Scheduled service date/time
* Booking status
* Ownership checks
* Workflow validation

## Technician Management

* Technician account
* Specialities
* Active/inactive status

## Job Cards

* Technician assignment
* Inspection notes
* Estimates
* Work status
* Completion information

## Service History

Customers can view service history for vehicles they own.

A customer cannot access another customer's vehicle history.

## AI Knowledge Assistant

* PDF support
* DOCX support
* TXT support
* Markdown support
* Document extraction
* Configurable chunking
* Embeddings
* PostgreSQL vector storage
* Similarity search
* RAG
* Source references

## Safety Guard

The assistant detects potentially dangerous situations such as:

* Brake failure
* Steering failure
* Tyre/tire failure
* Fuel leakage
* Electrical fire
* Smoke
* Severe overheating
* Dangerous fluid leakage

For potentially dangerous situations, the assistant provides a safety-oriented response instead of step-by-step repair instructions.

## LLM Support

* Groq provider
* Configurable LLM model
* Retrieval-only fallback
* Environment-based API configuration

## Chat

* REST chat API
* Chat sessions
* Chat history
* WebSocket chat
* Browser interface
* Retrieved source display

---

# 5. User Roles

| Role     | Main Responsibilities                                          |
| -------- | -------------------------------------------------------------- |
| CUSTOMER | Manage own profile, vehicles, bookings and service history     |
| STAFF    | Manage operational service-centre activities                   |
| ADMIN    | Manage administrative functions, users and knowledge documents |

Authorization is enforced on the backend.

The frontend does not determine whether a user is authorized.

---

# 6. System Architecture

The project follows a layered architecture.

```text
                    ┌──────────────────────────┐
                    │       Browser UI         │
                    │    HTML/CSS/JavaScript   │
                    └────────────┬─────────────┘
                                 │
                         REST / WebSocket
                                 │
                    ┌────────────▼─────────────┐
                    │        FastAPI            │
                    │       API Layer            │
                    └────────────┬─────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
       ┌──────▼──────┐    ┌─────▼─────┐    ┌──────▼──────┐
       │ Authentication│    │ Services  │    │   Chat/RAG  │
       │ JWT / RBAC   │    │ CRUD/Logic│    │   Pipeline   │
       └──────────────┘    └───────────┘    └──────┬───────┘
                                                    │
                                      ┌─────────────┼─────────────┐
                                      │             │             │
                               ┌──────▼──────┐ ┌────▼─────┐ ┌────▼─────┐
                               │  PostgreSQL │ │ pgvector │ │   Groq   │
                               │   Database  │ │ Retrieval│ │   LLM    │
                               └─────────────┘ └──────────┘ └──────────┘
```

### AI/RAG Flow

```text
User Question
      │
      ▼
Safety Guard
      │
      ├── Dangerous → Safety Response
      │
      ▼
Question Classification
      │
      ▼
Embedding Generation
      │
      ▼
pgvector Similarity Search
      │
      ▼
Approved Knowledge Chunks
      │
      ▼
Prompt Builder
      │
      ├── Groq LLM
      │
      └── Retrieval-only fallback
      │
      ▼
Answer + Sources
```

---

# 7. Technology Stack

| Technology            | Purpose                       |
| --------------------- | ----------------------------- |
| Python                | Backend programming           |
| FastAPI               | REST API and WebSocket server |
| Pydantic              | Request/response validation   |
| Pydantic Settings     | Environment configuration     |
| SQLAlchemy            | ORM/database access           |
| PostgreSQL            | Primary database              |
| psycopg               | PostgreSQL driver             |
| pgvector              | Vector similarity search      |
| Alembic               | Database migrations           |
| JWT                   | Authentication tokens         |
| pwdlib                | Password hashing              |
| Sentence Transformers | Embedding generation          |
| Groq                  | Optional LLM provider         |
| HTML                  | Browser interface             |
| CSS                   | Browser styling               |
| JavaScript            | Frontend interaction          |
| Pytest                | Automated testing             |
| Git/GitHub            | Version control               |

---

# 8. Folder Structure

```text
vehicle-service-ai-assistant/
│
├── README.md
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
│
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── *.py
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── endpoints/
│   │           ├── auth.py
│   │           ├── customers.py
│   │           ├── vehicles.py
│   │           ├── service_types.py
│   │           ├── technicians.py
│   │           ├── bookings.py
│   │           ├── job_cards.py
│   │           ├── documents.py
│   │           └── chat.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── logging.py
│   │   ├── security.py
│   │   └── deps.py
│   │
│   ├── db/
│   │   ├── base.py
│   │   ├── session.py
│   │   └── models/
│   │
│   ├── schemas/
│   ├── crud/
│   ├── services/
│   ├── llm/
│   ├── websocket/
│   └── static/
│       ├── chat.html
│       ├── chat.js
│       └── styles.css
│
├── data/
│   ├── knowledge_base/
│   ├── storage/
│   └── vector_index/
│
├── scripts/
│   ├── create_admin.py
│   ├── seed_data.py
│   ├── check_local_setup.py
│   └── ingest_knowledge_base.py
│
└── tests/
    ├── test_auth.py
    ├── test_bookings.py
    ├── test_chat.py
    ├── test_customers.py
    ├── test_documents.py
    ├── test_job_cards.py
    ├── test_rag.py
    ├── test_safety.py
    ├── test_service_history.py
    ├── test_vehicle_safety_guard.py
    └── test_vehicles.py
```

---

# 9. Database Design

The application uses **PostgreSQL** as its primary relational database.

Main entities:

```text
User
 │
 ├── Customer
 │      │
 │      └── Vehicle
 │              │
 │              └── ServiceBooking
 │                       │
 │                       └── JobCard
 │
 └── Technician
```

Knowledge system:

```text
KnowledgeDocument
       │
       └── KnowledgeChunk
                │
                └── Embedding / Vector
```

Chat system:

```text
ChatSession
     │
     └── ChatMessage
```

Main tables:

* `users`
* `customers`
* `vehicles`
* `service_types`
* `technicians`
* `service_bookings`
* `job_cards`
* `knowledge_documents`
* `knowledge_chunks`
* `chat_sessions`
* `chat_messages`
* `alembic_version`

JSONB is used where flexible structured information is required, such as vehicle details, customer address, technician specialities, estimates and document metadata.

---

# 10. Authentication

Authentication is implemented using:

1. Password hashing
2. Login verification
3. JWT access tokens
4. Protected API dependencies
5. Active-user validation

Passwords are never stored in plaintext.

Only password hashes are stored in the database.

---

# 11. JWT

After successful login, the server generates a JWT access token.

The token contains authentication information required by the application.

Protected requests use:

```text
Authorization: Bearer <access_token>
```

The JWT secret is loaded from an environment variable.

Secrets are not hard-coded in the source code.

---

# 12. RBAC

Role-Based Access Control determines which users can perform specific operations.

Example:

```text
CUSTOMER
   │
   ├── Own profile
   ├── Own vehicles
   ├── Own bookings
   └── Own service history

STAFF
   │
   ├── Service operations
   ├── Bookings
   ├── Technicians
   └── Job cards

ADMIN
   │
   ├── Administrative operations
   └── Knowledge/document management
```

Backend authorization is mandatory even when the browser UI hides certain options.

---

# 13. Customer Ownership

Customer data is protected using ownership checks.

For example:

```text
Customer A
   └── Vehicle A

Customer B
   └── Vehicle B
```

Customer A cannot request Customer B's:

* Vehicle details
* Service history
* Unauthorized bookings
* Other protected resources

The service-history endpoint verifies ownership before returning data.

---

# 14. Vehicle Management

Each vehicle belongs to a customer.

Vehicle information includes:

* Registration number
* Make
* Model
* Manufacturing year
* Additional JSONB details

Example:

```text
Customer
   ↓
Vehicle
   ├── Registration Number
   ├── Make
   ├── Model
   ├── Year
   └── Details
```

Vehicle year and registration data are validated using Pydantic schemas.

---

# 15. Booking Workflow

The service booking workflow is:

```text
Customer
    ↓
Vehicle
    ↓
Service Booking
    ↓
Technician
    ↓
Inspection
    ↓
Job Card
    ↓
Estimate
    ↓
Work
    ↓
Completed
    ↓
Service History
```

Booking status transitions are validated by the application.

The system does not allow arbitrary invalid workflow transitions.

---

# 16. Job-Card Workflow

A job card connects a service booking with the technician performing the work.

Typical workflow:

```text
Booking
   ↓
Technician Assignment
   ↓
Inspection
   ↓
Notes
   ↓
Estimate
   ↓
Work
   ↓
Completion
```

Job cards may contain:

* Technician
* Inspection notes
* Estimate
* Work status
* Timestamps

Customers can view appropriate completed service information but cannot modify technician job-card data.

---

# 17. Service History

Service history provides a historical record of completed services for a customer's vehicle.

Endpoint:

```text
GET /api/v1/vehicles/{vehicle_id}/service-history
```

Ownership authorization is performed before returning the information.

This prevents a customer from accessing another customer's vehicle history.

---

# 18. Document Upload

Authorized users can upload approved knowledge documents.

Supported formats:

```text
PDF
DOCX
TXT
Markdown
```

The system validates:

* File extension
* File type
* Safe storage path
* Document status
* Processing state

Uploaded documents are processed only as knowledge data.

They are not executed as programs.

---

# 19. Document Processing

The document loader supports:

```text
PDF  → page-based text extraction
DOCX → paragraphs/tables
TXT  → text extraction
MD   → Markdown text extraction
```

PDF page information is preserved where available.

Document metadata is stored with the knowledge document/chunks.

---

# 20. Chunking

Large documents are divided into smaller chunks before embedding.

The project uses configurable chunking parameters.

Current ingestion configuration uses approximately:

```text
Chunk size: 1200
Overlap:    200
```

The overlap helps preserve context between neighboring chunks.

Page metadata is retained where available.

---

# 21. Embeddings

The project uses a CPU-compatible Sentence Transformers model.

Configured model:

```text
sentence-transformers/all-MiniLM-L6-v2
```

Embedding dimension:

```text
384
```

The embedding service:

* Loads the model
* Generates embeddings
* Supports batches
* Normalizes vectors
* Validates embedding dimensions

No GPU is required.

---

# 22. pgvector

PostgreSQL is extended with the `vector` extension.

The application stores document chunk embeddings directly in PostgreSQL.

The extension can be enabled with:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

The project uses SQLAlchemy/pgvector integration for vector operations.

Similarity search is performed using cosine distance.

---

# 23. RAG

Retrieval-Augmented Generation is used to answer knowledge-based questions.

The process is:

```text
Question
   ↓
Question Embedding
   ↓
pgvector Similarity Search
   ↓
Relevant Knowledge Chunks
   ↓
Prompt Construction
   ↓
LLM / Retrieval-only Provider
   ↓
Answer + Sources
```

Only approved and completed knowledge documents are eligible for retrieval.

The system does not treat arbitrary user-provided text as trusted service-centre knowledge.

The assistant is instructed not to fabricate:

* Prices
* Warranty terms
* Service history
* Technician information
* Vehicle information
* Unsupported repair facts

---

# 24. Safety Guard

Before normal knowledge retrieval, potentially dangerous vehicle conditions are checked.

Examples include:

```text
Brake failure
Steering failure
Tyre/tire blowout
Fuel leakage
Electrical fire
Smoke
Severe overheating
Dangerous fluid leakage
```

When a dangerous condition is detected, the system recommends stopping use of the vehicle and contacting qualified professional assistance.

The assistant does not provide step-by-step repair instructions for potentially dangerous conditions.

---

# 25. Groq

Groq can be used as the LLM provider.

The provider is configured using environment variables.

Example:

```env
LLM_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=your_model_name
```

**Do not put a real API key into `README.md`, GitHub, source code, or `.env.example`.**

The actual `.env` file must remain local and must not be committed.

---

# 26. Retrieval-Only Mode

The application supports a retrieval-only fallback.

This allows the system to provide answers from retrieved approved knowledge without depending on an external LLM.

Conceptually:

```text
RAG
 │
 ├── Groq available
 │       ↓
 │     LLM Answer
 │
 └── Groq unavailable
         ↓
   Retrieval-only Answer
```

This improves resilience when an external LLM API is unavailable or not configured.

---

# 27. REST API

The application exposes REST endpoints under:

```text
/api/v1
```

Main API areas include:

```text
/auth
/customers
/vehicles
/service-types
/technicians
/bookings
/job-cards
/documents
/chat
```

Health endpoint:

```text
GET /health
```

---

# 28. WebSocket

Real-time chat is available through:

```text
/ws/chat/{session_id}
```

The WebSocket connection authenticates the user using a JWT token and validates chat-session ownership.

The WebSocket layer provides:

* Connection handling
* Authentication
* Session ownership validation
* Chat processing
* Error responses
* Connection management

---

# 29. Browser UI

A lightweight browser interface is provided using:

```text
HTML
CSS
JavaScript
```

Main frontend files:

```text
app/static/chat.html
app/static/chat.js
app/static/styles.css
```

The interface supports:

* Login
* JWT token handling
* Chat
* Loading state
* Error display
* Safety responses
* Retrieved sources
* WebSocket communication

---

# 30. PostgreSQL Setup

The project requires PostgreSQL.

Database name:

```text
vehicle_service_db
```

Create the database using PostgreSQL:

```powershell
psql -U postgres
```

Then inside the PostgreSQL shell:

```sql
CREATE DATABASE vehicle_service_db;
```

Connect to it:

```sql
\c vehicle_service_db
```

Enable pgvector:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Check the extension:

```sql
SELECT extversion
FROM pg_extension
WHERE extname = 'vector';
```

Exit:

```sql
\q
```

> PostgreSQL must be installed and available to the Windows command line.

---

# 31. Windows Installation

The project is designed for **Windows 10/11**, VS Code and PowerShell.

Open PowerShell and navigate to the project:

```powershell
cd "D:\FINAL PROJECT\vehicle-service-ai-assistant"
```

Create a virtual environment if it does not already exist:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution, run:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then activate again:

```powershell
.\.venv\Scripts\Activate.ps1
```

Upgrade pip:

```powershell
python -m pip install --upgrade pip
```

Install project dependencies:

```powershell
python -m pip install -r requirements.txt
```

---

# 32. Environment Variables

Create the local environment file:

```text
.env
```

The project should use `.env.example` as the template.

Example:

```env
APP_NAME=AI-Powered Vehicle Service Centre Knowledge and Booking Assistant
APP_VERSION=1.0.0
APP_ENVIRONMENT=development
DEBUG=true
HOST=127.0.0.1
PORT=8000

DATABASE_URL=postgresql+psycopg://postgres:YOUR_POSTGRES_PASSWORD@localhost:5432/vehicle_service_db

SECRET_KEY=YOUR_SECRET_KEY
ACCESS_TOKEN_EXPIRE_MINUTES=30

EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384
EMBEDDING_BATCH_SIZE=32

RETRIEVAL_TOP_K=5
RETRIEVAL_SIMILARITY_THRESHOLD=0.30

LLM_PROVIDER=groq
GROQ_API_KEY=
GROQ_MODEL=llama-3.1-8b-instant
```

Replace placeholders only in the local `.env`.

### Generate a secure secret key

Use:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Copy the generated value into your local `.env`.

### Security rules

Never commit:

```text
.env
```

Never place real:

* PostgreSQL passwords
* JWT secrets
* Groq API keys

inside source code or README files.

---

# 33. Alembic

Alembic is used for database schema migrations.

Do not use:

```python
Base.metadata.create_all()
```

for normal project database initialization.

Check migration history:

```powershell
python -m alembic history
```

Check the current migration:

```powershell
python -m alembic current
```

Apply migrations:

```powershell
python -m alembic upgrade head
```

Create a new migration after intentional model changes:

```powershell
python -m alembic revision --autogenerate -m "describe your change"
```

Then apply it:

```powershell
python -m alembic upgrade head
```

Downgrade one migration when required:

```powershell
python -m alembic downgrade -1
```

---

# 34. Sample Data

The project provides scripts for creating administrative and sample data.

From the project root:

```powershell
python -m scripts.create_admin
```

Seed sample application data:

```powershell
python -m scripts.seed_data
```

Check the local installation:

```powershell
python -m scripts.check_local_setup
```

These scripts use the configured PostgreSQL database.

---

# 35. Knowledge Ingestion

Place approved knowledge files into:

```text
data/knowledge_base/
```

Supported files:

```text
.pdf
.docx
.txt
.md
.markdown
```

Then run:

```powershell
python -m scripts.ingest_knowledge_base
```

The ingestion process:

```text
Knowledge File
      ↓
Document Loader
      ↓
Text Extraction
      ↓
Chunking
      ↓
KnowledgeDocument
      ↓
KnowledgeChunk
      ↓
Embedding Generation
      ↓
pgvector
```

Documents are marked with processing status such as:

```text
PROCESSING
COMPLETED
FAILED
```

Only completed documents are used by retrieval.

---

# 36. Running the Application

Activate the virtual environment:

```powershell
cd "D:\FINAL PROJECT\vehicle-service-ai-assistant"
```

```powershell
.\.venv\Scripts\Activate.ps1
```

Make sure PostgreSQL is running.

Apply migrations:

```powershell
python -m alembic upgrade head
```

Start FastAPI:

```powershell
python -m uvicorn app.main:app --reload
```

The development server normally starts at:

```text
http://127.0.0.1:8000
```

---

# 37. Swagger API Documentation

FastAPI automatically provides interactive API documentation.

Open:

```text
http://127.0.0.1:8000/docs
```

The OpenAPI specification is available at:

```text
http://127.0.0.1:8000/openapi.json
```

Swagger can be used to test:

* Authentication
* Customers
* Vehicles
* Service types
* Technicians
* Bookings
* Job cards
* Documents
* Chat

For protected endpoints, first obtain a JWT token through the login endpoint and authorize the Swagger session.

---

# 38. Testing

The project uses Pytest.

Run all tests:

```powershell
python -m pytest
```

Run tests with verbose output:

```powershell
python -m pytest -v
```

Run a specific test file:

```powershell
python -m pytest tests\test_auth.py -v
```

Run service-history tests:

```powershell
python -m pytest tests\test_service_history.py -v
```

Run safety tests:

```powershell
python -m pytest tests\test_safety.py tests\test_vehicle_safety_guard.py -v
```

Run the complete test suite with coverage:

```powershell
pytest --cov=app --cov-report=term-missing
```

The tests cover areas including:

* Authentication
* Invalid login
* Vehicle validation
* Customer ownership
* Booking workflow
* Job cards
* Documents
* RAG
* Safety guard
* Chat
* Service history

---

# 39. Docker

Docker configuration files are included in the project:

```text
Dockerfile
docker-compose.yml
```

However, the primary development and testing workflow for this project is **Windows + PowerShell + local PostgreSQL + Python virtual environment**.

The application does not require Docker for the standard local setup described above.

No SQLite database is used.

---

# 40. GitHub

Initialize Git from the project root:

```powershell
cd "D:\FINAL PROJECT\vehicle-service-ai-assistant"
```

Initialize the repository:

```powershell
git init
```

Check the repository:

```powershell
git status
```

Add project files:

```powershell
git add .
```

Create the first commit:

```powershell
git commit -m "Initial project setup and implementation"
```

Rename the branch to `main`:

```powershell
git branch -M main
```

Add the GitHub repository:

```powershell
git remote add origin https://github.com/YOUR_USERNAME/vehicle-service-ai-assistant.git
```

Verify:

```powershell
git remote -v
```

Push:

```powershell
git push -u origin main
```

Check status:

```powershell
git status
```

### Important GitHub security rule

Before committing, verify that `.env` is ignored.

The repository must not contain:

```text
.env
```

or any file containing real:

```text
DATABASE_URL credentials
SECRET_KEY
GROQ_API_KEY
```

Use `.env.example` for safe configuration documentation.

---

# 41. Troubleshooting

## Problem: `relation "users" does not exist`

This normally means the database migration has not created the application tables.

Check the configured database:

```powershell
python -c "from app.core.config import settings; print(settings.database_url)"
```

Check Alembic:

```powershell
python -m alembic current
```

Apply migrations:

```powershell
python -m alembic upgrade head
```

Check PostgreSQL tables:

```powershell
psql -U postgres -d vehicle_service_db -c "\dt"
```

The database should contain application tables such as:

```text
users
customers
vehicles
service_types
technicians
service_bookings
job_cards
knowledge_documents
knowledge_chunks
chat_sessions
chat_messages
```

---

## Problem: PowerShell activation is blocked

Run:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then:

```powershell
.\.venv\Scripts\Activate.ps1
```

---

## Problem: PostgreSQL connection error

Check that PostgreSQL is running.

Verify the connection:

```powershell
psql -U postgres -d vehicle_service_db
```

Also verify that `.env` contains the correct local `DATABASE_URL`.

---

## Problem: `psql` is not recognized

PostgreSQL's `bin` directory may not be in the Windows PATH.

Use the PostgreSQL installation's `psql.exe` or add the PostgreSQL `bin` directory to the Windows PATH.

---

## Problem: `vector` extension does not exist

Connect to the project database:

```powershell
psql -U postgres -d vehicle_service_db
```

Then run:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Verify:

```sql
SELECT extversion
FROM pg_extension
WHERE extname = 'vector';
```

---

## Problem: Embedding model download

The first embedding operation may take longer because the Sentence Transformers model needs to be downloaded and initialized.

Subsequent runs can reuse the local model cache.

The selected model is CPU-compatible and does not require a GPU.

---

## Problem: Groq is unavailable

The project supports retrieval-only behavior.

Check:

```env
LLM_PROVIDER=groq
GROQ_API_KEY=
```

If an external LLM cannot be used, the retrieval-only provider can be used as the fallback path.

---

## Problem: Login returns HTTP 500

First verify that the database contains the `users` table:

```powershell
psql -U postgres -d vehicle_service_db -c "\dt"
```

Then verify migrations:

```powershell
python -m alembic current
```

Apply them if necessary:

```powershell
python -m alembic upgrade head
```

---

## Problem: Import errors

Make sure the virtual environment is activated:

```powershell
.\.venv\Scripts\Activate.ps1
```

Then install dependencies:

```powershell
python -m pip install -r requirements.txt
```

For project scripts, use module execution from the project root:

```powershell
python -m scripts.seed_data
```

rather than:

```powershell
python scripts/seed_data.py
```

---

# 42. Security Considerations

The application follows several security principles:

* Passwords are hashed.
* JWT secrets come from environment variables.
* API keys are not hard-coded.
* PostgreSQL credentials are not hard-coded.
* `.env` is excluded from Git.
* Customer ownership is validated.
* Role-based authorization is enforced.
* Uploaded document types are restricted.
* Knowledge retrieval uses approved documents.
* Arbitrary uploaded content is not executed.
* Dangerous vehicle conditions trigger the safety guard.
* Customers cannot modify protected job-card information.

---

# 43. Project Workflow Summary

The complete system can be represented as:

```text
                    CUSTOMER
                       │
                       ▼
                   Login/JWT
                       │
                       ▼
                  Own Vehicle
                       │
                       ▼
                 Book Service
                       │
                       ▼
                 Technician
                       │
                       ▼
                   Job Card
                       │
                       ▼
                  Service Work
                       │
                       ▼
                    Complete
                       │
                       ▼
                Service History


                    KNOWLEDGE
                       │
                       ▼
                Upload Document
                       │
                       ▼
                 Extract Text
                       │
                       ▼
                    Chunking
                       │
                       ▼
                  Embeddings
                       │
                       ▼
                    pgvector
                       │
                       ▼
                    Retrieval
                       │
                       ▼
                 Safety Guard
                       │
                       ▼
                  Groq / RAG
                       │
                       ▼
                Answer + Sources
```

---

# 44. API and AI Flow

For a normal knowledge question:

```text
User
 ↓
POST /api/v1/chat
 ↓
Chat Service
 ↓
Safety Guard
 ↓
RAG Service
 ↓
Embedding Service
 ↓
PostgreSQL + pgvector
 ↓
Relevant Knowledge Chunks
 ↓
Prompt Builder
 ↓
Groq
 ↓
Answer
 ↓
Sources
 ↓
Chat History
```

For a dangerous vehicle question:

```text
User
 ↓
POST /api/v1/chat
 ↓
Safety Guard
 ↓
Danger detected
 ↓
Safety response
```

The dangerous request does not proceed through normal repair-oriented generation.

---

# 45. Future Improvements

Potential future enhancements include:

1. Appointment reminders.
2. Email/SMS notifications.
3. WhatsApp integration.
4. Online payment integration.
5. Advanced technician scheduling.
6. Spare-parts inventory management.
7. Invoice generation.
8. Customer feedback and ratings.
9. Vehicle maintenance reminders.
10. Multilingual AI responses.
11. Voice-based vehicle assistant.
12. More advanced document metadata filtering.
13. Hybrid keyword + vector retrieval.
14. Reranking models.
15. Better citation/source presentation.
16. Audit logging.
17. Rate limiting.
18. Production-grade WebSocket authentication.
19. Background document processing.
20. Cloud deployment.
21. Monitoring and observability.
22. Automated CI/CD.
23. Larger domain-specific knowledge bases.
24. Mobile application integration.

---

# 46. Final Project Status

The project demonstrates the integration of:

```text
FastAPI
   +
PostgreSQL
   +
SQLAlchemy
   +
Alembic
   +
JWT Authentication
   +
RBAC
   +
Customer Ownership
   +
Vehicle Service Management
   +
Job Cards
   +
Service History
   +
Document Processing
   +
Chunking
   +
Sentence Transformers
   +
pgvector
   +
RAG
   +
Safety Guard
   +
Groq
   +
Retrieval-only Fallback
   +
REST API
   +
WebSocket
   +
Browser UI
   +
Pytest
   +
Git/GitHub
```

This provides a complete foundation for an AI-enabled vehicle service centre management and knowledge-assistance platform.

---

## License

This project is developed as an academic final-year project.

Add an appropriate license if the project is later distributed publicly.