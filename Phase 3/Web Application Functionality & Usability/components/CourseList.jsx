import React from 'react';
import { Link } from 'react-router-dom';

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

            <li key={course.CourseID} className="list-group-item p-0">
              
            <Link 
              to={`/course/${course.CourseID}`} 
              key={course.CourseID} 
              className="list-group-item list-group-item-action d-flex justify-content-between align-items-center p-3"
              style={{textDecoration: 'none', color: 'inherit'}}
            >
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
              </Link>
            </li>
          );
        })}
      </ul>
    </div>
  );
}

export default CourseList;