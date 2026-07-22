import { useEffect, useMemo, useState } from "react";

const STUDENT_API_URL = "/api/students";
const COURSE_API_URL = "/api/courses";

const EMPTY_STUDENT_FORM = {
    student_id: "",
    name: "",
    email: "",
    program: ""
};

const EMPTY_COURSE_FORM = {
    course_id: "",
    course_name: "",
    credit_points: 6,
    faculty: ""
};


async function readResponse(response) {
    if (response.status === 204) {
        return null;
    }

    const data = await response.json();

    if (!response.ok) {
        throw new Error(
            data.detail || "The request could not be completed."
        );
    }

    return data;
}


function App() {
    const [activeTab, setActiveTab] = useState("students");

    const [students, setStudents] = useState([]);
    const [courses, setCourses] = useState([]);

    const [studentForm, setStudentForm] = useState(
        EMPTY_STUDENT_FORM
    );

    const [courseForm, setCourseForm] = useState(
        EMPTY_COURSE_FORM
    );

    const [editingStudentId, setEditingStudentId] =
        useState(null);

    const [editingCourseId, setEditingCourseId] =
        useState(null);

    const [studentSearch, setStudentSearch] = useState("");
    const [courseSearch, setCourseSearch] = useState("");

    const [loadingStudents, setLoadingStudents] =
        useState(true);

    const [loadingCourses, setLoadingCourses] =
        useState(true);

    const [saving, setSaving] = useState(false);
    const [message, setMessage] = useState("");
    const [error, setError] = useState("");


    const clearNotifications = () => {
        setMessage("");
        setError("");
    };


    const fetchStudents = async () => {
        setLoadingStudents(true);

        try {
            const response = await fetch(STUDENT_API_URL);
            const data = await readResponse(response);
            setStudents(data);
        } catch (requestError) {
            setError(requestError.message);
        } finally {
            setLoadingStudents(false);
        }
    };


    const fetchCourses = async () => {
        setLoadingCourses(true);

        try {
            const response = await fetch(COURSE_API_URL);
            const data = await readResponse(response);
            setCourses(data);
        } catch (requestError) {
            setError(requestError.message);
        } finally {
            setLoadingCourses(false);
        }
    };


    useEffect(() => {
        fetchStudents();
        fetchCourses();
    }, []);


    const filteredStudents = useMemo(() => {
        const searchText = studentSearch.toLowerCase().trim();

        if (!searchText) {
            return students;
        }

        return students.filter((student) =>
            [
                student.student_id,
                student.name,
                student.email,
                student.program
            ].some((value) =>
                value.toLowerCase().includes(searchText)
            )
        );
    }, [students, studentSearch]);


    const filteredCourses = useMemo(() => {
        const searchText = courseSearch.toLowerCase().trim();

        if (!searchText) {
            return courses;
        }

        return courses.filter((course) =>
            [
                course.course_id,
                course.course_name,
                course.faculty,
                String(course.credit_points)
            ].some((value) =>
                value.toLowerCase().includes(searchText)
            )
        );
    }, [courses, courseSearch]);


    const handleStudentSubmit = async (event) => {
        event.preventDefault();

        clearNotifications();
        setSaving(true);

        try {
            const isEditing = Boolean(editingStudentId);

            const url = isEditing
                ? `${STUDENT_API_URL}/${editingStudentId}`
                : STUDENT_API_URL;

            const payload = isEditing
                ? {
                    name: studentForm.name,
                    email: studentForm.email,
                    program: studentForm.program
                }
                : studentForm;

            const response = await fetch(url, {
                method: isEditing ? "PUT" : "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            });

            await readResponse(response);

            setMessage(
                isEditing
                    ? "Student updated successfully."
                    : "Student created successfully."
            );

            resetStudentForm();
            await fetchStudents();
        } catch (requestError) {
            setError(requestError.message);
        } finally {
            setSaving(false);
        }
    };


    const handleCourseSubmit = async (event) => {
        event.preventDefault();

        clearNotifications();
        setSaving(true);

        try {
            const isEditing = Boolean(editingCourseId);

            const url = isEditing
                ? `${COURSE_API_URL}/${editingCourseId}`
                : COURSE_API_URL;

            const payload = {
                ...(isEditing
                    ? {}
                    : { course_id: courseForm.course_id }),
                course_name: courseForm.course_name,
                credit_points: Number(courseForm.credit_points),
                faculty: courseForm.faculty
            };

            const response = await fetch(url, {
                method: isEditing ? "PUT" : "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            });

            await readResponse(response);

            setMessage(
                isEditing
                    ? "Course updated successfully."
                    : "Course created successfully."
            );

            resetCourseForm();
            await fetchCourses();
        } catch (requestError) {
            setError(requestError.message);
        } finally {
            setSaving(false);
        }
    };


    const editStudent = (student) => {
        clearNotifications();

        setEditingStudentId(student.student_id);

        setStudentForm({
            student_id: student.student_id,
            name: student.name,
            email: student.email,
            program: student.program
        });

        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });
    };


    const editCourse = (course) => {
        clearNotifications();

        setEditingCourseId(course.course_id);

        setCourseForm({
            course_id: course.course_id,
            course_name: course.course_name,
            credit_points: course.credit_points,
            faculty: course.faculty
        });

        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });
    };


    const deleteStudent = async (studentId) => {
        const confirmed = window.confirm(
            `Delete student ${studentId}?`
        );

        if (!confirmed) {
            return;
        }

        clearNotifications();

        try {
            const response = await fetch(
                `${STUDENT_API_URL}/${studentId}`,
                {
                    method: "DELETE"
                }
            );

            await readResponse(response);

            setMessage("Student deleted successfully.");
            await fetchStudents();
        } catch (requestError) {
            setError(requestError.message);
        }
    };


    const deleteCourse = async (courseId) => {
        const confirmed = window.confirm(
            `Delete course ${courseId}?`
        );

        if (!confirmed) {
            return;
        }

        clearNotifications();

        try {
            const response = await fetch(
                `${COURSE_API_URL}/${courseId}`,
                {
                    method: "DELETE"
                }
            );

            await readResponse(response);

            setMessage("Course deleted successfully.");
            await fetchCourses();
        } catch (requestError) {
            setError(requestError.message);
        }
    };


    const resetStudentForm = () => {
        setEditingStudentId(null);
        setStudentForm(EMPTY_STUDENT_FORM);
    };


    const resetCourseForm = () => {
        setEditingCourseId(null);
        setCourseForm(EMPTY_COURSE_FORM);
    };


    return (
        <div className="application">
            <header className="header">
                <div>
                    <p className="eyebrow">KoalaTech University</p>

                    <h1>Course Registration Platform</h1>

                    <p className="subtitle">
                        University Administration Dashboard
                    </p>
                </div>

                <div className="environment-badge">
                    Week 04
                </div>
            </header>

            <main className="main-content">
                <section
                    className="summary-grid"
                    aria-label="Application summary"
                >
                    <article className="summary-card">
                        <span>Total Students</span>
                        <strong>{students.length}</strong>
                    </article>

                    <article className="summary-card">
                        <span>Total Courses</span>
                        <strong>{courses.length}</strong>
                    </article>

                    <article className="summary-card">
                        <span>Backend Services</span>
                        <strong>2</strong>
                    </article>
                </section>

                {message && (
                    <div
                        className="notification success"
                        role="status"
                    >
                        {message}
                    </div>
                )}

                {error && (
                    <div
                        className="notification error"
                        role="alert"
                    >
                        {error}
                    </div>
                )}

                <nav
                    className="tabs"
                    aria-label="Administration sections"
                >
                    <button
                        className={
                            activeTab === "students"
                                ? "tab active"
                                : "tab"
                        }
                        onClick={() => {
                            setActiveTab("students");
                            clearNotifications();
                        }}
                    >
                        Students
                    </button>

                    <button
                        className={
                            activeTab === "courses"
                                ? "tab active"
                                : "tab"
                        }
                        onClick={() => {
                            setActiveTab("courses");
                            clearNotifications();
                        }}
                    >
                        Courses
                    </button>
                </nav>

                {activeTab === "students" && (
                    <section className="workspace">
                        <article className="form-card">
                            <div className="section-heading">
                                <div>
                                    <p className="section-label">
                                        Student Management
                                    </p>

                                    <h2>
                                        {editingStudentId
                                            ? "Edit Student"
                                            : "Add Student"}
                                    </h2>
                                </div>
                            </div>

                            <form
                                className="form-grid"
                                onSubmit={handleStudentSubmit}
                            >
                                <label>
                                    Student ID
                                    <input
                                        required
                                        disabled={Boolean(editingStudentId)}
                                        placeholder="S100001"
                                        value={studentForm.student_id}
                                        onChange={(event) =>
                                            setStudentForm({
                                                ...studentForm,
                                                student_id: event.target.value
                                            })
                                        }
                                    />
                                </label>

                                <label>
                                    Name
                                    <input
                                        required
                                        placeholder="Student name"
                                        value={studentForm.name}
                                        onChange={(event) =>
                                            setStudentForm({
                                                ...studentForm,
                                                name: event.target.value
                                            })
                                        }
                                    />
                                </label>

                                <label>
                                    Email
                                    <input
                                        required
                                        type="email"
                                        placeholder="student@university.edu.au"
                                        value={studentForm.email}
                                        onChange={(event) =>
                                            setStudentForm({
                                                ...studentForm,
                                                email: event.target.value
                                            })
                                        }
                                    />
                                </label>

                                <label>
                                    Program
                                    <input
                                        required
                                        placeholder="Master of Information Technology"
                                        value={studentForm.program}
                                        onChange={(event) =>
                                            setStudentForm({
                                                ...studentForm,
                                                program: event.target.value
                                            })
                                        }
                                    />
                                </label>

                                <div className="form-actions">
                                    <button
                                        className="primary-button"
                                        type="submit"
                                        disabled={saving}
                                    >
                                        {saving
                                            ? "Saving..."
                                            : editingStudentId
                                                ? "Update Student"
                                                : "Add Student"}
                                    </button>

                                    {editingStudentId && (
                                        <button
                                            className="secondary-button"
                                            type="button"
                                            onClick={resetStudentForm}
                                        >
                                            Cancel
                                        </button>
                                    )}
                                </div>
                            </form>
                        </article>

                        <article className="table-card">
                            <div className="table-header">
                                <div>
                                    <p className="section-label">
                                        Student Records
                                    </p>

                                    <h2>Students</h2>
                                </div>

                                <input
                                    className="search-input"
                                    aria-label="Search students"
                                    placeholder="Search students..."
                                    value={studentSearch}
                                    onChange={(event) =>
                                        setStudentSearch(event.target.value)
                                    }
                                />
                            </div>

                            {loadingStudents ? (
                                <p className="status-message">
                                    Loading students...
                                </p>
                            ) : filteredStudents.length === 0 ? (
                                <p className="status-message">
                                    No student data found.
                                </p>
                            ) : (
                                <div className="table-wrapper">
                                    <table>
                                        <thead>
                                            <tr>
                                                <th>Student ID</th>
                                                <th>Name</th>
                                                <th>Email</th>
                                                <th>Program</th>
                                                <th>Actions</th>
                                            </tr>
                                        </thead>

                                        <tbody>
                                            {filteredStudents.map((student) => (
                                                <tr key={student.student_id}>
                                                    <td>{student.student_id}</td>
                                                    <td>{student.name}</td>
                                                    <td>{student.email}</td>
                                                    <td>{student.program}</td>

                                                    <td>
                                                        <div className="row-actions">
                                                            <button
                                                                className="edit-button"
                                                                onClick={() =>
                                                                    editStudent(student)
                                                                }
                                                            >
                                                                Edit
                                                            </button>

                                                            <button
                                                                className="delete-button"
                                                                onClick={() =>
                                                                    deleteStudent(
                                                                        student.student_id
                                                                    )
                                                                }
                                                            >
                                                                Delete
                                                            </button>
                                                        </div>
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            )}
                        </article>
                    </section>
                )}

                {activeTab === "courses" && (
                    <section className="workspace">
                        <article className="form-card">
                            <div className="section-heading">
                                <div>
                                    <p className="section-label">
                                        Course Management
                                    </p>

                                    <h2>
                                        {editingCourseId
                                            ? "Edit Course"
                                            : "Add Course"}
                                    </h2>
                                </div>
                            </div>

                            <form
                                className="form-grid"
                                onSubmit={handleCourseSubmit}
                            >
                                <label>
                                    Course ID
                                    <input
                                        required
                                        disabled={Boolean(editingCourseId)}
                                        placeholder="SIT722"
                                        value={courseForm.course_id}
                                        onChange={(event) =>
                                            setCourseForm({
                                                ...courseForm,
                                                course_id: event.target.value
                                            })
                                        }
                                    />
                                </label>

                                <label>
                                    Course Name
                                    <input
                                        required
                                        placeholder="DevOps"
                                        value={courseForm.course_name}
                                        onChange={(event) =>
                                            setCourseForm({
                                                ...courseForm,
                                                course_name: event.target.value
                                            })
                                        }
                                    />
                                </label>

                                <label>
                                    Credit Points
                                    <input
                                        required
                                        min="1"
                                        type="number"
                                        value={courseForm.credit_points}
                                        onChange={(event) =>
                                            setCourseForm({
                                                ...courseForm,
                                                credit_points: event.target.value
                                            })
                                        }
                                    />
                                </label>

                                <label>
                                    Faculty
                                    <input
                                        required
                                        placeholder="School of IT"
                                        value={courseForm.faculty}
                                        onChange={(event) =>
                                            setCourseForm({
                                                ...courseForm,
                                                faculty: event.target.value
                                            })
                                        }
                                    />
                                </label>

                                <div className="form-actions">
                                    <button
                                        className="primary-button"
                                        type="submit"
                                        disabled={saving}
                                    >
                                        {saving
                                            ? "Saving..."
                                            : editingCourseId
                                                ? "Update Course"
                                                : "Add Course"}
                                    </button>

                                    {editingCourseId && (
                                        <button
                                            className="secondary-button"
                                            type="button"
                                            onClick={resetCourseForm}
                                        >
                                            Cancel
                                        </button>
                                    )}
                                </div>
                            </form>
                        </article>

                        <article className="table-card">
                            <div className="table-header">
                                <div>
                                    <p className="section-label">
                                        Course Catalogue
                                    </p>

                                    <h2>Courses</h2>
                                </div>

                                <input
                                    className="search-input"
                                    aria-label="Search courses"
                                    placeholder="Search courses..."
                                    value={courseSearch}
                                    onChange={(event) =>
                                        setCourseSearch(event.target.value)
                                    }
                                />
                            </div>

                            {loadingCourses ? (
                                <p className="status-message">
                                    Loading courses...
                                </p>
                            ) : filteredCourses.length === 0 ? (
                                <p className="status-message">
                                    No course data found.
                                </p>
                            ) : (
                                <div className="table-wrapper">
                                    <table>
                                        <thead>
                                            <tr>
                                                <th>Course ID</th>
                                                <th>Course Name</th>
                                                <th>Credit Points</th>
                                                <th>Faculty</th>
                                                <th>Actions</th>
                                            </tr>
                                        </thead>

                                        <tbody>
                                            {filteredCourses.map((course) => (
                                                <tr key={course.course_id}>
                                                    <td>{course.course_id}</td>
                                                    <td>{course.course_name}</td>
                                                    <td>{course.credit_points}</td>
                                                    <td>{course.faculty}</td>

                                                    <td>
                                                        <div className="row-actions">
                                                            <button
                                                                className="edit-button"
                                                                onClick={() =>
                                                                    editCourse(course)
                                                                }
                                                            >
                                                                Edit
                                                            </button>

                                                            <button
                                                                className="delete-button"
                                                                onClick={() =>
                                                                    deleteCourse(
                                                                        course.course_id
                                                                    )
                                                                }
                                                            >
                                                                Delete
                                                            </button>
                                                        </div>
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            )}
                        </article>
                    </section>
                )}
            </main>
        </div>
    );
}

export default App;