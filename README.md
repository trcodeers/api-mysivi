# Secure Multi-Tenant Task Management System

A secure, multi-tenant task management system built with **FastAPI** and **SQLite**, supporting role-based access control, company-level data isolation, and API abuse prevention through rate limiting.

The system allows **Managers** to create and assign tasks to **Reportees**, while enforcing strict permissions and security rules.

---

## Features

- Multi-tenant architecture (company-based isolation)
- Role-based access control (Manager / Reportee)
- JWT authentication using HTTP-only cookies
- Secure task lifecycle management
- API rate limiting (IP-based & user-based)
- Configurable rate limits
- Soft delete for tasks
- Clean and scalable architecture

---

## Tech Stack

- **Backend:** FastAPI
- **Database:** SQLite
- **ORM:** SQLAlchemy
- **Authentication:** JWT (HTTP-only cookies)
- **Rate Limiting:** SlowAPI
- **Password Hashing:** Passlib (bcrypt)
- **API Docs:** Swagger (OpenAPI)

---

## Core Concepts

### Multi-Tenancy
Each company’s data is isolated using a `company_id`.  
All queries enforce company-level filtering to prevent data leakage across tenants.

### Roles
- **Manager**
  - Can sign up and log in
  - Can create reportees
  - Can create, assign, update, and delete tasks
- **Reportee**
  - Can log in using manager-created credentials
  - Can view assigned tasks
  - Can update task status only to `COMPLETED`

---

## Data Models

### User
- `id`
- `username`
- `password_hash`
- `role` (MANAGER / REPORTEE)
- `company_id`
- `manager_id` (for reportees)
- `created_at`
- `updated_at`

### Company
- `id`
- `name`
- `created_at`

### Task
- `id`
- `title`
- `description`
- `status` (DEV / TEST / STUCK / COMPLETED)
- `assigned_to_id`
- `created_by_id`
- `company_id`
- `is_deleted` (soft delete)
- `created_at`
- `updated_at`

---

## Authentication & Authorization

- Authentication is handled using **JWT tokens stored in HTTP-only cookies**
- Tokens contain:
  - `sub` (user ID)
  - `role`
  - `company_id`
- Authorization is enforced using FastAPI dependencies:
  - `require_manager`
  - `require_reportee`

---

## Role-Based Permission Logic

| Action | Manager | Reportee |
|------|--------|---------|
| Create reportee | ✅ | ❌ |
| Create task | ✅ | ❌ |
| Assign task | ✅ | ❌ |
| Update task status | ✅ (any) | ✅ (COMPLETED only) |
| Delete task | ✅ | ❌ |
| View tasks | ✅ | ✅ (assigned only) |

---

## Company-Level Data Isolation

- Every request is scoped using `company_id`
- Users can only access:
  - Tasks created within their company
  - Reportees belonging to their company
- Cross-company access is strictly prevented at the query level

---

## Task Management Rules

- Managers can create tasks (assigned or unassigned)
- Managers can reassign tasks
- Managers can update task status to any value
- Reportees can update task status **only to `COMPLETED`**
- Tasks are soft-deleted using an `is_deleted` flag

---

## Rate Limiting & Abuse Prevention

Rate limiting is implemented using **SlowAPI**.

### Strategy
- **Unauthenticated users:** limited by IP address
- **Authenticated users:** limited by user ID
- Different limits for different APIs

### Configurable Limits
Rate limits are centrally defined in `RATE_LIMITS` configuration and can be adjusted without changing route logic.

Example:
```python
RATE_LIMITS.signup
RATE_LIMITS.login
RATE_LIMITS.task_create
