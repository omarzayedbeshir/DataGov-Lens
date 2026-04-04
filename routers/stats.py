from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct

from database import get_db
import models, schemas

router = APIRouter()


# ── Top 5 contributing organizations ──────────────────────────────────────────

@router.get("/top-organizations", response_model=list[schemas.CountItem])
def top_organizations(db: Session = Depends(get_db)):
    """Top 5 publishers by number of datasets contributed."""
    rows = (
        db.query(models.Publisher.Name, func.count(models.Dataset.UUID).label("cnt"))
        .join(models.Dataset, models.Dataset.PublisherEmailAddress == models.Publisher.EmailAddress)
        .group_by(models.Publisher.EmailAddress)
        .order_by(func.count(models.Dataset.UUID).desc())
        .limit(5)
        .all()
    )
    return [schemas.CountItem(label=r.Name or "Unknown", count=r.cnt) for r in rows]


# ── Total datasets by organization ────────────────────────────────────────────

@router.get("/datasets-by-organization", response_model=list[schemas.CountItem])
def datasets_by_organization(db: Session = Depends(get_db)):
    """Total number of datasets contributed per organization (publisher)."""
    rows = (
        db.query(models.Publisher.Name, func.count(models.Dataset.UUID).label("cnt"))
        .join(models.Dataset, models.Dataset.PublisherEmailAddress == models.Publisher.EmailAddress)
        .group_by(models.Publisher.EmailAddress)
        .order_by(func.count(models.Dataset.UUID).desc())
        .all()
    )
    return [schemas.CountItem(label=r.Name or "Unknown", count=r.cnt) for r in rows]


# ── Total datasets by topic ───────────────────────────────────────────────────

@router.get("/datasets-by-topic", response_model=list[schemas.CountItem])
def datasets_by_topic(db: Session = Depends(get_db)):
    """Total number of datasets per topic."""
    rows = (
        db.query(models.DatasetTopics.Topic, func.count(distinct(models.DatasetTopics.DatasetUUID)).label("cnt"))
        .group_by(models.DatasetTopics.Topic)
        .order_by(func.count(distinct(models.DatasetTopics.DatasetUUID)).desc())
        .all()
    )
    return [schemas.CountItem(label=r.Topic, count=r.cnt) for r in rows]


# ── Total datasets by format ──────────────────────────────────────────────────

@router.get("/datasets-by-format", response_model=list[schemas.CountItem])
def datasets_by_format(db: Session = Depends(get_db)):
    """Total number of datasets per file format."""
    rows = (
        db.query(models.File.Format, func.count(distinct(models.File.DatasetUUID)).label("cnt"))
        .group_by(models.File.Format)
        .order_by(func.count(distinct(models.File.DatasetUUID)).desc())
        .all()
    )
    return [schemas.CountItem(label=r.Format, count=r.cnt) for r in rows]


# ── Total datasets by organization type ───────────────────────────────────────

@router.get("/datasets-by-org-type", response_model=list[schemas.CountItem])
def datasets_by_org_type(db: Session = Depends(get_db)):
    """Total number of datasets per organization type (federal, state, city, …)."""
    rows = (
        db.query(models.Publisher.OrganizationType, func.count(models.Dataset.UUID).label("cnt"))
        .join(models.Dataset, models.Dataset.PublisherEmailAddress == models.Publisher.EmailAddress)
        .group_by(models.Publisher.OrganizationType)
        .order_by(func.count(models.Dataset.UUID).desc())
        .all()
    )
    return [schemas.CountItem(label=r.OrganizationType or "Unknown", count=r.cnt) for r in rows]


# ── Top 5 datasets by number of users ─────────────────────────────────────────

@router.get("/top-datasets-by-users", response_model=list[schemas.TopDataset])
def top_datasets_by_users(db: Session = Depends(get_db)):
    """Top 5 datasets ranked by number of distinct users using them."""
    rows = (
        db.query(
            models.Dataset.UUID,
            models.Dataset.Name,
            func.count(distinct(models.ProjectDatasets.UserEmailAddress)).label("user_count"),
        )
        .join(models.ProjectDatasets, models.ProjectDatasets.DatasetUUID == models.Dataset.UUID)
        .group_by(models.Dataset.UUID)
        .order_by(func.count(distinct(models.ProjectDatasets.UserEmailAddress)).desc())
        .limit(5)
        .all()
    )
    return [schemas.TopDataset(UUID=r.UUID, Name=r.Name, user_count=r.user_count) for r in rows]


# ── Dataset usage distribution by project type ────────────────────────────────

@router.get("/usage-by-project-type", response_model=list[schemas.ProjectTypeUsage])
def usage_by_project_type(db: Session = Depends(get_db)):
    """Distribution of dataset usages across project categories."""
    rows = (
        db.query(models.Project.Category, func.count(models.ProjectDatasets.DatasetUUID).label("cnt"))
        .join(
            models.ProjectDatasets,
            (models.ProjectDatasets.UserEmailAddress == models.Project.UserEmailAddress)
            & (models.ProjectDatasets.ProjectName == models.Project.Name),
        )
        .group_by(models.Project.Category)
        .order_by(func.count(models.ProjectDatasets.DatasetUUID).desc())
        .all()
    )
    return [schemas.ProjectTypeUsage(category=r.Category or "Unknown", usage_count=r.cnt) for r in rows]


# ── Top 10 tags per project type ──────────────────────────────────────────────

@router.get("/top-tags-by-project-type", response_model=list[schemas.TagByProjectType])
def top_tags_by_project_type(db: Session = Depends(get_db)):
    """Top 10 tags associated with datasets used under each project type."""
    rows = (
        db.query(
            models.Project.Category,
            models.DatasetTags.Tag,
            func.count(models.DatasetTags.Tag).label("tag_count"),
        )
        .join(
            models.ProjectDatasets,
            (models.ProjectDatasets.UserEmailAddress == models.Project.UserEmailAddress)
            & (models.ProjectDatasets.ProjectName == models.Project.Name),
        )
        .join(models.DatasetTags, models.DatasetTags.DatasetUUID == models.ProjectDatasets.DatasetUUID)
        .group_by(models.Project.Category, models.DatasetTags.Tag)
        .order_by(models.Project.Category, func.count(models.DatasetTags.Tag).desc())
        .all()
    )

    # Keep only top 10 per category
    from collections import defaultdict
    category_counts: dict = defaultdict(list)
    for r in rows:
        category_counts[r.Category].append(
            schemas.TagByProjectType(category=r.Category or "Unknown", tag=r.Tag, tag_count=r.tag_count)
        )

    result = []
    for cat_items in category_counts.values():
        result.extend(cat_items[:10])

    return result
