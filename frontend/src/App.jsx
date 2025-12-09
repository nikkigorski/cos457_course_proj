import React, { useState, useEffect } from 'react';
import NoteList from './NoteList.jsx';
import NotePage from './NotePage.jsx';
import Topbar from './Topbar.jsx';
import ProfessorDashboard from './pages/ProfessorDashboard.jsx';
import SearchPage from './pages/SearchPage.jsx';
import AccountCreation from './AccountCreation.jsx';
import UsersList from './UsersList.jsx';
import Login from './pages/Login.jsx'
import HomePage from './pages/HomePage.jsx';

const API_BASE_URL = 'http://127.0.0.1:8080/api';

const sampleNotes = [
];

const sampleSearch = [
];

window.__SAMPLE_NOTES__ = sampleNotes;

function NoteEditor({ user, onNoteCreated }){
  const [title, setTitle] = useState('');
  const [course, setCourse] = useState('');
  const [keywords, setKeywords] = useState('');
  const [body, setBody] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState('');

  async function submit(e){
    e.preventDefault();
    
    if (!title || !body) {
      setMessage('Title and body are required');
      return;
    }
    
    setSubmitting(true);
    setMessage('');
    
    try {
      const response = await fetch(`${API_BASE_URL}/resources`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          DateFor: new Date().toISOString().split('T')[0], // Today's date in YYYY-MM-DD
          Author: user.username || 'Anonymous',
          Topic: title,
          Keywords: keywords || null,
          Format: 'Note',
          Body: body,
        }),
      });
      
      if (response.ok) {
        const result = await response.json();
        setMessage('Note saved successfully!');
        setTitle('');
        setCourse('');
        setKeywords('');
        setBody('');
        
        // Notify parent to refresh notes list
        if (onNoteCreated) {
          onNoteCreated();
        }
      } else {
        const error = await response.json();
        setMessage(`Error: ${error.error || 'Failed to save note'}`);
      }
    } catch (error) {
      console.error('Error saving note:', error);
      setMessage('Error: Failed to save note');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form className="note-editor" onSubmit={submit}>
      <h2>Note Editor</h2>
      {message && <div style={{padding: '8px', marginBottom: '8px', backgroundColor: message.includes('Error') ? '#f8d7da' : '#d4edda', borderRadius: '4px'}}>{message}</div>}
      <input className="note-title" placeholder="Title" value={title} onChange={e=>setTitle(e.target.value)} required />
      <input className="note-course" placeholder="Course" value={course} onChange={e=>setCourse(e.target.value)} />
      <input className="note-keywords" placeholder="Keywords (separated by commas)" value={keywords} onChange={e=>setKeywords(e.target.value)} />
      <textarea className="note-body" placeholder="Write your note here..." value={body} onChange={e=>setBody(e.target.value)} required />
      <div className="note-actions">
        <button className="btn btn-primary" type="submit" disabled={submitting}>
          {submitting ? 'Saving...' : 'Save Note'}
        </button>
      </div>
    </form>
  );
}

export default function App(){
  const [route, setRoute] = useState({ name: 'home', id: null });
  const [searchActive, setSearchActive] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [notes, setNotes] = useState(sampleNotes);
  const [loading, setLoading] = useState(false);
  const [searchResults, setSearchResults] = useState([]);
  const [user, setUser] = useState(null);
  const hasUser = !!user;

  // Fetch notes from API on mount
  useEffect(() => {
    const fetchNotes = async () => {
      setLoading(true);
      try {
        const response = await fetch(`${API_BASE_URL}/resources`);
        if (response.ok) {
          const data = await response.json();
          setNotes(data);
        } else {
          console.error('Failed to fetch notes');
          setNotes(sampleNotes); // Fallback to sample data
        }
      } catch (error) {
        console.error('Error fetching notes:', error);
        setNotes(sampleNotes); // Fallback to sample data
      } finally {
        setLoading(false);
      }
    };
    fetchNotes();
  }, []);

  useEffect(() => {
    const syncRouteFromLocation = () => {
      const p = window.location.pathname;
      const m = p.match(/^\/note\/(\d+)$/);
      if (m) {
        setRoute({ name: 'note', id: Number(m[1]) });
      } else if (p === '/dashboard') {
        setRoute({ name: 'dashboard', id: null });
      } else if (p === '/account') {
        setRoute({ name: 'account', id: null });
      } else if (p === '/users') {
        setRoute({ name: 'users', id: null });
      } else if (p === '/search') {
        setRoute({ name: 'search', id: null });
      } else if (p === '/login'){
        setRoute({name: 'login',id: null});
      } else if (p === '/account') {
        setRoute({ name: 'account', id: null });
      } else if (p === '/notes'){
        setRoute({ name: 'notes', id: null });
      } else {
        setRoute({ name: 'home', id: null });
      }
    };

    syncRouteFromLocation();

    const onPop = () => syncRouteFromLocation();
    window.addEventListener('popstate', onPop);
    return () => window.removeEventListener('popstate', onPop);
  }, []);

  // Enforce account page until user exists; once user exists, prevent navigating back to account
  useEffect(() => {
    if (!hasUser && route.name !== 'account') {
      setRoute({ name: 'account', id: null });
      window.history.replaceState({ route: 'account' }, '', '/account');
    }
    if (hasUser && route.name === 'account') {
      // Move to homepage and replace history to avoid back navigation to account page
      setRoute({ name: 'home', id: null });
      window.history.replaceState({ route: 'home' }, '', '/');
    }
  }, [hasUser, route.name]);

  const openNote = (id) => {
    const noteUrl = `/note/${id}`;
    window.history.pushState({ route: 'note', id }, '', noteUrl);
    setRoute({ name: 'note', id });
    setSearchActive(false);
  };

  const openDashboard = () => {
    window.history.pushState({ route: 'dashboard' }, '', '/dashboard');
    setRoute({ name: 'dashboard', id: null });
    setSearchActive(false);
  };

  const openUsers = () => {
    window.history.pushState({ route: 'users' }, '', '/users');
    setRoute({ name: 'users', id: null });
    setSearchActive(false);
  };

  const handleAccountCreated = ({ userId, name, isProfessor }) => {
    const newUser = {
      userId,
      username: name,
      isProfessor: isProfessor,
    };
    setUser(newUser);
    if (isProfessor) {
      window.history.replaceState({ route: 'dashboard' }, '', '/dashboard');
      setRoute({ name: 'dashboard', id: null });
    } else {
      window.history.replaceState({ route: 'list' }, '', '/');
      setRoute({ name: 'list', id: null });
    }
  };

  const goHome = () => {
    window.history.pushState({ route: 'home' }, '', '/');
    setRoute({ name: 'home', id: null });
    setSearchActive(false);
    setSearchQuery('');
    window.dispatchEvent(new PopStateEvent('popstate'));
  };

  const goLogin = () => {
    window.history.pushState({route: 'login'},'','/login');
    setRoute({name:'login',id:null});
    setSearchActive(false);
  };

  const APIonLogin = async (username,password) => {
    const response = await fetch(`${API_BASE_URL}/login`,{
      method: "GET",
      body: JSON.stringify({username:username,password:password}),
      headers: {
        'Content-Type': 'application/json',
      }
    });
    return response;
  };

  const doLogin = async (userData) => {
    if (userData != null){
      setUser(userData);
      goHome();
    }
    return;
  }

  const openSearch = async (query) => {
    const url = '/search';
    window.history.pushState({ route: 'search', query }, '', url);
    setRoute({ name: 'search', id: null });
    setSearchActive(true);
    setSearchQuery(query || '');
    
    // Fetch search results from API
    if (query && query.trim()) {
      setLoading(true);
      try {
        const response = await fetch(`${API_BASE_URL}/resources?search=${encodeURIComponent(query)}`);
        if (response.ok) {
          const data = await response.json();
          setSearchResults(data);
        } else {
          console.error('Failed to fetch search results');
          setSearchResults(sampleSearch);
        }
      } catch (error) {
        console.error('Error fetching search results:', error);
        setSearchResults(sampleSearch);
      } finally {
        setLoading(false);
      }
    } else {
      setSearchResults([]);
    }
  };

  const goBack = () => {
    window.history.back();
  };

  const goNotes = () => {
    window.history.pushState({route: 'list'}, '', '/notes');
    setRoute({ name: 'list', id: null });
    setSearchActive(false);
  };

  const goAcctCreate = () => {
    window.history.pushState({route: 'account'},'','/account');
    setRoute({name:'account',id:null});
    setSearchActive(false);
  };

  const handleLogout = () => {
    setUser(null);
    window.history.replaceState({ route: 'account' }, '', '/account');
    setRoute({ name: 'account', id: null });
    setSearchActive(false);
    setSearchQuery('');
    setSearchResults([]);
  };

  const activeNote = notes.find(n => n.ResourceID === route.id) || null;

  // Callback to refresh notes after creating a new one
  const handleNoteCreated = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/resources`);
      if (response.ok) {
        const data = await response.json();
        setNotes(data);
      }
    } catch (error) {
      console.error('Error refreshing notes:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-shell">
      <Topbar
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
        onSearch={(e) => { e.preventDefault(); openSearch(searchQuery); }}
        onClear={() => { setSearchQuery(''); setSearchActive(false); }}
        onDashboard={openDashboard}
        onNotes={goNotes}
        user={user || {}}
        hasUser={hasUser}
        onLogout={handleLogout}
        onHome={goHome}
        onLoginButton={goLogin}
        onCreateAccount={goAcctCreate}
      />
      <main className="main">
        {searchActive ? (
          <section style={{width: '100%'}}>
            <SearchPage notes={searchResults.length > 0 ? searchResults : sampleSearch} onOpenNote={openNote} onBack={goBack} user={user} loading={loading} />
          </section>
        ) : route.name === 'note' ? (
          <section className="note-full">
            <NotePage noteId={route.id} note={activeNote} onBack={goBack} user={user} apiBaseUrl={API_BASE_URL} />
          </section>
        ) : route.name === 'account' ? (
          <section style={{width: '100%'}}>
            <AccountCreation onSuccess={handleAccountCreated} />
          </section>
        ) : route.name === 'users' ? (
          <section style={{width: '100%'}}>
            <UsersList onBack={goBack} />
          </section>
        ) : route.name === 'dashboard' ? (
          <section style={{width: '100%'}}>
            <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12}}>
              <h2>Professor Dashboard</h2>
              <div>
                <button className="btn" onClick={goBack}>Back</button>
              </div>
            </div>
            <ProfessorDashboard professorId={user?.userId || 1} />
          </section>
        ) : route.name === 'notes' ? (
          <React.Fragment>
            <section className="left">
              <div style={{display: 'flex', gap: '8px', marginBottom: '12px'}}>
                <button className="btn" onClick={openUsers}>View Users</button>
              </div>
              <NoteEditor user={user || { username: 'Anonymous' }} onNoteCreated={handleNoteCreated} />
            </section>
            <section className="right">
              <h2>My Notes</h2>
              {loading ? <p>Loading notes...</p> : <NoteList notes={notes} onOpenNote={openNote} user={user} />}
            </section>
          </React.Fragment>
        ) : route.name === 'login' ? (
          <section className='login-full'>
            <Login
            onLogin={APIonLogin}
            user={user}
            doLogin={doLogin}/>
          </section>
        ) : (
          <section className='note-full'>
            <HomePage user={user}/>
          </section>
        )}
      </main>
    </div>
  );
}

