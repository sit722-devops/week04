from pydantic import BaseModel, ConfigDict, EmailStr


class StudentCreate(BaseModel):
    student_id: str
    name: str
    email: EmailStr
    program: str


class StudentUpdate(BaseModel):
    name: str
    email: EmailStr
    program: str


class StudentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    student_id: str
    name: str
    email: EmailStr
    program: str