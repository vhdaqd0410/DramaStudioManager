from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_no = Column(String, comment="项目编号")
    name = Column(String, nullable=False, comment="项目名称")
    status = Column(String, default="待开始", comment="项目状态")
    start_date = Column(String, comment="开始时间")
    delivery_date = Column(String, comment="交付时间")
    local_path = Column(String, comment="本地项目路径")
    nas_path = Column(String, comment="NAS项目路径")
    notes = Column(String, comment="备注")
    created_at = Column(DateTime, default=datetime.now)

    episodes = relationship("Episode", back_populates="project", cascade="all, delete-orphan")


class Episode(Base):
    __tablename__ = "episodes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    editor_name = Column(String, nullable=False, comment="剪辑师名字")
    start_ep = Column(Integer, nullable=False, comment="起始集号")
    end_ep = Column(Integer, nullable=False, comment="结束集号")
    notes = Column(String, comment="备注")

    project = relationship("Project", back_populates="episodes")
