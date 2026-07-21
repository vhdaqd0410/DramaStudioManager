from typing import List, Optional

from app.database.database import get_session
from app.database.models import Project


class ProjectService:

    @staticmethod
    def create(data: dict) -> Project:
        session = get_session()
        try:
            project = Project(**data)
            session.add(project)
            session.commit()
            session.refresh(project)
            return project
        finally:
            session.close()

    @staticmethod
    def get_all(keyword: str = "") -> List[Project]:
        session = get_session()
        try:
            query = session.query(Project)
            if keyword:
                kw = f"%{keyword}%"
                query = query.filter(
                    (Project.name.like(kw)) |
                    (Project.project_no.like(kw)) |
                    (Project.status.like(kw))
                )
            return query.order_by(Project.created_at.desc()).all()
        finally:
            session.close()

    @staticmethod
    def get_by_id(project_id: int) -> Optional[Project]:
        session = get_session()
        try:
            return session.query(Project).filter(Project.id == project_id).first()
        finally:
            session.close()

    @staticmethod
    def update(project_id: int, data: dict) -> Optional[Project]:
        session = get_session()
        try:
            project = session.query(Project).filter(Project.id == project_id).first()
            if not project:
                return None
            for key, value in data.items():
                if hasattr(project, key):
                    setattr(project, key, value)
            session.commit()
            session.refresh(project)
            return project
        finally:
            session.close()

    @staticmethod
    def delete(project_id: int) -> bool:
        session = get_session()
        try:
            project = session.query(Project).filter(Project.id == project_id).first()
            if not project:
                return False
            session.delete(project)
            session.commit()
            return True
        finally:
            session.close()
