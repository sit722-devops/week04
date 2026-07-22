from pydantic import BaseModel, ConfigDict, Field


class CourseCreate(BaseModel):
    course_id: str
    course_name: str
    credit_points: int = Field(gt=0)
    faculty: str


class CourseUpdate(BaseModel):
    course_name: str
    credit_points: int = Field(gt=0)
    faculty: str


class CourseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    course_id: str
    course_name: str
    credit_points: int
    faculty: str