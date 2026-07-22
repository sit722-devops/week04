import asyncio
import logging
from contextlib import asynccontextmanager
import os


from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

from app.db import Base, engine, get_db
from app.models import Course
from app.schemas import CourseCreate, CourseResponse, CourseUpdate


FRONTEND_ORIGIN = os.getenv(
    "FRONTEND_ORIGIN",
    "http://localhost:5173"
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger("course-service")

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
    title="Course Service",
    description=(
        "Week 04 Course Service with FastAPI, PostgreSQL, "
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
        "message": "Welcome to Course Service",
        "service": "course-service",
        "week": "week-04"
    }


@app.get("/health")
def health_check():
    logger.info("Health endpoint accessed.")

    return {
        "status": "healthy",
        "service": "course-service"
    }


@app.get(
    "/courses",
    response_model=list[CourseResponse]
)
def get_courses(db: Session = Depends(get_db)):
    logger.info("Retrieving all courses.")

    return db.query(Course).order_by(Course.course_id).all()


@app.get(
    "/courses/{course_id}",
    response_model=CourseResponse
)
def get_course(
    course_id: str,
    db: Session = Depends(get_db)
):
    logger.info(
        "Retrieving course with ID: %s",
        course_id
    )

    course = db.query(Course).filter(
        Course.course_id == course_id
    ).first()

    if course is None:
        logger.warning(
            "Course not found: %s",
            course_id
        )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    return course


@app.post(
    "/courses",
    response_model=CourseResponse,
    status_code=status.HTTP_201_CREATED
)
def create_course(
    course: CourseCreate,
    db: Session = Depends(get_db)
):
    logger.info(
        "Creating course with ID: %s",
        course.course_id
    )

    existing_course = db.query(Course).filter(
        Course.course_id == course.course_id
    ).first()

    if existing_course:
        logger.warning(
            "Duplicate course ID attempted: %s",
            course.course_id
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course ID already exists"
        )

    new_course = Course(
        course_id=course.course_id,
        course_name=course.course_name,
        credit_points=course.credit_points,
        faculty=course.faculty
    )

    try:
        db.add(new_course)
        db.commit()
        db.refresh(new_course)

    except IntegrityError:
        db.rollback()

        logger.exception(
            "Database integrity error while creating course: %s",
            course.course_id
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to create course"
        )

    logger.info(
        "Course created successfully: %s",
        course.course_id
    )

    return new_course


@app.put(
    "/courses/{course_id}",
    response_model=CourseResponse
)
def update_course(
    course_id: str,
    course_update: CourseUpdate,
    db: Session = Depends(get_db)
):
    logger.info(
        "Updating course with ID: %s",
        course_id
    )

    course = db.query(Course).filter(
        Course.course_id == course_id
    ).first()

    if course is None:
        logger.warning(
            "Course not found for update: %s",
            course_id
        )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    course.course_name = course_update.course_name
    course.credit_points = course_update.credit_points
    course.faculty = course_update.faculty

    try:
        db.commit()
        db.refresh(course)

    except IntegrityError:
        db.rollback()

        logger.exception(
            "Database integrity error while updating course: %s",
            course_id
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to update course"
        )

    logger.info(
        "Course updated successfully: %s",
        course_id
    )

    return course


@app.delete(
    "/courses/{course_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_course(
    course_id: str,
    db: Session = Depends(get_db)
):
    logger.info(
        "Deleting course with ID: %s",
        course_id
    )

    course = db.query(Course).filter(
        Course.course_id == course_id
    ).first()

    if course is None:
        logger.warning(
            "Course not found for deletion: %s",
            course_id
        )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    db.delete(course)
    db.commit()

    logger.info(
        "Course deleted successfully: %s",
        course_id
    )

    return None