import React, { useState, useEffect } from 'react';

function CourseDetail({ id, onBack }) {
  const [course, setCourse] = useState(null);
  const [enrolledStudents, setEnrolledStudents] = useState([]);
  const [loading, setLoading] = useState(true);

  
  const resources = []; 

  const API_BASE_URL = 'http://127.0.0.1:8080/api';

  useEffect(function() {
    if (!id) return;

    setLoading(true);

//get course details
    fetch(API_BASE_URL + '/course/' + id)
      .then(function(response) {
        return response.json();
      })
      .then(function(courseData) {
        //has course data
        setCourse(courseData);

//get roster
        return fetch(API_BASE_URL + '/course/' + id + '/roster');
      })
      .then(function(response) {
        return response.json();
      })
      .then(function(rosterData) {
        //has roster data
        setEnrolledStudents(rosterData);
      
        setLoading(false);
      })
      .catch(function(err) {
        console.error("Error loading data:", err);
        setLoading(false);
      });
      
  }, [id]);

  if (loading) {
    return <div className="container mt-5"><h3>Loading...</h3></div>;
  }

  if (!course || course.error) {
    return (
      <div className="container mt-5">
        <h3>Course not found</h3>
        <button className="btn btn-secondary mt-3" onClick={onBack}>Back to Dashboard</button>
      </div>
    );
  }

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
        <button onClick={onBack} className="btn btn-outline-secondary">Back to Dashboard</button>
      </div>

      <div className="row">
        {/* Left Column: Details & Resources */}
        <div className="col-md-8">
          {/* Professor Card */}
          <div className="card mb-4">
            <div className="card-header">Instructor</div>
            <div className="card-body">
              <h5 className="card-title">{course.ProfessorName || "Unknown"}</h5>
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