# AI-Powered Vehicle Service Centre Knowledge and Booking Assistant

An AI-powered vehicle service centre assistant that helps customers with vehicle service information, service bookings, service history, job cards, and knowledge-based questions.

## Project Overview

The system combines a FastAPI backend, PostgreSQL database, pgvector-based semantic search, Retrieval-Augmented Generation (RAG), and an optional Groq LLM provider.

The application is designed to provide:

* Vehicle and customer management
* Service type management
* Service booking
* Technician management
* Job card management
* Vehicle service history
* Knowledge document processing
* Text chunking and embeddings
* PostgreSQL + pgvector vector search
* RAG-based answers
* Vehicle safety protection
* JWT authentication and role-based authorization
* REST API
* WebSocket-based chat
* Web-based chat interface

## Technology Stack

### Backend

* Python
* FastAPI
* Pydantic
* SQLAlchemy
* Alembic

### Database

* PostgreSQL
* JSONB
* pgvector

### Authentication

* JWT
* Password hashing
* Role-based authorization

### AI / RAG

* Sentence Transformers
* Vector similarity search
* Retrieval-Augmented Generation
* Groq LLM integration
* Retrieval-only fallback

### Frontend

* HTML
* CSS
* JavaScript
* WebSocket

### Testing

* Pytest
* Pytest-Cov

## Main Features

### Customer Management

Customers can manage their vehicle-related information through authenticated APIs.

### Vehicle Management

The system stores:

* Registration number
* Make
* Model
* Year
* Vehicle details

### Service Booking

Customers can create and manage service bookings for their own vehicles.

### Technician and Job Cards

Authorized staff can manage technicians and job cards, including:

* Inspection notes
* Technician assignment
* Estimates
* Work status
* Completion status

### Service History

Customers can view the service history of vehicles they are authorized to access.

Unauthorized access to another customer's vehicle history is blocked.

### Knowledge Base

The system supports knowledge documents in:

* PDF
* DOCX
* TXT
* Markdown

Documents are processed into chunks and converted into embeddings.

### Vector Search

Document embeddings are stored in PostgreSQL using pgvector.

The system performs semantic similarity search to retrieve relevant knowledge for user questions.

### RAG

The RAG pipeline:

1. Receives the user's question
2. Applies safety checks
3. Retrieves relevant approved knowledge
4. Builds a grounded context
5. Generates an answer using the configured LLM provider
6. Returns source information

### Vehicle Safety

Potentially dangerous situations such as brake failure, steering failure, tyre failure, fuel leakage, electrical fire, smoke, severe overheating, and dangerous fluid leakage are detected and handled with safety-focused responses.

The system does not provide step-by-step repair instructions for potentially dangerous vehicle conditions.

### Chat

The project provides:

* REST chat API
* Chat sessions
* Chat history
* WebSocket chat
* Retrieved document sources

## Project Structure

```text
vehicle-service-ai-assistant/
│
├── alembic/
├── app/
│   ├── api/
│   ├── core/
│   ├── crud/
│   ├── db/
│   ├── llm/
│   ├── schemas/
│   ├── services/
│   ├── static/
│   └── websocket/
│
├── data/
│   ├── knowledge_base/
│   ├── storage/
│   └── vector_index/
│
├── scripts/
├── tests/
│
├── .env.example
├── .gitignore
├── alembic.ini
├── README.md
└── requirements.txt
```

## Requirements

* Windows 10/11
* Python 3.13
* PostgreSQL
* PostgreSQL pgvector extension
* VS Code
* Git

## Environment Configuration

Create a local `.env` file from `.env.example`.

The `.env` file contains local configuration and secrets and must never be committed to GitHub.

Example:

```env
DATABASE_URL=postgresql+psycopg://postgres:YOUR_POSTGRES_PASSWORD@localhost:5432/vehicle_service_db
SECRET_KEY=YOUR_SECRET_KEY
GROQ_API_KEY=YOUR_GROQ_API_KEY
```

Do not use the example values as real credentials.

## Installation

Create and activate the virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Database

Create the PostgreSQL database:

```text
vehicle_service_db
```

Make sure PostgreSQL and pgvector are installed and available.

Run migrations:

```powershell
python -m alembic upgrade head
```

## Run the Application

Start the FastAPI server:

```powershell
python -m uvicorn app.main:app --reload
```

The application will normally be available at:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
http://127.0.0.1:8000/health
```

## Useful Scripts

Create an administrator:

```powershell
python -m scripts.create_admin
```

Seed sample data:

```powershell
python -m scripts.seed_data
```

Check local setup:

```powershell
python -m scripts.check_local_setup
```

Ingest knowledge-base documents:

```powershell
python -m scripts.ingest_knowledge_base
```

## Testing

Run the complete test suite:

```powershell
pytest
```

Run tests with coverage:

```powershell
pytest --cov=app --cov-report=term-missing
```

## Security

The following must never be committed to the repository:

* `.env`
* Database passwords
* JWT secret keys
* API keys
* Personal credentials
* Private uploaded documents
* Customer information
* Virtual environment
* Python cache
* Local database files
* Generated logs

Use `.env.example` with placeholder values for configuration documentation.

## Docker

Docker deployment is intentionally not included in the current development setup.

The application is currently designed to run directly on Windows using Python, PostgreSQL, and the local virtual environment.

## Project Status

This project is being developed as a final-year academic project.

Core components include authentication, database models, service booking, job cards, document processing, embeddings, vector search, RAG, safety handling, chat, WebSocket communication, testing, and GitHub source control.
