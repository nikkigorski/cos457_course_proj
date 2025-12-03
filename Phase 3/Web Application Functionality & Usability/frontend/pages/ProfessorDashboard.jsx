import React, { useState, useEffect } from 'react';
import CourseList from '../components/CourseList';
import StudentRoster from '../components/StudentRoster';



function ProfessorDashboard( {onCourseSelect}) {
  const [courses, setCourses] = useState([]);
  const [selectedCourseId, setSelectedCourseId] = useState(null);
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);

  const [searchTerm, setSearchTerm] = useState(''); 

  const [inputSearchTerm, setInputSearchTerm] = useState('');

  const API_BASE_URL = 'http://127.0.0.1:8080/api';
  const PROFESSOR_ID = 1; // Test Professor ID 1

  const handleCourseSelection = function(courseID){
    setSelectedCourseId(courseID);

    if (onCourseSelect) {
      onCourseSelect(courseID);
    }
  };

  const handleSearchSubmit = function(e) {
      e.preventDefault();
      setSearchTerm(inputSearchTerm);
  };
  useEffect(function() {
    setLoading(true); 
    
  
    var url = API_BASE_URL + '/professor/' + PROFESSOR_ID + '/courses';
    if (searchTerm) {
        url += '?search=' + encodeURIComponent(searchTerm);
    }

    fetch(url)
      .then(function(response) {
        if (!response.ok) {
          throw new Error('Failed to fetch courses');
        }
        return response.json();
      })
      .then(function(data) {
        setCourses(data);
        setLoading(false);
        // Automatically select the first course to show its roster
        if (data.length > 0 && selectedCourseId === null) {
          setSelectedCourseId(data[0].CourseID);
        } else if (data.length === 0) {
          setSelectedCourseId(null);
        }
      })
      .catch(function(error) {
        console.error("Error fetching courses:", error);
        setLoading(false);
      });
  }, [searchTerm]); 

  // Fetch Roster when a Course is Selected
  useEffect(function() {
    if (selectedCourseId) {
      // Fetch the roster for the currently selected course
      fetch(API_BASE_URL + '/course/' + selectedCourseId + '/roster')
        .then(function(response) {
          return response.json();
        })
        .then(function(data) {
          setStudents(data); 
        })
        .catch(function(error) {
          console.error("Error fetching roster:", error);
        });
    } else {
      setStudents([]); // Clear roster if no course is selected
    }
  }, [selectedCourseId]); 


  if (loading) {
    return (
      <div className="container mt-5 text-center">
        <p>Loading professor dashboard...</p>
      </div>
    );
  }

  return (
    <div className="container mt-5">
      <div className="row mb-4">
        <div className="col">
          <h1>Professor Dashboard</h1>
          <p className="text-muted">Manage courses and view students.</p>
        </div>
        
        {/* Search Input Field */}
        <form className="col-12 mb-4" onSubmit={handleSearchSubmit}>
            <input
                type="text"
                className="form-control"
                placeholder="Search courses by name or subject..."
                onChange={function(e) { setInputSearchTerm(e.target.value); }}
                value={inputSearchTerm}
            />
          <button type="submit" style={{ display: 'none' }}>Search</button> 

        </form>
        
      </div>

      <div className="row">
        {/* Courses on left */}
        <div className="col-md-5 mb-4">
          <CourseList 
            courses={courses} 
            onCourseSelect={handleCourseSelection}
            selectedCourseId={selectedCourseId}
          /> 
        </div>

        {/* Students on right*/}
        <div className="col-md-7">
          <StudentRoster students={students} />
        </div>
      </div>
    </div>
  );
}

export default ProfessorDashboard;