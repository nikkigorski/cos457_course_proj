import React from "react";
import ReactDOM from "react-dom/client";
import "./styles.css";

function ProfessorCourses() {
  const [courseInput, setCourseInput] = React.useState({
    subject: "",
    catalogNumber: "",
    section: "",
    name: "",
    session: "",
    year: "",
  });

  const [courses, setCourses] = React.useState([]);
  const [loading, setLoading] = React.useState(false);

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
      alert("Subject must be exactly 3 letters");
      return;
    }

    if (!/^\d{3}$/.test(courseInput.catalogNumber)) {
      alert("Catalog Number must be 3 digits");
      return;
    }

    if (!courseInput.name.trim()) {
      alert("Course Name is required");
      return;
    }

    if (!courseInput.session || !courseInput.year) {
      alert("Session and Year are required");
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

  const handleConfirm = async () => {
    const professorName = localStorage.getItem("name");

    if (!professorName) {
      alert("Professor name not found. Please create account again.");
      return;
    }

    if (courses.length === 0) {
      alert("Please add at least one course.");
      return;
    }

    setLoading(true);

    try {
      const res = await fetch("/create-professor-account", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: professorName,
          courses: courses,
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.error || "Failed to create professor account");
      }

      alert("Professor account and courses saved successfully!");
      console.log("Professor Saved:", data);
      // Can add redirect to other html
      // window.location.href = "/dashboard.html";

    } catch (err) {
      alert("Error: " + err.message);
    } finally {
      setLoading(false);
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
            <h1 style={{ marginTop: 0 }}>Professor - Course Selection</h1>

            <form onSubmit={handleAddCourse}>
              <label>Subject:
                <input name="subject" value={courseInput.subject} onChange={handleChange} required className="note-title"/>
              </label>

              <label>Catalog Number:
                <input name="catalogNumber" value={courseInput.catalogNumber} onChange={handleChange} required className="note-title"/>
              </label>

              <label>Section:
                <input name="section" value={courseInput.section} onChange={handleChange} className="note-title"/>
              </label>

              <label>Name:
                <input name="name" value={courseInput.name} onChange={handleChange} className="note-title"/>
              </label>

              <label>Session:
                <select name="session" value={courseInput.session} onChange={handleChange} required className="note-title">
                  <option value="">Select</option>
                  <option>Spring</option>
                  <option>Summer</option>
                  <option>Fall</option>
                  <option>Winter</option>
                </select>
              </label>

              <label>Year:
                <input type="number" name="year" value={courseInput.year} onChange={handleChange} required className="note-title"/>
              </label>

              <button type="submit" className="btn btn-primary">Add Course</button>
            </form>

            <div className="note-list">
              {courses.map((course, index) => (
                <div key={index} className="notes">
                  <strong>{course.Name}</strong><br />
                  {course.Subject}
                  {course.CatalogNumber} — {course.Section} — {course.Session} {course.Year}
                </div>
              ))}
            </div>

            <button className="btn btn-primary" onClick={handleConfirm} disabled={loading || courses.length === 0}>
              {loading ? "Submitting" : "Confirm"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("professor-root"))
  .render(<ProfessorCourses />);
