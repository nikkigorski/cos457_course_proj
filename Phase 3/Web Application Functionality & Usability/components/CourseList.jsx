import React from 'react';

function CourseList({ courses }) {
  return (
    <div className="card shadow-sm">
      <div className="card-header bg-primary text-white">
        <h5 className="mb-0">Courses</h5>
      </div>
      <ul className="list-group list-group-flush">
        {courses.map(function(course) {
          // Standard function syntax
          return (
            <li key={course.CourseID} className="list-group-item d-flex justify-content-between align-items-center">
              <div>
                {/* Combines subject and catalog number into a course */}
                <strong>{course.Subject} {course.CatalogNumber}</strong>: {course.Name}
                <br/>
                {/* Display Session, Year and Section */}
                <small className="text-muted">
                  {course.Session} {course.Year} | Section {course.Section}
                </small>
              </div>
              
              <div className="text-end">
                {/* ProfessorID for course */}
                <span className="badge bg-secondary">
                  Prof ID: {course.ProfessorID}
                </span>
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
}

export default CourseList;