## Tech Stack

- **Backend Framework:** FastAPI  
- **Database:** SQLite (`db.sqlite`)  
- **ORM:** SQLAlchemy  
- **Authentication:** JWT (stored in HTTP-only cookies)  
- **Password Hashing:** bcrypt  
- **Rate Limiting:** SlowAPI  
- **Environment Configuration:** python-dotenv  



## Local Setup (macOS)

This project was **developed and tested on macOS (MacBook)** using the following environment:

- **Python:** 3.13.5  
- **pip:** 25.2  
- **OS:** macOS  

The steps below assume a macOS system.

---

## Prerequisites

Ensure the following are installed on your Mac:

- Python **3.10+** (tested with **Python 3.13.5**)
- pip (tested with **pip 25.2**)
- Git

Verify versions:

```bash
python --version
pip --version


## Application Architecture


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

### Creation Rules

- A company is created automatically during manager signup.
- There is **no separate API** to create a company.

This design ensures:
- A company cannot exist without at least one manager.
- Orphan company records are avoided.

---

## User Model

The **User** model stores both managers and reportees in a single table.

### Core Fields

- `id`  
  Uniquely identifies each user.

- `username`  
  Used as the login identifier and kept **unique** to prevent duplicate accounts.

- `password_hash`  
  Stores the **bcrypt-hashed** password instead of plaintext to ensure security.

- `role`  
  Defines whether the user is a `MANAGER` or a `REPORTEE`.  
  Enforced at the API level using role-based permissions.

### Relationships & Access Control

- `company_id`  
  Links the user to a specific company and is the foundation of **tenant isolation**.  
  All access control checks rely on this field to ensure users can only access data belonging to their own company.

- `manager_id`  
  Used only for reportees.  
  Links a reportee to the manager who created them, establishing a reporting hierarchy and ensuring each reportee belongs to exactly one manager.

### Account State & Auditing

- `is_active`  
  Allows users to be disabled without deleting their records, supporting safer account management and future auditing.

- `created_at`
- `updated_at`  
  Track when the user was created and last updated.

### Relationships

- Users are linked to their company.
- Reportees are additionally linked to their manager.

---

## Task Model

The **Task** model represents work items managed within a company.

### Core Fields

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

### Relationships & Ownership

- `assigned_to_id`  
  Links the task to a reportee.  
  This field is nullable to allow managers to create unassigned tasks.  
  Assignment is validated to ensure the reportee belongs to the same company.

- `created_by_id`  
  Stores the manager who created the task, ensuring clear ownership and allowing only the creator to modify or delete the task.

- `company_id`  
  Links the task to a company and enforces **tenant isolation**.  
  All task queries are scoped using this field to prevent cross-company access.

### Soft Deletion & Auditing

- `is_deleted`  
  Implements **soft deletion**.  
  Tasks are marked as deleted instead of being permanently removed, preventing accidental data loss and enabling future recovery.

- `created_at`
- `updated_at`  
  Track when the task was created and last modified.

### Relationships

- Tasks are linked to:
  - The assigned reportee
  - The manager who created the task
