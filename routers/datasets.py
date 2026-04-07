from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import Optional

from database import get_db
import models, schemas

router = APIRouter()


# ── Dataset detail ─────────────────────────────────────────────────────────────

@router.get("/{uuid}", response_model=schemas.DatasetDetail)
def get_dataset(uuid: str, db: Session = Depends(get_db)):
    """Get full details for a single dataset."""
    dataset = (
        db.query(models.Dataset)
        .options(
            joinedload(models.Dataset.tags),
            joinedload(models.Dataset.topics),
            joinedload(models.Dataset.files),
        )
        .filter(models.Dataset.UUID == uuid)
        .first()
    )
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    result = schemas.DatasetDetail.model_validate({
        **dataset.__dict__,
        "tags":   [t.Tag for t in dataset.tags],
        "topics": [t.Topic for t in dataset.topics],
        "files":  [{"Link": f.Link, "Format": f.Format} for f in dataset.files],
    })
    return result

# ── List datasets with optional filters ───────────────────────────────────────

@router.get("/", response_model=list[schemas.DatasetBrief])
def list_datasets(
    org_type: Optional[str] = Query(None, description="Filter by publisher organization type"),
    format: Optional[str] = Query(None, description="Filter by file format (e.g. CSV, JSON)"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    db: Session = Depends(get_db),
):
    """
    List datasets with optional filters:
    - **org_type**: organization type (federal, state, city, …)
    - **format**: file format (CSV, JSON, …)
    - **tag**: dataset tag keyword
    """
    query = db.query(models.Dataset)

    if org_type:
        query = (
            query.join(models.Publisher, models.Dataset.PublisherEmailAddress == models.Publisher.EmailAddress)
            .filter(models.Publisher.OrganizationType.ilike(f"%{org_type}%"))
        )

    if format:
        query = (
            query.join(models.File, models.File.DatasetUUID == models.Dataset.UUID)
            .filter(models.File.Format.ilike(f"%{format}%"))
        )

    if tag:
        query = (
            query.join(models.DatasetTags, models.DatasetTags.DatasetUUID == models.Dataset.UUID)
            .filter(models.DatasetTags.Tag.ilike(f"%{tag}%"))
        )

    return query.offset(offset).limit(limit).all()
