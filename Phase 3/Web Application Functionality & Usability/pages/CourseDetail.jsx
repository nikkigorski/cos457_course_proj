import React from 'react';
//import { useParams, Link } from 'react-router-dom';
import { sampleCourses, sampleStudents, sampleResources } from '../data.js';

function CourseDetail(id, onBack) {
  //const { id } = useParams(); // Get CourseID from URL
  const courseId = parseInt(id);

 //Find Course
  const course = sampleCourses.find(function(c) {
    return c.CourseID === courseId;
  });

  if (!course) {
    return <div className="container mt-5"><h2>Course not found</h2></div>;
  }

  //Find Professor
  const professor = sampleStudents.find(function(u) {
    return u.UserID === course.ProfessorID;
  });

  // Find Enrolled Students
  const enrolledStudents = sampleStudents.filter(function(s) {
    return s.Courses === course.Subject && s.IsProfessor === "False";
  });

  //Find Resources
  const resources = sampleResources.filter(function(r) {
    return r.CourseID === courseId;
  });

  return (
    <div className="container mt-5">
      {/* Header */}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1 className="mb-0">{course.Subject} {course.CatalogNumber}: {course.Name}</h1>
          <p className="text-muted mb-0">
            {course.Session} {course.Year} | Section {course.Section} | Dept: {course.Subject}
          </p>
        </div>
        <Link to="/professor" className="btn btn-outline-secondary">Back to Dashboard</Link>
      </div>

      <div className="row">
        {/* Left Column: Details & Resources */}
        <div className="col-md-8">
          {/* Professor Card */}
          <div className="card mb-4">
            <div className="card-header">Instructor</div>
            <div className="card-body">
              <h5 className="card-title">{professor ? professor.Name : "Unknown"}</h5>
              <p className="card-text text-muted">User ID: {course.ProfessorID}</p>
            </div>
          </div>

          {/* Resources Card */}
          <div className="card mb-4">
            <div className="card-header">Course Resources</div>
            <ul className="list-group list-group-flush">
              {resources.length > 0 ? (
                resources.map(function(r) {
                  return (
                    <li key={r.ResourceID} className="list-group-item d-flex justify-content-between">
                      <span>{r.Title}</span>
                      <span className="badge bg-info">{r.Type}</span>
                    </li>
                  );
                })
              ) : (
                <li className="list-group-item text-muted">No resources uploaded.</li>
              )}
            </ul>
          </div>
        </div>

        {/* Right Column: Student Roster */}
        <div className="col-md-4">
          <div className="card">
            <div className="card-header bg-success text-white d-flex justify-content-between align-items-center">
              <span>Roster</span>
              <span className="badge bg-light text-dark">{enrolledStudents.length}</span>
            </div>
            <ul className="list-group list-group-flush">
              {enrolledStudents.map(function(s) {
                return (
                  <li key={s.UserID} className="list-group-item">
                    {s.Name} <br/>
                    <small className="text-muted">ID: {s.UserID}</small>
                  </li>
                );
              })}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

export default CourseDetail;