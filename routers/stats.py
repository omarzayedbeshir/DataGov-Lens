from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db
import schemas

router = APIRouter()


@router.get("/top-organizations", response_model=list[schemas.CountItem])
def top_organizations(db: Session = Depends(get_db)):
    rows = db.execute(text("""
        SELECT p.Name AS label, COUNT(d.UUID) AS count
        FROM Publisher p
        JOIN Dataset d ON d.PublisherEmailAddress = p.EmailAddress
        GROUP BY p.EmailAddress
        ORDER BY count DESC
        LIMIT 5
    """)).mappings().fetchall()
    return [dict(r) for r in rows]


@router.get("/datasets-by-organization", response_model=list[schemas.CountItem])
def datasets_by_organization(db: Session = Depends(get_db)):
    rows = db.execute(text("""
        SELECT p.Name AS label, COUNT(d.UUID) AS count
        FROM Publisher p
        JOIN Dataset d ON d.PublisherEmailAddress = p.EmailAddress
        GROUP BY p.EmailAddress
        ORDER BY count DESC
    """)).mappings().fetchall()
    return [dict(r) for r in rows]


@router.get("/datasets-by-topic", response_model=list[schemas.CountItem])
def datasets_by_topic(db: Session = Depends(get_db)):
    rows = db.execute(text("""
        SELECT Topic AS label, COUNT(DISTINCT DatasetUUID) AS count
        FROM DatasetTopics
        GROUP BY Topic
        ORDER BY count DESC
    """)).mappings().fetchall()
    return [dict(r) for r in rows]


@router.get("/datasets-by-format", response_model=list[schemas.CountItem])
def datasets_by_format(db: Session = Depends(get_db)):
    rows = db.execute(text("""
        SELECT Format AS label, COUNT(DISTINCT DatasetUUID) AS count
        FROM File
        GROUP BY Format
        ORDER BY count DESC
    """)).mappings().fetchall()
    return [dict(r) for r in rows]


@router.get("/datasets-by-org-type", response_model=list[schemas.CountItem])
def datasets_by_org_type(db: Session = Depends(get_db)):
    rows = db.execute(text("""
        SELECT COALESCE(p.OrganizationType, 'Unknown') AS label, COUNT(d.UUID) AS count
        FROM Publisher p
        JOIN Dataset d ON d.PublisherEmailAddress = p.EmailAddress
        GROUP BY p.OrganizationType
        ORDER BY count DESC
    """)).mappings().fetchall()
    return [dict(r) for r in rows]


@router.get("/top-datasets-by-users", response_model=list[schemas.TopDataset])
def top_datasets_by_users(db: Session = Depends(get_db)):
    rows = db.execute(text("""
        SELECT d.UUID, d.Name, COUNT(DISTINCT pd.UserEmailAddress) AS user_count
        FROM Dataset d
        JOIN ProjectDatasets pd ON pd.DatasetUUID = d.UUID
        GROUP BY d.UUID
        ORDER BY user_count DESC
        LIMIT 5
    """)).mappings().fetchall()
    return [dict(r) for r in rows]


@router.get("/usage-by-project-type", response_model=list[schemas.ProjectTypeUsage])
def usage_by_project_type(db: Session = Depends(get_db)):
    rows = db.execute(text("""
        SELECT p.Category AS category, COUNT(pd.DatasetUUID) AS usage_count
        FROM Project p
        JOIN ProjectDatasets pd
          ON pd.UserEmailAddress = p.UserEmailAddress AND pd.ProjectName = p.Name
        GROUP BY p.Category
        ORDER BY usage_count DESC
    """)).mappings().fetchall()
    return [dict(r) for r in rows]


@router.get("/top-tags-by-project-type", response_model=list[schemas.TagByProjectType])
def top_tags_by_project_type(db: Session = Depends(get_db)):
    rows = db.execute(text("""
        SELECT category, tag, tag_count
        FROM (
            SELECT
                p.Category        AS category,
                dt.Tag            AS tag,
                COUNT(dt.Tag)     AS tag_count,
                RANK() OVER (
                    PARTITION BY p.Category
                    ORDER BY COUNT(dt.Tag) DESC
                ) AS rnk
            FROM Project p
            JOIN ProjectDatasets pd
              ON pd.UserEmailAddress = p.UserEmailAddress AND pd.ProjectName = p.Name
            JOIN DatasetTags dt ON dt.DatasetUUID = pd.DatasetUUID
            GROUP BY p.Category, dt.Tag
        ) ranked
        WHERE rnk <= 10
        ORDER BY category, tag_count DESC
    """)).mappings().fetchall()
    return [dict(r) for r in rows]
