from sqlalchemy import Column, String, Text, Date, CHAR, ForeignKey, ForeignKeyConstraint
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "User"

    EmailAddress = Column(String(200), primary_key=True)
    Username = Column(String(20), nullable=False)
    Password = Column(String(200), nullable=False)
    Country = Column(String(50), nullable=False)
    Gender = Column(CHAR(10), nullable=False)
    Birthdate = Column(Date, nullable=False)

    projects = relationship("Project", back_populates="user", cascade="all, delete")


class Publisher(Base):
    __tablename__ = "Publisher"

    EmailAddress = Column(String(200), primary_key=True)
    Name = Column(String(250))
    Description = Column(Text)
    OrganizationType = Column(String(100))

    datasets = relationship("Dataset", back_populates="publisher")


class Maintainer(Base):
    __tablename__ = "Maintainer"

    EmailAddress = Column(String(200), primary_key=True)
    Name = Column(String(250), nullable=False)

    datasets = relationship("Dataset", back_populates="maintainer")


class Dataset(Base):
    __tablename__ = "Dataset"

    UUID = Column(CHAR(36), primary_key=True)
    Identifier = Column(String(200))
    Name = Column(String(500), nullable=False)
    Description = Column(Text)
    Category = Column(String(500))
    BureauCode = Column(String(50))
    FirstPublished = Column(Date)
    SourceHash = Column(String(64))
    LastModified = Column(Date)
    MetadataCatalogID = Column(String(200))
    SourceSchemaVersion = Column(String(10))
    CatalogDescribedby = Column(String(200))
    HarvestObjectID = Column(String(200))
    HarvestSourceID = Column(String(200))
    AccessLevel = Column(String(50))
    MetadataSource = Column(String(500))
    License = Column(String(500))
    SchemaVersion = Column(String(200))
    HomepageURL = Column(String(500))
    MetadataCreationDate = Column(Date)
    HarvestSourceTitle = Column(String(200))
    HarvestSourceLink = Column(String(500))
    MetadataUpdateDate = Column(Date)
    SourceDatajsonIdentifier = Column(String(500))
    ProgramCode = Column(String(100))
    MetadataContext = Column(String(500))
    MaintainerEmailAddress = Column(String(200), ForeignKey("Maintainer.EmailAddress", ondelete="SET NULL", onupdate="CASCADE"))
    PublisherEmailAddress = Column(String(200), ForeignKey("Publisher.EmailAddress", ondelete="SET NULL", onupdate="CASCADE"))

    maintainer = relationship("Maintainer", back_populates="datasets")
    publisher = relationship("Publisher", back_populates="datasets")
    tags = relationship("DatasetTags", back_populates="dataset", cascade="all, delete")
    topics = relationship("DatasetTopics", back_populates="dataset", cascade="all, delete")
    files = relationship("File", back_populates="dataset", cascade="all, delete")
    project_datasets = relationship("ProjectDatasets", back_populates="dataset", cascade="all, delete")


class DatasetTags(Base):
    __tablename__ = "DatasetTags"

    DatasetUUID = Column(CHAR(36), ForeignKey("Dataset.UUID", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    Tag = Column(String(100), primary_key=True)

    dataset = relationship("Dataset", back_populates="tags")


class DatasetTopics(Base):
    __tablename__ = "DatasetTopics"

    DatasetUUID = Column(CHAR(36), ForeignKey("Dataset.UUID", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    Topic = Column(String(200), primary_key=True)

    dataset = relationship("Dataset", back_populates="topics")


class File(Base):
    __tablename__ = "File"

    Link = Column(String(650), primary_key=True)
    DatasetUUID = Column(CHAR(36), ForeignKey("Dataset.UUID", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    Format = Column(String(100), nullable=False)

    dataset = relationship("Dataset", back_populates="files")


class Project(Base):
    __tablename__ = "Project"

    UserEmailAddress = Column(String(200), ForeignKey("User.EmailAddress", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    Name = Column(String(200), primary_key=True)
    Category = Column(String(100))

    user = relationship("User", back_populates="projects")
    project_datasets = relationship("ProjectDatasets", back_populates="project", cascade="all, delete")


class ProjectDatasets(Base):
    __tablename__ = "ProjectDatasets"

    UserEmailAddress = Column(String(200), primary_key=True)
    ProjectName = Column(String(200), primary_key=True)
    DatasetUUID = Column(CHAR(36), ForeignKey("Dataset.UUID", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)

    __table_args__ = (
        ForeignKeyConstraint(
            ["UserEmailAddress", "ProjectName"],
            ["Project.UserEmailAddress", "Project.Name"],
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
    )

    project = relationship("Project", back_populates="project_datasets")
    dataset = relationship("Dataset", back_populates="project_datasets")
