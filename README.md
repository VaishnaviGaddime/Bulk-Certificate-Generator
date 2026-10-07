# Bulk Certificate Generator API

A backend API for generating participation certificates in bulk from a single predefined certificate template.

The application accepts event details and multiple recipients, generates individual PDF certificates, tracks generation status and progress, handles failures independently, and provides APIs to retrieve and download generated certificates.

## Features

* Bulk certificate generation from a single API request
* Predefined certificate template using Jinja2
* PDF certificate generation using ReportLab
* Input validation using Pydantic
* Email format validation
* Relational database using SQLite and SQLAlchemy
* Job and certificate status tracking
* Generation progress tracking
* Individual certificate retrieval
* PDF download endpoint
* Failure isolation — one failed certificate does not stop the remaining certificates
* Automated API tests using pytest
* Interactive API documentation using Swagger UI

## Tech Stack

* **Python 3.11**
* **FastAPI** — REST API framework
* **Pydantic** — request and response validation
* **SQLAlchemy** — ORM and database operations
* **SQLite** — relational database
* **Jinja2** — certificate template rendering
* **ReportLab** — PDF generation
* **Pytest** — automated testing
* **HTTPX** — API testing
* **Uvicorn** — ASGI server
* **Git/GitHub** — version control and submission

## Architecture

The application follows a simple layered backend architecture:

```text
Client
  |
  v
FastAPI Routes
  |
  v
Pydantic Validation
  |
  v
Job Processing
  |
  +--------------------+
  |                    |
  v                    v
SQLAlchemy           Certificate
Database             Generation
  |                    |
  v                    v
SQLite              PDF Files
```

### Main workflow

```text
POST /api/jobs/
       |
       v
Validate request
       |
       v
Create generation job
       |
       v
Create certificate records
       |
       v
Generate certificates individually
       |
       +---- Success ---> COMPLETED
       |
       +---- Failure ---> FAILED
       |
       v
Update job progress
       |
       v
Return job status
```

## Project Structure

```text
bulk-certificate-generator/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   └── jobs.py
│   │
│   └── services/
│       ├── __init__.py
│       └── certificate_service.py
│
├── templates/
│   └── certificate_template.html
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_jobs.py
│   ├── test_validation.py
│   ├── test_status.py
│   ├── test_certificates.py
│   ├── test_failure.py
│   └── test_download.py
│
├── generated/
├── requirements.txt
├── .gitignore
└── README.md
```

## Database Design

The application uses two main tables.

### GenerationJob

Stores information about a bulk certificate generation request.

| Field                     | Description                         |
| ------------------------- | ----------------------------------- |
| `id`                      | Unique job identifier               |
| `event_name`              | Name of the event                   |
| `organization`            | Organization conducting the event   |
| `event_date`              | Event date                          |
| `status`                  | Current job status                  |
| `total_certificates`      | Total certificates requested        |
| `successful_certificates` | Successfully generated certificates |
| `failed_certificates`     | Failed certificate generations      |
| `created_at`              | Job creation timestamp              |
| `completed_at`            | Job completion timestamp            |

### Certificate

Stores information about each individual certificate.

| Field             | Description                       |
| ----------------- | --------------------------------- |
| `id`              | Unique certificate identifier     |
| `job_id`          | Related generation job            |
| `recipient_name`  | Recipient name                    |
| `recipient_email` | Recipient email                   |
| `status`          | Certificate generation status     |
| `file_path`       | Generated PDF path                |
| `error_message`   | Error details if generation fails |
| `created_at`      | Certificate creation timestamp    |

Relationship:

```text
GenerationJob 1 -------- N Certificate
```

One generation job can contain multiple certificates.

## API Endpoints

### 1. Create Bulk Generation Job

**POST**

```text
/api/jobs/
```

Creates a bulk certificate generation job.

Example request:

```json
{
  "event_name": "Python Workshop",
  "organization": "AEREO",
  "event_date": "2026-10-15",
  "recipients": [
    {
      "name": "Vaishnavi Gaddime",
      "email": "vaishnavi@example.com"
    },
    {
      "name": "Rahul Sharma",
      "email": "rahul@example.com"
    }
  ]
}
```

Example response:

```json
{
  "job_id": 1,
  "status": "COMPLETED",
  "total_certificates": 2,
  "successful_certificates": 2,
  "failed_certificates": 0,
  "message": "Bulk certificate generation completed"
}
```

### 2. Get Job Status

**GET**

```text
/api/jobs/{job_id}
```

Example:

```text
/api/jobs/1
```

Response:

```json
{
  "job_id": 1,
  "status": "COMPLETED",
  "total_certificates": 2,
  "successful_certificates": 2,
  "failed_certificates": 0,
  "progress": "2/2"
}
```

### 3. Get Job Certificates

**GET**

```text
/api/jobs/{job_id}/certificates
```

Returns all certificates associated with a generation job.

Example:

```text
/api/jobs/1/certificates
```

### 4. Download Certificate

**GET**

```text
/api/jobs/certificates/{certificate_id}/download
```

Returns the generated certificate as a PDF file.

Example:

```text
/api/jobs/certificates/1/download
```

## Certificate Generation

The certificate uses a predefined HTML template located at:

```text
templates/certificate_template.html
```

Jinja2 is used to populate the template data:

* Recipient name
* Event name
* Organization
* Event date

ReportLab is used to generate the final PDF certificate.

Generated files are stored locally in:

```text
generated/
```

The generated directory is excluded from Git using `.gitignore`.

## Failure Handling

Certificate generation is handled independently for each recipient.

For example, if a job contains:

```text
Recipient A → Success
Recipient B → Failure
Recipient C → Success
```

the application continues processing instead of stopping the entire job.

The final job status becomes:

```text
PARTIAL_FAILURE
```

The response tracks:

```text
Total:      3
Successful: 2
Failed:     1
```

The failed certificate also stores an error message for debugging.

This ensures that a single certificate generation failure does not affect other recipients.

## Validation

The API validates incoming data using Pydantic.

Validation includes:

* Event name must contain at least 2 characters
* Organization must contain at least 2 characters
* At least one recipient is required
* Recipient name must contain at least 2 characters
* Recipient email must be a valid email address

Invalid requests return HTTP `422 Unprocessable Entity`.

## Running the Application

### 1. Clone the repository

```bash
git clone <your-github-repository-url>
cd bulk-certificate-generator
```

### 2. Create a virtual environment

Windows:

```powershell
python -m venv venv
```

Activate it:

```powershell
venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Start the server

```powershell
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

### 5. Open Swagger UI

```text
http://127.0.0.1:8000/docs
```

Swagger UI can be used to test all API endpoints interactively.

## Running Tests

Run the complete automated test suite:

```powershell
pytest
```

The current test suite covers:

* Bulk job creation
* Empty recipient validation
* Invalid email validation
* Job status and progress
* Certificate retrieval
* Certificate PDF download
* Failure isolation

Current result:

```text
6 passed
```

## Design Decisions

### Why FastAPI?

FastAPI provides:

* Automatic request validation
* Automatic OpenAPI documentation
* Easy REST API development
* Strong Python type-hint support
* Good fit for backend services

### Why SQLite?

SQLite was selected for simplicity and easy local development.

The database layer uses SQLAlchemy, so the application can be migrated to PostgreSQL or another relational database with minimal architectural changes.

### Why SQLAlchemy?

SQLAlchemy provides:

* ORM-based database operations
* Relationship handling
* Database abstraction
* Easy migration from SQLite to PostgreSQL

### Why ReportLab?

ReportLab provides direct PDF generation from Python without requiring an external PDF service.

### Why individual certificate processing?

Each recipient is processed independently so that one failure does not stop the entire bulk generation job.

## API Documentation

FastAPI automatically generates interactive documentation.

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

## Future Improvements

Possible improvements for a production version include:

* Background job processing using Celery or a task queue
* Redis for job queue and progress tracking
* PostgreSQL for production database usage
* Authentication and authorization
* Certificate email delivery
* Configurable certificate templates
* Uploading custom templates
* Cloud storage for generated certificates
* Docker containerization
* Deployment to a cloud platform
* Pagination for large certificate lists
* Structured application logging

## Author

**Vaishnavi Gaddime**

Computer Science and Engineering Graduate

Built as part of the AEREO Software Development Intern assignment.