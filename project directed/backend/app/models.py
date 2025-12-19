import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Integer, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True) # UUID string or simple ID
    username = Column(String, unique=True, index=True)
    user_type = Column(String) # 'student', 'jobseeker', 'developer'
    created_at = Column(DateTime, default=datetime.utcnow)

    goals = relationship("Goal", back_populates="owner", cascade="all, delete-orphan")
    logs = relationship("Log", back_populates="owner", cascade="all, delete-orphan")


class Goal(Base):
    __tablename__ = "goals"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, index=True) # 과목명, 기업명, 프로젝트명
    description = Column(String, nullable=True)
    user_id = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Progress stats could be computed or stored
    progress = Column(Integer, default=0) 

    owner = relationship("User", back_populates="goals")
    todos = relationship("Todo", back_populates="goal", cascade="all, delete-orphan")


class Todo(Base):
    __tablename__ = "todos"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    text = Column(String, index=True)
    done = Column(Boolean, default=False)
    important = Column(Boolean, default=False)
    
    # For Developer type: Difficulty, Energy, Time? (Optional for now, store in JSON if needed or add columns)
    meta_info = Column(JSON, default={}) 

    goal_id = Column(String, ForeignKey("goals.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    goal = relationship("Goal", back_populates="todos")


class Log(Base):
    __tablename__ = "logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    content = Column(Text) # 감정 기록, 실패 사유, 메모
    log_type = Column(String) # 'daily', 'error', 'retrospective'
    user_id = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="logs")


class Problem(Base):
    __tablename__ = "problems"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    text = Column(Text)
    options = Column(JSON, default=[]) # 객관식 선지
    answer = Column(String, nullable=True)
    explain = Column(Text, nullable=True)
    source = Column(String, nullable=True) # 파일명 등
    tags = Column(JSON, default=[])
    important = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # User linkage could be added if multi-user problem management is needed
    # For now, keep it global as per MVP legacy behavior or attach to a default user
