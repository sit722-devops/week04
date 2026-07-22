import asyncio
import logging
from contextlib import asynccontextmanager
import os

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

from app.db import Base, engine, get_db
from app.models import Student
from app.schemas import StudentCreate, StudentResponse, StudentUpdate

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger("student-service")

FRONTEND_ORIGIN = os.getenv(
    "FRONTEND_ORIGIN",
    "http://localhost:5173"
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    max_retries = 10
    retry_delay_seconds = 5

    for attempt in range(1, max_retries + 1):
        try:
            logger.info(
                f"Connecting to PostgreSQL and creating tables "
                f"(attempt {attempt}/{max_retries})..."
            )

            with engine.begin() as connection:
                Base.metadata.create_all(bind=connection)

            logger.info("PostgreSQL connection successful. Tables are ready.")
            break

        except OperationalError as error:
            logger.warning(f"PostgreSQL connection failed: {error}")

            if attempt == max_retries:
                logger.critical("PostgreSQL connection failed after all retries.")
                raise RuntimeError("Database startup failed") from error

            logger.info(f"Retrying in {retry_delay_seconds} seconds...")
            await asyncio.sleep(retry_delay_seconds)

        except Exception:
            logger.critical(
                "Unexpected error during database startup",
                exc_info=True
            )
            raise

    yield


app = FastAPI(
    title="Student Service",
    description=(
        "Week 04 Student Service with FastAPI, PostgreSQL, "
        "Docker and full CRUD operations"
    ),
    version="4.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/")
def root():
    logger.info("Root endpoint accessed.")

    return {
        "message": "Welcome to Student Service",
        "service": "student-service",
        "week": "week-04"
    }


@app.get("/health")
def health_check():
    logger.info("Health endpoint accessed.")

    return {
        "status": "healthy",
        "service": "student-service"
    }


@app.get(
    "/students",
    response_model=list[StudentResponse]
)
def get_students(db: Session = Depends(get_db)):
    logger.info("Retrieving all students.")

    return db.query(Student).order_by(Student.student_id).all()


@app.get(
    "/students/{student_id}",
    response_model=StudentResponse
)
def get_student(
    student_id: str,
    db: Session = Depends(get_db)
):
    logger.info(
        "Retrieving student with ID: %s",
        student_id
    )

    student = db.query(Student).filter(
        Student.student_id == student_id
    ).first()

    if student is None:
        logger.warning(
            "Student not found: %s",
            student_id
        )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    return student


@app.post(
    "/students",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED
)
def create_student(
    student: StudentCreate,
    db: Session = Depends(get_db)
):
    logger.info(
        "Creating student with ID: %s",
        student.student_id
    )

    existing_student = db.query(Student).filter(
        Student.student_id == student.student_id
    ).first()

    if existing_student:
        logger.warning(
            "Duplicate student ID attempted: %s",
            student.student_id
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student ID already exists"
        )

    existing_email = db.query(Student).filter(
        Student.email == student.email
    ).first()

    if existing_email:
        logger.warning(
            "Duplicate student email attempted: %s",
            student.email
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student email already exists"
        )

    new_student = Student(
        student_id=student.student_id,
        name=student.name,
        email=student.email,
        program=student.program
    )

    try:
        db.add(new_student)
        db.commit()
        db.refresh(new_student)

    except IntegrityError:
        db.rollback()

        logger.exception(
            "Database integrity error while creating student: %s",
            student.student_id
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to create student"
        )

    logger.info(
        "Student created successfully: %s",
        student.student_id
    )

    return new_student


@app.put(
    "/students/{student_id}",
    response_model=StudentResponse
)
def update_student(
    student_id: str,
    student_update: StudentUpdate,
    db: Session = Depends(get_db)
):
    logger.info(
        "Updating student with ID: %s",
        student_id
    )

    student = db.query(Student).filter(
        Student.student_id == student_id
    ).first()

    if student is None:
        logger.warning(
            "Student not found for update: %s",
            student_id
        )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    existing_email = db.query(Student).filter(
        Student.email == student_update.email,
        Student.student_id != student_id
    ).first()

    if existing_email:
        logger.warning(
            "Duplicate email attempted during student update: %s",
            student_update.email
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student email already exists"
        )

    student.name = student_update.name
    student.email = student_update.email
    student.program = student_update.program

    try:
        db.commit()
        db.refresh(student)

    except IntegrityError:
        db.rollback()

        logger.exception(
            "Database integrity error while updating student: %s",
            student_id
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to update student"
        )

    logger.info(
        "Student updated successfully: %s",
        student_id
    )

    return student


@app.delete(
    "/students/{student_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_student(
    student_id: str,
    db: Session = Depends(get_db)
):
    logger.info(
        "Deleting student with ID: %s",
        student_id
    )

    student = db.query(Student).filter(
        Student.student_id == student_id
    ).first()

    if student is None:
        logger.warning(
            "Student not found for deletion: %s",
            student_id
        )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    db.delete(student)
    db.commit()

    logger.info(
        "Student deleted successfully: %s",
        student_id
    )

    return None