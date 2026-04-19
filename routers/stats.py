from fastapi import APIRouter, Depends
from pymysql.connections import Connection

from database import get_db
import schemas

router = APIRouter()


# ── Top 5 contributing organizations ──────────────────────────────────────────

@router.get("/top-organizations", response_model=list[schemas.CountItem])
def top_organizations(conn: Connection = Depends(get_db)):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT p.Name AS label, COUNT(d.UUID) AS count
            FROM Publisher p
            JOIN Dataset d ON d.PublisherEmailAddress = p.EmailAddress
            GROUP BY p.EmailAddress
            ORDER BY count DESC
            LIMIT 5
        """)
        return cur.fetchall()


# ── Total datasets by organization ────────────────────────────────────────────

@router.get("/datasets-by-organization", response_model=list[schemas.CountItem])
def datasets_by_organization(conn: Connection = Depends(get_db)):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT p.Name AS label, COUNT(d.UUID) AS count
            FROM Publisher p
            JOIN Dataset d ON d.PublisherEmailAddress = p.EmailAddress
            GROUP BY p.EmailAddress
            ORDER BY count DESC
        """)
        return cur.fetchall()


# ── Total datasets by topic ───────────────────────────────────────────────────

@router.get("/datasets-by-topic", response_model=list[schemas.CountItem])
def datasets_by_topic(conn: Connection = Depends(get_db)):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT Topic AS label, COUNT(DISTINCT DatasetUUID) AS count
            FROM DatasetTopics
            GROUP BY Topic
            ORDER BY count DESC
        """)
        return cur.fetchall()


# ── Total datasets by format ──────────────────────────────────────────────────

@router.get("/datasets-by-format", response_model=list[schemas.CountItem])
def datasets_by_format(conn: Connection = Depends(get_db)):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT Format AS label, COUNT(DISTINCT DatasetUUID) AS count
            FROM File
            GROUP BY Format
            ORDER BY count DESC
        """)
        return cur.fetchall()


# ── Total datasets by organization type ───────────────────────────────────────

@router.get("/datasets-by-org-type", response_model=list[schemas.CountItem])
def datasets_by_org_type(conn: Connection = Depends(get_db)):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT COALESCE(p.OrganizationType, 'Unknown') AS label, COUNT(d.UUID) AS count
            FROM Publisher p
            JOIN Dataset d ON d.PublisherEmailAddress = p.EmailAddress
            GROUP BY p.OrganizationType
            ORDER BY count DESC
        """)
        return cur.fetchall()


# ── Top 5 datasets by number of users ─────────────────────────────────────────

@router.get("/top-datasets-by-users", response_model=list[schemas.TopDataset])
def top_datasets_by_users(conn: Connection = Depends(get_db)):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT d.UUID, d.Name, COUNT(DISTINCT pd.UserEmailAddress) AS user_count
            FROM Dataset d
            JOIN ProjectDatasets pd ON pd.DatasetUUID = d.UUID
            GROUP BY d.UUID
            ORDER BY user_count DESC
            LIMIT 5
        """)
        return cur.fetchall()


# ── Dataset usage distribution by project type ────────────────────────────────

@router.get("/usage-by-project-type", response_model=list[schemas.ProjectTypeUsage])
def usage_by_project_type(conn: Connection = Depends(get_db)):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT p.Category AS category, COUNT(pd.DatasetUUID) AS usage_count
            FROM Project p
            JOIN ProjectDatasets pd
              ON pd.UserEmailAddress = p.UserEmailAddress AND pd.ProjectName = p.Name
            GROUP BY p.Category
            ORDER BY usage_count DESC
        """)
        return cur.fetchall()


# ── Top 10 tags per project type ──────────────────────────────────────────────

@router.get("/top-tags-by-project-type", response_model=list[schemas.TagByProjectType])
def top_tags_by_project_type(conn: Connection = Depends(get_db)):
    with conn.cursor() as cur:
        # Rank tags within each category and keep top 10
        cur.execute("""
            SELECT category, tag, tag_count
            FROM (
                SELECT
                    p.Category                  AS category,
                    dt.Tag                      AS tag,
                    COUNT(dt.Tag)               AS tag_count,
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
        """)
        return cur.fetchall()
