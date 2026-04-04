from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import date


# ── User ──────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    EmailAddress: EmailStr
    Username: str
    Password: str
    Country: str
    Gender: str
    Birthdate: date

    @field_validator("Gender")
    @classmethod
    def gender_valid(cls, v):
        allowed = {"male", "female", "other", "prefer not to say"}
        if v.lower() not in allowed:
            raise ValueError(f"Gender must be one of: {allowed}")
        return v


class UserResponse(BaseModel):
    EmailAddress: str
    Username: str
    Country: str
    Gender: str
    Birthdate: date

    model_config = {"from_attributes": True}


# ── Project ───────────────────────────────────────────────────────────────────

class ProjectCreate(BaseModel):
    Name: str
    Category: str

    @field_validator("Category")
    @classmethod
    def category_valid(cls, v):
        allowed = {"analytics", "machine learning", "field research"}
        if v.lower() not in allowed:
            raise ValueError(f"Category must be one of: {allowed}")
        return v.lower()


class ProjectResponse(BaseModel):
    UserEmailAddress: str
    Name: str
    Category: Optional[str]

    model_config = {"from_attributes": True}


# ── Dataset Usage ─────────────────────────────────────────────────────────────

class UsageCreate(BaseModel):
    DatasetUUID: str


class UsageResponse(BaseModel):
    UserEmailAddress: str
    ProjectName: str
    DatasetUUID: str

    model_config = {"from_attributes": True}


# ── Dataset ───────────────────────────────────────────────────────────────────

class DatasetBrief(BaseModel):
    UUID: str
    Name: str
    Description: Optional[str]
    AccessLevel: Optional[str]
    Category: Optional[str]
    FirstPublished: Optional[date]

    model_config = {"from_attributes": True}


class FileOut(BaseModel):
    Link: str
    Format: str

    model_config = {"from_attributes": True}


class DatasetDetail(BaseModel):
    UUID: str
    Name: str
    Description: Optional[str]
    AccessLevel: Optional[str]
    Category: Optional[str]
    License: Optional[str]
    HomepageURL: Optional[str]
    FirstPublished: Optional[date]
    LastModified: Optional[date]
    MetadataCreationDate: Optional[date]
    MetadataUpdateDate: Optional[date]
    ProgramCode: Optional[str]
    BureauCode: Optional[str]
    PublisherEmailAddress: Optional[str]
    MaintainerEmailAddress: Optional[str]
    tags: list[str] = []
    topics: list[str] = []
    files: list[FileOut] = []

    model_config = {"from_attributes": True}


# ── Stats ─────────────────────────────────────────────────────────────────────

class CountItem(BaseModel):
    label: str
    count: int


class TopDataset(BaseModel):
    UUID: str
    Name: str
    user_count: int


class ProjectTypeUsage(BaseModel):
    category: str
    usage_count: int


class TagByProjectType(BaseModel):
    category: str
    tag: str
    tag_count: int
