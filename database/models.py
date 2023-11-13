from sqlalchemy import Column, Integer, String, Date, UUID, Text
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base

PostgresBase = declarative_base()
MysqlBase = declarative_base()


class MindUsers(PostgresBase):
    # __tablename__ = 'mind_users'
    __tablename__ = 'mindtickle_users'
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String(255), nullable=False)
    active_status = Column(String(10), nullable=False)


class LessonCompletion(MysqlBase):
    __tablename__ = 'lesson_completion'
    completion_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    lesson_id = Column(Integer, nullable=False)
    completion_date = Column(Date, nullable=False)


class ReportsGenerated(PostgresBase):
    __tablename__ = 'reports_generated'
    report_id = Column(UUID, primary_key=True)
    s3_object_key = Column(String(255), nullable=False)
    s3_bucket = Column(String(255), nullable=False)
    report_date = Column(Date, nullable=False)
    report_type = Column(String(255), nullable=False)
    download_link = Column(Text, nullable=False)
