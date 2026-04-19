from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db
from auth import get_current_user
import schemas

router = APIRouter()


@router.post("/", response_model=schemas.ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(payload: schemas.ProjectCreate, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    email = current_user["EmailAddress"]

    existing = db.execute(
        text("SELECT Name FROM Project WHERE UserEmailAddress = :email AND Name = :name"),
        {"email": email, "name": payload.Name}
    ).fetchone()
    if existing:
        raise HTTPException(status_code=409, detail="A project with this name already exists.")

    db.execute(
        text("INSERT INTO Project (UserEmailAddress, Name, Category) VALUES (:email, :name, :category)"),
        {"email": email, "name": payload.Name, "category": payload.Category}
    )
    db.commit()

    row = db.execute(
        text("SELECT * FROM Project WHERE UserEmailAddress = :email AND Name = :name"),
        {"email": email, "name": payload.Name}
    ).mappings().fetchone()
    return dict(row)


@router.post("/{project_name}/datasets", response_model=schemas.UsageResponse, status_code=status.HTTP_201_CREATED)
def add_dataset_to_project(project_name: str, payload: schemas.UsageCreate, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    email = current_user["EmailAddress"]

    if not db.execute(
        text("SELECT Name FROM Project WHERE UserEmailAddress = :email AND Name = :name"),
        {"email": email, "name": project_name}
    ).fetchone():
        raise HTTPException(status_code=404, detail="Project not found.")

    if not db.execute(
        text("SELECT UUID FROM Dataset WHERE UUID = :uuid"),
        {"uuid": payload.DatasetUUID}
    ).fetchone():
        raise HTTPException(status_code=404, detail="Dataset not found.")

    if db.execute(
        text("""SELECT * FROM ProjectDatasets
                WHERE UserEmailAddress = :email AND ProjectName = :name AND DatasetUUID = :uuid"""),
        {"email": email, "name": project_name, "uuid": payload.DatasetUUID}
    ).fetchone():
        raise HTTPException(status_code=409, detail="Dataset already added to this project.")

    db.execute(
        text("""INSERT INTO ProjectDatasets (UserEmailAddress, ProjectName, DatasetUUID)
                VALUES (:email, :name, :uuid)"""),
        {"email": email, "name": project_name, "uuid": payload.DatasetUUID}
    )
    db.commit()

    row = db.execute(
        text("""SELECT * FROM ProjectDatasets
                WHERE UserEmailAddress = :email AND ProjectName = :name AND DatasetUUID = :uuid"""),
        {"email": email, "name": project_name, "uuid": payload.DatasetUUID}
    ).mappings().fetchone()
    return dict(row)


@router.get("/{project_name}/datasets", response_model=list[schemas.DatasetBrief])
def list_project_datasets(project_name: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    email = current_user["EmailAddress"]

    if not db.execute(
        text("SELECT Name FROM Project WHERE UserEmailAddress = :email AND Name = :name"),
        {"email": email, "name": project_name}
    ).fetchone():
        raise HTTPException(status_code=404, detail="Project not found.")

    rows = db.execute(
        text("""SELECT d.UUID, d.Name, d.Description, d.AccessLevel, d.Category, d.FirstPublished
                FROM Dataset d
                JOIN ProjectDatasets pd ON pd.DatasetUUID = d.UUID
                WHERE pd.UserEmailAddress = :email AND pd.ProjectName = :name"""),
        {"email": email, "name": project_name}
    ).mappings().fetchall()
    return [dict(r) for r in rows]
