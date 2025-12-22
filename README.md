## Tech Stack

- **Backend Framework:** FastAPI  
- **Database:** SQLite (`db.sqlite`)  
- **ORM:** SQLAlchemy  
- **Authentication:** JWT (stored in HTTP-only cookies)  
- **Password Hashing:** bcrypt  
- **Rate Limiting:** SlowAPI  
- **Environment Configuration:** python-dotenv  



## Local Setup (macOS)

This project was developed and tested on **macOS (MacBook)** using the following environment:

- **Python:** 3.13.5  
- **pip:** 25.2  
- **OS:** macOS  

The steps below assume a macOS system.

---

## Step 1: Clone the Repository

git clone <this-repository-url>
cd <this-project-folder>

---

## Step 2: Create and Activate Virtual Environment

- Create a virtual environment:
python3 -m venv venv
Activate it:

source venv/bin/activate


After activation, (venv) should appear in your terminal.

## Step 3: Install Dependencies

Install all required dependencies using the frozen requirements file:

python -m pip install -r requirements.txt
## Step 4: Environment Configuration

Create a .env file in the project root directory:

touch .env


Add the following values to the file:

JWT_SECRET_KEY=CHANGE_ME_SUPER_SECRET
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

## Step 5: Database Setup

The application uses SQLite

No manual database setup is required

Database tables are created automatically on application startup

## Step 6: Run the Application

Start the FastAPI development server:

uvicorn main:app --reload


The server will start at:

http://127.0.0.1:8000

Step 7: Access API Documentation

Open your browser and visit:

http://localhost:8000/docs
--

## Prerequisites

Ensure the following are installed on your Mac:

- Python **3.10+** (tested with **Python 3.13.5**)
- pip (tested with **pip 25.2**)
- Git

Verify versions:

python --version
pip --version


## Project Folder Structure

---

### `app/`

This is the main application folder.  
All backend code lives inside this directory.

---

### `app/routes/`

This folder contains all API route definitions.

- Each file groups related APIs together.
- Keeping routes separated by feature makes the API structure clean and easy to navigate.

#### Route Files

- **`auth.py`**  
  Contains authentication-related APIs such as manager signup, login, and logout.

- **`task.py`**  
  Contains task-related APIs such as creating tasks, assigning tasks, listing tasks, and updating task status.

- **`user.py`**  
  Contains user management APIs such as creating reportee accounts under a manager.

---

### `app/models/`

This folder contains SQLAlchemy ORM models that define the database schema.

#### Model Files

- **`company.py`**  
  Defines the `Company` model, which represents a tenant in the system.

- **`user.py`**  
  Defines the `User` model for both managers and reportees.

- **`task.py`**  
  Defines the `Task` model, including task status, assignment, and ownership.

All models inherit from a shared SQLAlchemy `Base` so that tables can be created and managed consistently.

---

### `app/schemas/`

This folder contains Pydantic schemas used for request and response validation.

Schemas define:
- What data an API expects as input
- What data is returned in responses

This ensures proper data validation and prevents invalid input from reaching the business logic layer.

---

### `app/core/`

This folder contains shared core logic reused across the application.

#### Core Files

- **`auth.py`**  
  Handles extracting and validating the current user from JWT cookies.

- **`jwt.py`**  
  Contains logic for creating and verifying JWT tokens.

- **`security.py`**  
  Handles password hashing and verification using bcrypt.

- **`permissions.py`**  
  Contains role-based permission checks such as `require_manager` and `require_reportee`.

- **`rate_limit.py`**  
  Configures API rate limiting using SlowAPI.

- **`config.py`**  
  Loads environment variables and central configuration such as rate limits.

Keeping this logic in one place avoids duplication and keeps route handlers clean.

---

### `app/db/`

This folder handles database setup and configuration.

- **`database.py`**  
  Creates the SQLAlchemy engine and session.

- **`deps.py`**  
  Defines the database session.

This separation keeps database configuration isolated from business logic.

---

### `main.py`

This is the application entry point.

#### Responsibilities

- Creating the FastAPI application
- Registering all routers
- Initializing rate limiting
- Creating database tables on startup
- Starting the application server


## Authentication & Authorization Layer

- Authentication is handled using **JWT tokens stored in HTTP-only cookies**
- JWT payload contains:
  - `sub` (user ID)
  - `role`
  - `company_id`
- Authorization is enforced using **dependency-based permissions**:
  - `require_manager`
  - `require_reportee`

This ensures:
- Only authorized roles can access specific APIs
- Authentication and authorization logic is reusable and centralized

---

## Multi-Tenant Design (Company-Based Isolation)

- Each user and task is associated with a `company_id`
- Company is created **implicitly during manager signup**
- All database queries are scoped by `company_id`

This guarantees:
- Strong tenant isolation
- No cross-company data access
- Secure multi-tenant behavior

---

## Task Management Architecture

- Managers create and assign tasks
- Tasks follow a controlled lifecycle (`DEV`, `TEST`, `STUCK`, `COMPLETED`)
- Reportees can update task status **only to `COMPLETED`**
- Managers can update task status at any stage
- Tasks use **soft delete** (`is_deleted`) instead of hard deletion
- Manager can see all the tasks created by him,, while Reportee can see all the task assigned to him
- Tasks are displayed in pagination, page size can configured in config.py

---

## Rate Limiting & Abuse Prevention

- Implemented using **SlowAPI**
- Rate limiting strategy:
  - **Unauthenticated users:** limited by IP address
  - **Authenticated users:** limited by user ID
- Different rate limits are applied per API
- Limits are centrally configurable

This prevents:
- Brute-force attacks
- API abuse
- Resource exhaustion

---


## Persistence Layer

- Database: **SQLite**
- ORM: **SQLAlchemy**
- Tables are created automatically on application startup
- ORM models inherit from a single shared `Base`

This keeps the setup simple while maintaining clear data modeling.

---


# Data Models Overview

Each model has a clear responsibility, and all relationships are explicitly defined using foreign keys.

---

## Company Model

The **Company** model represents a tenant in the system.

- The `id` field is the primary key and is used internally to associate users and tasks with the same company.
- The `name` field stores the company name provided during manager signup and is marked as **unique** to prevent duplicate companies.
- The `created_at` field stores the timestamp when the company was created, supporting auditing and future tracking.

## Creation Rules

- A company is created automatically during manager signup.
- There is **no separate API** to create a company.

This design ensures:
- A company cannot exist without at least one manager.
- Orphan company records are avoided.

---

## User Model

The **User** model stores both managers and reportees in a single table.

## Core Fields

- `id`  
  Uniquely identifies each user.

- `username`  
  Used as the login identifier and kept **unique** to prevent duplicate accounts.

- `password_hash`  
  Stores the **bcrypt-hashed** password instead of plaintext to ensure security.

- `role`  
  Defines whether the user is a `MANAGER` or a `REPORTEE`.  
  Enforced at the API level using role-based permissions.

## Relationships & Access Control

- `company_id`  
  Links the user to a specific company and is the foundation of **tenant isolation**.  
  All access control checks rely on this field to ensure users can only access data belonging to their own company.

- `manager_id`  
  Used only for reportees.  
  Links a reportee to the manager who created them, establishing a reporting hierarchy and ensuring each reportee belongs to exactly one manager.

## Account State & Auditing

- `is_active`  
  Allows users to be disabled without deleting their records, supporting safer account management and future auditing.

- `created_at`
- `updated_at`  
  Track when the user was created and last updated.

## Relationships

- Users are linked to their company.
- Reportees are additionally linked to their manager.

---

## Task Model

The **Task** model represents work items managed within a company.

## Core Fields

- `id`  
  Uniquely identifies each task.

- `title`  
  Stores a short name for the task and is **required**.

- `description`  
  Stores optional detailed information about the task.

- `status`  
  Represents the task lifecycle and defaults to `DEV`.

  Valid statuses:
  - `DEV`
  - `TEST`
  - `STUCK`
  - `COMPLETED`

  Status transitions are enforced at the application level based on user role.

## Relationships & Ownership

- `assigned_to_id`  
  Links the task to a reportee.  
  This field is nullable to allow managers to create unassigned tasks.  
  Assignment is validated to ensure the reportee belongs to the same company.

- `created_by_id`  
  Stores the manager who created the task, ensuring clear ownership and allowing only the creator to modify or delete the task.

- `company_id`  
  Links the task to a company and enforces **tenant isolation**.  
  All task queries are scoped using this field to prevent cross-company access.

## Soft Deletion & Auditing

- `is_deleted`  
  Implements **soft deletion**.  
  Tasks are marked as deleted instead of being permanently removed, preventing accidental data loss and enabling future recovery.

- `created_at`
- `updated_at`  
  Track when the task was created and last modified.

## Relationships

- Tasks are linked to:
  - The assigned reportee
  - The manager who created the task


## Inspecting the SQLite Database

Navigate to the project root where `db.sqlite` is located and open the database:
```
sqlite3 db.sqlite
```

Once inside the SQLite prompt, run the following commands:
List All Tables
```
.tables
```

View Users
```
SELECT * FROM users;
```

View Companies
```
SELECT * FROM companies;
```

View Tasks
```
SELECT * FROM tasks;
```


Exit the SQLite Prompt
```
.exit
```


## Possible Improvements

- Add proper application logging for important actions and errors.

- Enforce password complexity rules during signup.

- Add account lockout after multiple failed login attempts.

- Improve request and response validation error logging.

- Add task priority support (`LOW`, `MEDIUM`, `HIGH`).

- Add an API to list all reportees under a manager.

- Add task categories for better task organization.

- Add database indexing on task-related columns to improve query performance.

- Add filtering and searching capabilities on tasks.

- Use Redis to improve performance for filtering, searching, and rate limiting.
