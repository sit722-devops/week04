from sqlalchemy import Column, Integer, String

from app.db import Base


class Course(Base):
    __tablename__ = "courses"

    course_id = Column(String, primary_key=True, index=True)
    course_name = Column(String, nullable=False)
    credit_points = Column(Integer, nullable=False)
    faculty = Column(String, nullable=False)
