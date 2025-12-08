import React, { useState } from 'react';
import { API_BASE_URL } from './config.js';

export default function AccountCreation({ onSuccess }) {
  const [name, setName] = useState('');
  const [courses, setCourses] = useState('');
  const [isProfessor, setIsProfessor] = useState(false);
  const [message, setMessage] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      const response = await fetch(`${API_BASE_URL}/users`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          Name: name.trim(),
          Courses: courses || null,
          IsProfessor: isProfessor,
        }),
      });

      const data = await response.json();
      if (response.ok) {
        setMessage('Account created successfully!');
        if (onSuccess) {
          onSuccess({ userId: data.user_id, name: data.Name || name.trim(), isProfessor: data.IsProfessor ?? isProfessor });
        }
        setName('');
        setCourses('');
        setIsProfessor(false);
      } else {
        setMessage(data.error || 'Failed to create account');
      }
    } catch (err) {
      console.error('Error creating account:', err);
      setMessage('Error: Failed to create account');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div>
      <div className="topbar">
        <span className="brand">Lobster Notes</span>
      </div>

      <div className="main" style={{ justifyContent: 'center' }}>
        <div className="left" style={{ maxWidth: '520px' }}>
          <div className="note-editor">
            <h1 style={{ marginTop: 0 }}>Create Your Account</h1>

            <form onSubmit={handleSubmit} className="account-form">
              <label style={{ display: 'block', marginBottom: '12px' }}>
                Name:
                <input
                  type="text"
                  name="name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                  maxLength="50"
                  className="note-title"
                />
              </label>

              <label style={{ display: 'block', marginBottom: '12px' }}>
                Courses (optional):
                <input
                  type="text"
                  name="courses"
                  value={courses}
                  onChange={(e) => setCourses(e.target.value)}
                  className="note-title"
                  placeholder="e.g. CS101, MTH200"
                />
              </label>
              
              <div className="role-select" style={{ marginTop: '12px' }}>
                <p>Select your role:</p>

                <label style={{ marginRight: '12px' }}>
                  <input
                    type="radio"
                    name="role"
                    value="Student"
                    checked={!isProfessor}
                    onChange={() => setIsProfessor(false)}
                  />{' '}
                  Student
                </label>

                <label>
                  <input
                    type="radio"
                    name="role"
                    value="Professor"
                    checked={isProfessor}
                    onChange={() => setIsProfessor(true)}
                  />{' '}
                  Professor
                </label>
              </div>

              <button className="btn btn-primary" type="submit" style={{ marginTop: '12px' }} disabled={submitting}>
                {submitting ? 'Creating...' : 'Create Account'}
              </button>
            </form>

            {message && (
              <div
                style={{
                  marginTop: '12px',
                  padding: '8px',
                  borderRadius: '4px',
                  backgroundColor: message.includes('Error') ? '#f8d7da' : '#d4edda',
                  color: message.includes('Error') ? '#721c24' : '#155724'
                }}
              >
                {message}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
