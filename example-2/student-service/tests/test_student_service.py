from fastapi.testclient import TestClient

from app.db import Base, SessionLocal, engine
from app.main import app
from app.models import Student

Base.metadata.create_all(bind=engine)

client = TestClient(app)


def delete_test_student(student_id: str):
    db = SessionLocal()

    try:
        db.query(Student).filter(
            Student.student_id == student_id
        ).delete()

        db.commit()

    finally:
        db.close()


def create_test_student(
    student_id: str,
    name: str = "Test Student",
    email: str = "test.student@campus.edu.au",
    program: str = "Master of Information Technology"
):
    delete_test_student(student_id)

    student_data = {
        "student_id": student_id,
        "name": name,
        "email": email,
        "program": program
    }

    return client.post(
        "/students",
        json=student_data
    )


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["service"] == "student-service"
    assert response.json()["week"] == "week-04"


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_get_all_students():
    response = client.get("/students")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_student():
    test_student_id = "TEST-S100001"

    delete_test_student(test_student_id)

    student_data = {
        "student_id": test_student_id,
        "name": "John Smith",
        "email": "test.s100001@campus.edu.au",
        "program": "Master of Information Technology"
    }

    response = client.post(
        "/students",
        json=student_data
    )

    assert response.status_code == 201
    assert response.json()["student_id"] == test_student_id
    assert response.json()["name"] == "John Smith"
    assert response.json()["email"] == "test.s100001@campus.edu.au"

    delete_test_student(test_student_id)


def test_create_student_duplicate_id():
    test_student_id = "TEST-S100002"

    delete_test_student(test_student_id)

    first_student = {
        "student_id": test_student_id,
        "name": "Emma Brown",
        "email": "test.s100002@campus.edu.au",
        "program": "Master of Cyber Security"
    }

    duplicate_student = {
        "student_id": test_student_id,
        "name": "Duplicate Student",
        "email": "duplicate.s100002@campus.edu.au",
        "program": "Master of Data Science"
    }

    first_response = client.post(
        "/students",
        json=first_student
    )

    assert first_response.status_code == 201

    response = client.post(
        "/students",
        json=duplicate_student
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student ID already exists"

    delete_test_student(test_student_id)


def test_create_student_duplicate_email():
    first_student_id = "TEST-S100003"
    second_student_id = "TEST-S100004"
    test_email = "duplicate.email@campus.edu.au"

    delete_test_student(first_student_id)
    delete_test_student(second_student_id)

    first_student = {
        "student_id": first_student_id,
        "name": "First Student",
        "email": test_email,
        "program": "Master of Information Technology"
    }

    second_student = {
        "student_id": second_student_id,
        "name": "Second Student",
        "email": test_email,
        "program": "Master of Cyber Security"
    }

    first_response = client.post(
        "/students",
        json=first_student
    )

    assert first_response.status_code == 201

    response = client.post(
        "/students",
        json=second_student
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student email already exists"

    delete_test_student(first_student_id)
    delete_test_student(second_student_id)


def test_get_student_by_id():
    test_student_id = "TEST-S100005"

    response = create_test_student(
        student_id=test_student_id,
        name="Liam Wilson",
        email="test.s100005@campus.edu.au",
        program="Master of Data Science"
    )

    assert response.status_code == 201

    response = client.get(
        f"/students/{test_student_id}"
    )

    assert response.status_code == 200
    assert response.json()["student_id"] == test_student_id
    assert response.json()["name"] == "Liam Wilson"

    delete_test_student(test_student_id)


def test_get_student_not_found():
    test_student_id = "TEST-S999999"

    delete_test_student(test_student_id)

    response = client.get(
        f"/students/{test_student_id}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student not found"


def test_update_student():
    test_student_id = "TEST-S100006"

    response = create_test_student(
        student_id=test_student_id,
        name="Original Name",
        email="test.s100006@campus.edu.au",
        program="Master of Information Technology"
    )

    assert response.status_code == 201

    updated_student = {
        "name": "Updated Name",
        "email": "updated.s100006@campus.edu.au",
        "program": "Master of Cyber Security"
    }

    response = client.put(
        f"/students/{test_student_id}",
        json=updated_student
    )

    assert response.status_code == 200
    assert response.json()["student_id"] == test_student_id
    assert response.json()["name"] == "Updated Name"
    assert response.json()["email"] == "updated.s100006@campus.edu.au"
    assert response.json()["program"] == "Master of Cyber Security"

    delete_test_student(test_student_id)


def test_update_student_not_found():
    test_student_id = "TEST-S999998"

    delete_test_student(test_student_id)

    updated_student = {
        "name": "Updated Name",
        "email": "missing.student@campus.edu.au",
        "program": "Master of Information Technology"
    }

    response = client.put(
        f"/students/{test_student_id}",
        json=updated_student
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student not found"


def test_delete_student():
    test_student_id = "TEST-S100007"

    response = create_test_student(
        student_id=test_student_id,
        name="Student To Delete",
        email="test.s100007@campus.edu.au",
        program="Master of Software Engineering"
    )

    assert response.status_code == 201

    response = client.delete(
        f"/students/{test_student_id}"
    )

    assert response.status_code == 204

    response = client.get(
        f"/students/{test_student_id}"
    )

    assert response.status_code == 404

    delete_test_student(test_student_id)


def test_delete_student_not_found():
    test_student_id = "TEST-S999997"

    delete_test_student(test_student_id)

    response = client.delete(
        f"/students/{test_student_id}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student not found"