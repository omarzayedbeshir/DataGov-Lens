from fastapi import APIRouter, Depends, HTTPException, status
from pymysql.connections import Connection

from database import get_db
from auth import get_current_user
import schemas

router = APIRouter()


# ── Create project ────────────────────────────────────────────────────────────

@router.post("/", response_model=schemas.ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: schemas.ProjectCreate,
    current_user: dict = Depends(get_current_user),
    conn: Connection = Depends(get_db),
):
    email = current_user["EmailAddress"]
    with conn.cursor() as cur:
        cur.execute(
            "SELECT Name FROM Project WHERE UserEmailAddress = %s AND Name = %s",
            (email, payload.Name)
        )
        if cur.fetchone():
            raise HTTPException(status_code=409, detail="A project with this name already exists.")

        cur.execute(
            "INSERT INTO Project (UserEmailAddress, Name, Category) VALUES (%s, %s, %s)",
            (email, payload.Name, payload.Category)
        )
        conn.commit()

        cur.execute(
            "SELECT * FROM Project WHERE UserEmailAddress = %s AND Name = %s",
            (email, payload.Name)
        )
        return cur.fetchone()


# ── Add dataset to project ─────────────────────────────────────────────────────

@router.post("/{project_name}/datasets", response_model=schemas.UsageResponse, status_code=status.HTTP_201_CREATED)
def add_dataset_to_project(
    project_name: str,
    payload: schemas.UsageCreate,
    current_user: dict = Depends(get_current_user),
    conn: Connection = Depends(get_db),
):
    email = current_user["EmailAddress"]
    with conn.cursor() as cur:
        cur.execute(
            "SELECT Name FROM Project WHERE UserEmailAddress = %s AND Name = %s",
            (email, project_name)
        )
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Project not found.")

        cur.execute("SELECT UUID FROM Dataset WHERE UUID = %s", (payload.DatasetUUID,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Dataset not found.")

        cur.execute(
            """SELECT * FROM ProjectDatasets
               WHERE UserEmailAddress = %s AND ProjectName = %s AND DatasetUUID = %s""",
            (email, project_name, payload.DatasetUUID)
        )
        if cur.fetchone():
            raise HTTPException(status_code=409, detail="Dataset already added to this project.")

        cur.execute(
            """INSERT INTO ProjectDatasets (UserEmailAddress, ProjectName, DatasetUUID)
               VALUES (%s, %s, %s)""",
            (email, project_name, payload.DatasetUUID)
        )
        conn.commit()

        cur.execute(
            """SELECT * FROM ProjectDatasets
               WHERE UserEmailAddress = %s AND ProjectName = %s AND DatasetUUID = %s""",
            (email, project_name, payload.DatasetUUID)
        )
        return cur.fetchone()


# ── List datasets in a project ─────────────────────────────────────────────────

@router.get("/{project_name}/datasets", response_model=list[schemas.DatasetBrief])
def list_project_datasets(
    project_name: str,
    current_user: dict = Depends(get_current_user),
    conn: Connection = Depends(get_db),
):
    email = current_user["EmailAddress"]
    with conn.cursor() as cur:
        cur.execute(
            "SELECT Name FROM Project WHERE UserEmailAddress = %s AND Name = %s",
            (email, project_name)
        )
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Project not found.")

        cur.execute(
            """SELECT d.UUID, d.Name, d.Description, d.AccessLevel, d.Category, d.FirstPublished
               FROM Dataset d
               JOIN ProjectDatasets pd ON pd.DatasetUUID = d.UUID
               WHERE pd.UserEmailAddress = %s AND pd.ProjectName = %s""",
            (email, project_name)
        )
        return cur.fetchall()
