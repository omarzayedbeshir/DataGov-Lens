# DataGov API — Milestone III Backend

FastAPI backend for the CSCE 2501 Data.gov project.

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure your database
cp .env.example .env
# Edit .env with your remote MySQL credentials (DATABASE_URL)
# Also set a strong SECRET_KEY for JWT signing:
# python -c "import secrets; print(secrets.token_hex(32))"

# 3. Run the server
uvicorn main:app --reload
```

Interactive API docs available at **http://localhost:8000/docs**

---

## Project Structure

```
datagov_api/
├── main.py               # App entry point, router registration
├── database.py           # SQLAlchemy engine + get_db() dependency
├── models.py             # ORM models (mirrors MySQL schema)
├── schemas.py            # Pydantic request/response models
├── auth.py               # JWT creation, password hashing, token blacklist
├── requirements.txt
├── .env.example
└── routers/
    ├── auth_router.py    # Login, logout, /me
    ├── users.py          # Register, profile, usage history
    ├── projects.py       # Create project, add dataset usage
    ├── datasets.py       # Browse and filter datasets
    └── stats.py          # Aggregation and statistics queries
```

---

## Authentication

The API uses **JWT Bearer tokens**.

| Step | Method | Endpoint | Notes |
|------|--------|----------|-------|
| Register | POST | `/users/register` | Public — no token needed |
| Login | POST | `/auth/login` | Send email as `username` + `password` as form data. Returns a Bearer token. |
| Use token | — | — | Add `Authorization: Bearer <token>` header to protected requests |
| Who am I | GET | `/auth/me` | Returns current user's profile |
| Logout | POST | `/auth/logout` | Blacklists the token server-side |

> Passwords are stored as **bcrypt hashes**. Tokens expire after **24 hours**.

---

## Endpoints

### Auth `/auth`
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/auth/login` | ❌ | Login and receive a Bearer token |
| POST | `/auth/logout` | ✅ | Invalidate the current token |
| GET | `/auth/me` | ✅ | Get the logged-in user's profile |

### Users `/users`
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/users/register` | ❌ | Register a new user |
| GET | `/users/me/profile` | ✅ | Get your profile |
| GET | `/users/me/projects` | ✅ | List your projects |
| GET | `/users/me/usage` | ✅ | View all your dataset usages |

### Projects `/projects`
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/projects/` | ✅ | Create a new project |
| POST | `/projects/{project_name}/datasets` | ✅ | Add a dataset to a project |
| GET | `/projects/{project_name}/datasets` | ✅ | List datasets in a project |

### Datasets `/datasets`
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/datasets/` | ❌ | List datasets (filter by `org_type`, `format`, `tag`) |
| GET | `/datasets/{uuid}` | ❌ | Get full dataset detail |

### Statistics `/stats`
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/stats/top-organizations` | ❌ | Top 5 publishers by dataset count |
| GET | `/stats/datasets-by-organization` | ❌ | Dataset count per organization |
| GET | `/stats/datasets-by-topic` | ❌ | Dataset count per topic |
| GET | `/stats/datasets-by-format` | ❌ | Dataset count per file format |
| GET | `/stats/datasets-by-org-type` | ❌ | Dataset count per organization type |
| GET | `/stats/top-datasets-by-users` | ❌ | Top 5 datasets by distinct user count |
| GET | `/stats/usage-by-project-type` | ❌ | Usage distribution by project category |
| GET | `/stats/top-tags-by-project-type` | ❌ | Top 10 tags per project category |
