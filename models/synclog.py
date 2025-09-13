# models/sync_log.py
from sqlalchemy import Column, Integer, DateTime
from models.base import Base
import datetime


class SyncLog(Base):
    __tablename__ = "sync_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
