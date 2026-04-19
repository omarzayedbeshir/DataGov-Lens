from fastapi import APIRouter, Depends, HTTPException, Query
from pymysql.connections import Connection
from typing import Optional

from database import get_db
import schemas

router = APIRouter()


# ── Dataset detail ─────────────────────────────────────────────────────────────

@router.get("/{uuid}", response_model=schemas.DatasetDetail)
def get_dataset(uuid: str, conn: Connection = Depends(get_db)):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM Dataset WHERE UUID = %s", (uuid,))
        ds = cur.fetchone()
        if not ds:
            raise HTTPException(status_code=404, detail="Dataset not found.")

        cur.execute("SELECT Tag FROM DatasetTags WHERE DatasetUUID = %s", (uuid,))
        ds["tags"] = [r["Tag"] for r in cur.fetchall()]

        cur.execute("SELECT Topic FROM DatasetTopics WHERE DatasetUUID = %s", (uuid,))
        ds["topics"] = [r["Topic"] for r in cur.fetchall()]

        cur.execute("SELECT Link, Format FROM File WHERE DatasetUUID = %s", (uuid,))
        ds["files"] = cur.fetchall()

    return ds


# ── List datasets with optional filters ───────────────────────────────────────

@router.get("/", response_model=list[schemas.DatasetBrief])
def list_datasets(
    org_type: Optional[str] = Query(None),
    format:   Optional[str] = Query(None),
    tag:      Optional[str] = Query(None),
    limit:    int           = Query(50, le=200),
    offset:   int           = Query(0),
    conn: Connection = Depends(get_db),
):
    # Build query dynamically based on active filters
    joins  = ""
    wheres = []
    params = []

    if org_type:
        joins += " JOIN Publisher p ON p.EmailAddress = d.PublisherEmailAddress"
        wheres.append("p.OrganizationType LIKE %s")
        params.append(f"%{org_type}%")

    if format:
        joins += " JOIN File f ON f.DatasetUUID = d.UUID"
        wheres.append("f.Format LIKE %s")
        params.append(f"%{format}%")

    if tag:
        joins += " JOIN DatasetTags dt ON dt.DatasetUUID = d.UUID"
        wheres.append("dt.Tag LIKE %s")
        params.append(f"%{tag}%")

    where_clause = ("WHERE " + " AND ".join(wheres)) if wheres else ""
    params += [limit, offset]

    query = f"""
        SELECT DISTINCT d.UUID, d.Name, d.Description, d.AccessLevel, d.Category, d.FirstPublished
        FROM Dataset d
        {joins}
        {where_clause}
        LIMIT %s OFFSET %s
    """

    with conn.cursor() as cur:
        cur.execute(query, params)
        return cur.fetchall()
