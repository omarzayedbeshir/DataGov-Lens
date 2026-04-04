# DataGov API — Milestone III Backend

FastAPI backend for the CSCE 2501 Data.gov project.

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure your database
cp .env.example .env
# Edit .env with your remote MySQL credentials (e.g. db4free.net)

# 3. Run the server
uvicorn main:app --reload
```

The interactive API docs will be available at **http://localhost:8000/docs**

---

## Endpoints

### Users `/users`
| Method | Path | Description |
|--------|------|-------------|
| POST | `/users/register` | Register a new user |
| GET | `/users/{email}` | Get user profile |
| GET | `/users/{email}/projects` | List user's projects |
| GET | `/users/{email}/usage` | View all dataset usages by user |

### Projects `/projects`
| Method | Path | Description |
|--------|------|-------------|
| POST | `/projects/{email}` | Create a new project |
| POST | `/projects/{email}/{project_name}/datasets` | Add dataset usage to project |
| GET | `/projects/{email}/{project_name}/datasets` | List datasets in project |

### Datasets `/datasets`
| Method | Path | Description |
|--------|------|-------------|
| GET | `/datasets/` | List datasets (filter by `org_type`, `format`, `tag`) |
| GET | `/datasets/{uuid}` | Get full dataset detail |

### Statistics `/stats`
| Method | Path | Description |
|--------|------|-------------|
| GET | `/stats/top-organizations` | Top 5 orgs by dataset count |
| GET | `/stats/datasets-by-organization` | Dataset count per organization |
| GET | `/stats/datasets-by-topic` | Dataset count per topic |
| GET | `/stats/datasets-by-format` | Dataset count per file format |
| GET | `/stats/datasets-by-org-type` | Dataset count per org type |
| GET | `/stats/top-datasets-by-users` | Top 5 datasets by distinct user count |
| GET | `/stats/usage-by-project-type` | Usage distribution by project category |
| GET | `/stats/top-tags-by-project-type` | Top 10 tags per project category |
