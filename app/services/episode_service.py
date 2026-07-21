from typing import List, Optional

from app.database.database import get_session
from app.database.models import Episode


class EpisodeService:

    @staticmethod
    def create(data: dict) -> Episode:
        session = get_session()
        try:
            ep = Episode(**data)
            session.add(ep)
            session.commit()
            session.refresh(ep)
            return ep
        finally:
            session.close()

    @staticmethod
    def get_by_project(project_id: int) -> List[Episode]:
        session = get_session()
        try:
            return (
                session.query(Episode)
                .filter(Episode.project_id == project_id)
                .order_by(Episode.start_ep)
                .all()
            )
        finally:
            session.close()

    @staticmethod
    def get_by_id(episode_id: int) -> Optional[Episode]:
        session = get_session()
        try:
            return session.query(Episode).filter(Episode.id == episode_id).first()
        finally:
            session.close()

    @staticmethod
    def update(episode_id: int, data: dict) -> Optional[Episode]:
        session = get_session()
        try:
            ep = session.query(Episode).filter(Episode.id == episode_id).first()
            if not ep:
                return None
            for key, value in data.items():
                if hasattr(ep, key):
                    setattr(ep, key, value)
            session.commit()
            session.refresh(ep)
            return ep
        finally:
            session.close()

    @staticmethod
    def delete(episode_id: int) -> bool:
        session = get_session()
        try:
            ep = session.query(Episode).filter(Episode.id == episode_id).first()
            if not ep:
                return False
            session.delete(ep)
            session.commit()
            return True
        finally:
            session.close()

    @staticmethod
    def batch_create(project_id: int, assignments: list[dict]) -> List[Episode]:
        """批量创建分集分配记录"""
        session = get_session()
        try:
            episodes = []
            for item in assignments:
                ep = Episode(project_id=project_id, **item)
                session.add(ep)
                episodes.append(ep)
            session.commit()
            for ep in episodes:
                session.refresh(ep)
            return episodes
        finally:
            session.close()

    @staticmethod
    def merge_by_editor(episodes: list) -> list[dict]:
        """按剪辑师合并集数范围，返回 [{editor_name, ranges: '3-8,38-45', total_eps: 5}]"""
        grouped: dict[str, list[tuple[int, int]]] = {}
        for ep in episodes:
            grouped.setdefault(ep.editor_name, []).append((ep.start_ep, ep.end_ep))
        result = []
        for name, segs in grouped.items():
            segs.sort()
            parts: list[str] = []
            total = 0
            for s, e in segs:
                parts.append(str(s) if s == e else f"{s}-{e}")
                total += e - s + 1
            result.append({"editor_name": name, "ranges": ", ".join(parts), "total_eps": total})
        return result

    @staticmethod
    def get_by_project_and_editor(project_id: int, editor_name: str) -> list:
        session = get_session()
        try:
            return (
                session.query(Episode)
                .filter(Episode.project_id == project_id, Episode.editor_name == editor_name)
                .order_by(Episode.start_ep)
                .all()
            )
        finally:
            session.close()

    @staticmethod
    def delete_by_editor(project_id: int, editor_name: str):
        session = get_session()
        try:
            session.query(Episode).filter(
                Episode.project_id == project_id, Episode.editor_name == editor_name
            ).delete()
            session.commit()
        finally:
            session.close()

    @staticmethod
    def delete_by_project(project_id: int):
        """删除项目下所有分集"""
        session = get_session()
        try:
            session.query(Episode).filter(Episode.project_id == project_id).delete()
            session.commit()
        finally:
            session.close()
