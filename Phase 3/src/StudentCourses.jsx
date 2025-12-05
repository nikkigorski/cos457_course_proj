import React from "react";
import ReactDOM from "react-dom/client";
import "./styles.css";

function StudentCourses() {
  const [courseInput, setCourseInput] = React.useState({
    subject: "",
    catalogNumber: "",
    section: "",
    name: "",
    session: "",
    year: "",
  });

  const [courses, setCourses] = React.useState([]);

  const handleChange = (e) => {
    const { name, value } = e.target;
  
    setCourseInput((prev) => ({
      ...prev,
      [name]:
        name === "subject"
          ? value.toUpperCase()
          : name === "catalogNumber"
          ? value.replace(/\D/g, "")
          : value,
    }));
  };
  

  const handleAddCourse = (e) => {
    e.preventDefault();

    if (!/^[A-Z]{3}$/.test(courseInput.subject)) {
      alert("Subject must be exactly 3 letters (ex: COS)");
      return;
    }

    if (!/^\d{3}$/.test(courseInput.catalogNumber)) {
      alert("Catalog Number must be exactly 3 digits (ex: 450)");
      return;
    }

    if (courseInput.year < 2000) {
      alert("Year must be after 2000");
      return;
    }

    if (!courseInput.name.trim()) {
      alert("Course Name is required");
      return;
    }

    const newCourse = {
      Subject: courseInput.subject,
      CatalogNumber: courseInput.catalogNumber,
      Section: courseInput.section,
      Name: courseInput.name,
      Session: courseInput.session,
      Year: courseInput.year,
    };

    setCourses((prev) => [...prev, newCourse]);

    setCourseInput({
      subject: "",
      catalogNumber: "",
      section: "",
      name: "",
      session: "",
      year: "",
    });
  };

  const handleConfirm = async (e) => {
    e.preventDefault();
    //Flask call
    const studentName = localStorage.getItem("username");
  
    if (!studentName) {
      alert("Student name not found. Please create account again.");
      return;
    }
  
    try {
      const response = await fetch("http://localhost:5000/create-student-account", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: studentName,
          courses: courses,
        }),
      });
  
      const result = await response.json();
  
      if (!response.ok) {
        throw new Error(result.error || "Student creation failed");
      }
  
      alert("Student account created successfully!");
      console.log("Flask Response:", result);
  
    } catch (err) {
      alert("Error: " + err.message);
      console.error(err);
    }
  };

  return (
    <div>
      <div className="topbar">
        <span className="brand">Lobster Notes</span>
      </div>

      <div className="main" style={{ justifyContent: "center" }}>
        <div className="left" style={{ maxWidth: "520px" }}>
          <div className="note-editor">
            <h1 style={{ marginTop: 0 }}>Student - Course Selection</h1>

            <form onSubmit={handleAddCourse}>
              <label>
                Subject (3 letters):
                <input
                  type="text"
                  name="subject"
                  value={courseInput.subject}
                  onChange={handleChange}
                  required
                  maxLength="3"
                  className="note-title"
                />
              </label>

              <label>
                Catalog Number (3 digits):
                <input
                  type="text"
                  name="catalogNumber"
                  value={courseInput.catalogNumber}
                  onChange={handleChange}
                  required
                  maxLength="3"
                  className="note-title"
                />
              </label>

              <label>
                Section:
                <input
                  type="text"
                  name="section"
                  value={courseInput.section}
                  onChange={handleChange}
                  className="note-title"
                />
              </label>

              <label>Name:
                <input name="name" value={courseInput.name} onChange={handleChange} className="note-title"/>
              </label>

              <label>
                Session:
                <select
                  name="session"
                  value={courseInput.session}
                  onChange={handleChange}
                  required
                  className="note-title"
                >
                  <option value="">Select</option>
                  <option>Spring</option>
                  <option>Summer</option>
                  <option>Fall</option>
                  <option>Winter</option>
                </select>
              </label>

              <label>
                Year:
                <input
                  type="number"
                  name="year"
                  value={courseInput.year}
                  onChange={handleChange}
                  required
                  className="note-title"
                />
              </label>

              <div style={{ height: "14px" }} />

              <button type="submit" className="btn btn-primary">
                Add Course
              </button>
            </form>

            <div style={{ height: "24px" }} />

            <h3>Entered Courses</h3>

            <div className="note-list">
              {courses.length === 0 && (
                <div className="notes">No courses added yet.</div>
              )}

              {courses.map((course, index) => (
                <div key={index} className="notes">
                  <strong>{course.Name}</strong><br />
                  {course.Subject}
                  {course.CatalogNumber} — Section {course.Section} —{" "}
                  {course.Session} {course.Year}
                </div>
              ))}
            </div>

            <div style={{ height: "20px" }} />

            <button
              className="btn btn-primary"
              onClick={handleConfirm}
              disabled={courses.length === 0}
            >
              Confirm
            </button>
            </div>
        </div>
      </div>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("student-root"))
  .render(<StudentCourses />);
