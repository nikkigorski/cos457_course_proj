import React, { useState, useEffect } from 'react';
import CourseList from '../components/CourseList';
import StudentRoster from '../components/StudentRoster';
import { sampleCourses, sampleStudents } from '../data';

export default function ProfessorDashboard() {
  const [courses, setCourses] = useState([]);
  const [students, setStudents] = useState([]);

  useEffect(function() {
    setCourses(sampleCourses);
    setStudents(sampleStudents);
  }, []);

  return (
    <div className="container mt-5">
      <div className="row mb-4">
        <div className="col">
          <h1>Professor Dashboard</h1>
          <p className="text-muted">Manage courses and view students.</p>
        </div>
      </div>

      <div className="row">
        {/* Courses on left*/}
        <div className="col-md-5 mb-4">
          <CourseList courses={courses} />
        </div>

        {/* Students on right*/}
        <div className="col-md-7">
          <StudentRoster students={students} />
        </div>
      </div>
    </div>
  );
}
