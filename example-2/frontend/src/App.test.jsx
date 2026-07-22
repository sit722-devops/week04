import {
    fireEvent,
    render,
    screen,
    waitFor
} from "@testing-library/react";

import {
    beforeEach,
    describe,
    expect,
    test,
    vi
} from "vitest";

import App from "./App";


const mockJsonResponse = (data, status = 200) =>
    Promise.resolve({
        ok: status >= 200 && status < 300,
        status,
        json: () => Promise.resolve(data)
    });


describe("Course Registration Platform", () => {
    beforeEach(() => {
        global.fetch = vi.fn((url) => {
            if (url.includes("/api/students")) {
                return mockJsonResponse([]);
            }

            if (url.includes("/api/courses")) {
                return mockJsonResponse([]);
            }

            return mockJsonResponse([]);
        });

        window.scrollTo = vi.fn();
        window.confirm = vi.fn(() => true);
    });


    test("renders the application heading", async () => {
        render(<App />);

        expect(
            screen.getByRole("heading", {
                name: "Course Registration Platform"
            })
        ).toBeInTheDocument();
    });


    test("displays summary cards", async () => {
        render(<App />);

        expect(
            screen.getByText("Total Students")
        ).toBeInTheDocument();

        expect(
            screen.getByText("Total Courses")
        ).toBeInTheDocument();

        expect(
            screen.getByText("Backend Services")
        ).toBeInTheDocument();
    });


    test("shows empty student message", async () => {
        render(<App />);

        await waitFor(() => {
            expect(
                screen.getByText("No student data found.")
            ).toBeInTheDocument();
        });
    });


    test("switches to the course tab", async () => {
        render(<App />);

        fireEvent.click(
            screen.getByRole("button", {
                name: "Courses"
            })
        );

        expect(
            screen.getByRole("heading", {
                name: "Add Course"
            })
        ).toBeInTheDocument();

        await waitFor(() => {
            expect(
                screen.getByText("No course data found.")
            ).toBeInTheDocument();
        });
    });


    test("renders student form fields", async () => {
        render(<App />);

        expect(
            screen.getByPlaceholderText("S100001")
        ).toBeInTheDocument();

        expect(
            screen.getByPlaceholderText("Student name")
        ).toBeInTheDocument();

        expect(
            screen.getByPlaceholderText(
                "student@university.edu.au"
            )
        ).toBeInTheDocument();

        expect(
            screen.getByPlaceholderText(
                "Master of Information Technology"
            )
        ).toBeInTheDocument();
    });
});