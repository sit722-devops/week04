from fastapi.testclient import TestClient

from app.db import Base, SessionLocal, engine
from app.main import app
from app.models import Course

Base.metadata.create_all(bind=engine)

client = TestClient(app)


def delete_test_course(course_id: str):
    db = SessionLocal()

    try:
        db.query(Course).filter(
            Course.course_id == course_id
        ).delete()

        db.commit()

    finally:
        db.close()


def create_test_course(
    course_id: str,
    course_name: str = "Test Course",
    credit_points: int = 6,
    faculty: str = "School of IT"
):
    delete_test_course(course_id)

    course_data = {
        "course_id": course_id,
        "course_name": course_name,
        "credit_points": credit_points,
        "faculty": faculty
    }

    return client.post(
        "/courses",
        json=course_data
    )


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["service"] == "course-service"
    assert response.json()["week"] == "week-04"


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_get_all_courses():
    response = client.get("/courses")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_course():
    test_course_id = "TEST-SIT701"

    delete_test_course(test_course_id)

    course_data = {
        "course_id": test_course_id,
        "course_name": "Cloud Computing",
        "credit_points": 6,
        "faculty": "School of IT"
    }

    response = client.post(
        "/courses",
        json=course_data
    )

    assert response.status_code == 201
    assert response.json()["course_id"] == test_course_id
    assert response.json()["course_name"] == "Cloud Computing"
    assert response.json()["credit_points"] == 6

    delete_test_course(test_course_id)


def test_create_course_duplicate_id():
    test_course_id = "TEST-SIT702"

    delete_test_course(test_course_id)

    first_course = {
        "course_id": test_course_id,
        "course_name": "Software Engineering",
        "credit_points": 6,
        "faculty": "School of IT"
    }

    duplicate_course = {
        "course_id": test_course_id,
        "course_name": "Duplicate Course",
        "credit_points": 12,
        "faculty": "School of Engineering"
    }

    first_response = client.post(
        "/courses",
        json=first_course
    )

    assert first_response.status_code == 201

    response = client.post(
        "/courses",
        json=duplicate_course
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Course ID already exists"

    delete_test_course(test_course_id)


def test_create_course_invalid_credit_points():
    test_course_id = "TEST-SIT703"

    delete_test_course(test_course_id)

    invalid_course = {
        "course_id": test_course_id,
        "course_name": "Invalid Course",
        "credit_points": 0,
        "faculty": "School of IT"
    }

    response = client.post(
        "/courses",
        json=invalid_course
    )

    assert response.status_code == 422

    delete_test_course(test_course_id)


def test_get_course_by_id():
    test_course_id = "TEST-SIT704"

    response = create_test_course(
        course_id=test_course_id,
        course_name="DevOps",
        credit_points=6,
        faculty="School of IT"
    )

    assert response.status_code == 201

    response = client.get(
        f"/courses/{test_course_id}"
    )

    assert response.status_code == 200
    assert response.json()["course_id"] == test_course_id
    assert response.json()["course_name"] == "DevOps"

    delete_test_course(test_course_id)


def test_get_course_not_found():
    test_course_id = "TEST-SIT999"

    delete_test_course(test_course_id)

    response = client.get(
        f"/courses/{test_course_id}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Course not found"


def test_update_course():
    test_course_id = "TEST-SIT705"

    response = create_test_course(
        course_id=test_course_id,
        course_name="Original Course",
        credit_points=6,
        faculty="School of IT"
    )

    assert response.status_code == 201

    updated_course = {
        "course_name": "Updated Course",
        "credit_points": 12,
        "faculty": "School of Engineering"
    }

    response = client.put(
        f"/courses/{test_course_id}",
        json=updated_course
    )

    assert response.status_code == 200
    assert response.json()["course_id"] == test_course_id
    assert response.json()["course_name"] == "Updated Course"
    assert response.json()["credit_points"] == 12
    assert response.json()["faculty"] == "School of Engineering"

    delete_test_course(test_course_id)


def test_update_course_not_found():
    test_course_id = "TEST-SIT998"

    delete_test_course(test_course_id)

    updated_course = {
        "course_name": "Updated Course",
        "credit_points": 6,
        "faculty": "School of IT"
    }

    response = client.put(
        f"/courses/{test_course_id}",
        json=updated_course
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Course not found"


def test_update_course_invalid_credit_points():
    test_course_id = "TEST-SIT706"

    response = create_test_course(
        course_id=test_course_id,
        course_name="Valid Course",
        credit_points=6,
        faculty="School of IT"
    )

    assert response.status_code == 201

    updated_course = {
        "course_name": "Invalid Updated Course",
        "credit_points": 0,
        "faculty": "School of IT"
    }

    response = client.put(
        f"/courses/{test_course_id}",
        json=updated_course
    )

    assert response.status_code == 422

    delete_test_course(test_course_id)


def test_delete_course():
    test_course_id = "TEST-SIT707"

    response = create_test_course(
        course_id=test_course_id,
        course_name="Course To Delete",
        credit_points=6,
        faculty="School of IT"
    )

    assert response.status_code == 201

    response = client.delete(
        f"/courses/{test_course_id}"
    )

    assert response.status_code == 204

    response = client.get(
        f"/courses/{test_course_id}"
    )

    assert response.status_code == 404

    delete_test_course(test_course_id)


def test_delete_course_not_found():
    test_course_id = "TEST-SIT997"

    delete_test_course(test_course_id)

    response = client.delete(
        f"/courses/{test_course_id}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Course not found"