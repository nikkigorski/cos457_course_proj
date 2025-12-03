import React from 'react';

function StudentRoster({ students }) {
  return (
    <div className="card shadow-sm">
      <div className="card-header bg-success text-white">
        <h5 className="mb-0">Student Roster</h5>
      </div>
      <div className="table-responsive">
        <table className="table table-hover mb-0">
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Enrolled In</th>
              <th>Role</th>
            </tr>
          </thead>
          <tbody>
            {students.map(function(student) {
              // if IsProfessor is True -> skip record
              if (String(student.IsProfessor) === 'True') {
                return null;
              }

              return (
                <tr key={student.UserID}>
                  <td>{student.UserID}</td>
                  <td>{student.Name}</td>
                  <td>{student.Courses}</td>
                  <td>
                    <span className="badge bg-secondary">
                      Student
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default StudentRoster;