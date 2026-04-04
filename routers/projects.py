from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from auth import get_current_user
import models, schemas

router = APIRouter()


# ── Create project ────────────────────────────────────────────────────────────

@router.post("/", response_model=schemas.ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: schemas.ProjectCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new project for the logged-in user."""
    existing = db.get(models.Project, (current_user.EmailAddress, payload.Name))
    if existing:
        raise HTTPException(status_code=409, detail="A project with this name already exists.")

    project = models.Project(
        UserEmailAddress=current_user.EmailAddress,
        Name=payload.Name,
        Category=payload.Category,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


# ── Add dataset to project ─────────────────────────────────────────────────────

@router.post("/{project_name}/datasets", response_model=schemas.UsageResponse, status_code=status.HTTP_201_CREATED)
def add_dataset_to_project(
    project_name: str,
    payload: schemas.UsageCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a dataset usage entry to one of the logged-in user's projects."""
    project = db.get(models.Project, (current_user.EmailAddress, project_name))
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    dataset = db.get(models.Dataset, payload.DatasetUUID)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    existing = db.get(models.ProjectDatasets, (current_user.EmailAddress, project_name, payload.DatasetUUID))
    if existing:
        raise HTTPException(status_code=409, detail="Dataset already added to this project.")

    usage = models.ProjectDatasets(
        UserEmailAddress=current_user.EmailAddress,
        ProjectName=project_name,
        DatasetUUID=payload.DatasetUUID,
    )
    db.add(usage)
    db.commit()
    db.refresh(usage)
    return usage


# ── List datasets in a project ─────────────────────────────────────────────────

@router.get("/{project_name}/datasets", response_model=list[schemas.DatasetBrief])
def list_project_datasets(
    project_name: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all datasets used in one of the logged-in user's projects."""
    project = db.get(models.Project, (current_user.EmailAddress, project_name))
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    return (
        db.query(models.Dataset)
        .join(models.ProjectDatasets, models.ProjectDatasets.DatasetUUID == models.Dataset.UUID)
        .filter(
            models.ProjectDatasets.UserEmailAddress == current_user.EmailAddress,
            models.ProjectDatasets.ProjectName == project_name,
        )
        .all()
    )
