from .database import Base
from sqlalchemy import Column, DateTime, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    logo = Column(String)
    # documents = Column(ARRAY(String))
    owner_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    # this is relation betwen User and project
    owner = relationship("User", back_populates="project_created")


"""
    team_members = relationship(
        "User",
        secondary="user_project_association",
        back_populates="projects_worked_on",
    )
"""


# CASCADE ALL
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    date_of_birth = Column(DateTime)
    project_created = relationship(
        "Project",
        back_populates="owner",
        cascade="all, delete-orphan",
        foreign_keys="[Project.owner_id]",
    )
    """
    projects_worked_on = relationship(
        "Project", secondary="user_project_association", back_populates="team_members"
    )
    """


class UserProjectAssociation(Base):
    __tablename__ = "user_project_association"

    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    project_id = Column(
        Integer, ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True
    )


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)  # for storing url or s3 key
    project_id = Column(
        Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
