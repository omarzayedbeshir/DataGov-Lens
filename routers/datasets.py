from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional

from database import get_db
import schemas

router = APIRouter()


@router.get("/{uuid}", response_model=schemas.DatasetDetail)
def get_dataset(uuid: str, db: Session = Depends(get_db)):
    row = db.execute(
        text("SELECT * FROM Dataset WHERE UUID = :uuid"),
        {"uuid": uuid}
    ).mappings().fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    ds = dict(row)

    ds["tags"] = [r[0] for r in db.execute(
        text("SELECT Tag FROM DatasetTags WHERE DatasetUUID = :uuid"), {"uuid": uuid}
    ).fetchall()]

    ds["topics"] = [r[0] for r in db.execute(
        text("SELECT Topic FROM DatasetTopics WHERE DatasetUUID = :uuid"), {"uuid": uuid}
    ).fetchall()]

    ds["files"] = [dict(r) for r in db.execute(
        text("SELECT Link, Format FROM File WHERE DatasetUUID = :uuid"), {"uuid": uuid}
    ).mappings().fetchall()]

    return ds


@router.get("/", response_model=list[schemas.DatasetBrief])
def list_datasets(
    org_type: Optional[str] = Query(None),
    format:   Optional[str] = Query(None),
    tag:      Optional[str] = Query(None),
    limit:    int           = Query(50, le=200),
    offset:   int           = Query(0),
    db: Session = Depends(get_db),
):
    joins  = ""
    wheres = []
    params = {"limit": limit, "offset": offset}

    if org_type:
        joins += " JOIN Publisher p ON p.EmailAddress = d.PublisherEmailAddress"
        wheres.append("p.OrganizationType LIKE :org_type")
        params["org_type"] = f"%{org_type}%"

    if format:
        joins += " JOIN File f ON f.DatasetUUID = d.UUID"
        wheres.append("f.Format LIKE :format")
        params["format"] = f"%{format}%"

    if tag:
        joins += " JOIN DatasetTags dt ON dt.DatasetUUID = d.UUID"
        wheres.append("dt.Tag LIKE :tag")
        params["tag"] = f"%{tag}%"

    where_clause = ("WHERE " + " AND ".join(wheres)) if wheres else ""

    query = text(f"""
        SELECT DISTINCT d.UUID, d.Name, d.Description, d.AccessLevel, d.Category, d.FirstPublished
        FROM Dataset d
        {joins}
        {where_clause}
        LIMIT :limit OFFSET :offset
    """)

    rows = db.execute(query, params).mappings().fetchall()
    return [dict(r) for r in rows]
