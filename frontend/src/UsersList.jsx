import React, { useEffect, useState } from 'react';
import { API_BASE_URL } from './config.js';

export default function UsersList({ onBack }) {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchUsers = async () => {
      setLoading(true);
      setError('');
      try {
        const response = await fetch(`${API_BASE_URL}/users`);
        if (response.ok) {
          const data = await response.json();
          setUsers(data);
        } else {
          setError('Failed to fetch users');
        }
      } catch (err) {
        console.error('Error fetching users:', err);
        setError('Error fetching users');
      } finally {
        setLoading(false);
      }
    };

    fetchUsers();
  }, []);

  return (
    <div style={{ padding: '16px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <h2 style={{ margin: 0 }}>Users</h2>
        {onBack && <button className="btn" onClick={onBack}>Back</button>}
      </div>

      {loading ? (
        <p>Loading users...</p>
      ) : error ? (
        <p>{error}</p>
      ) : users.length === 0 ? (
        <p>No users found.</p>
      ) : (
        <div style={{ display: 'grid', gap: '8px' }}>
          {users.map((u) => (
            <div key={u.UserID} style={{ padding: '8px', border: '1px solid #ddd', borderRadius: '6px' }}>
              <div><strong>ID:</strong> {u.UserID}</div>
              <div><strong>Name:</strong> {u.Name}</div>
              <div><strong>Courses:</strong> {u.Courses || '—'}</div>
              <div><strong>Professor:</strong> {u.IsProfessor ? 'Yes' : 'No'}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
