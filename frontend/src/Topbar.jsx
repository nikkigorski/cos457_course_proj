import React from 'react';

function Topbar({ searchQuery, setSearchQuery, onSearch, onClear, onDashboard, onNotes, user, hasUser, onLogout }){
  // When no user exists yet, hide navigation/search controls.
  const isProfessor = user?.isProfessor;
  return (
    <header className="topbar">
      <div style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '12px', width: '100%'}}>
        <div style={{display: 'flex', alignItems: 'center', gap: '12px'}}>
          <div className="brand">Lobster Notes</div>
          {hasUser ? (
            <form onSubmit={onSearch} style={{display:'flex', alignItems:'center', gap: '8px'}}>
              <input
                className="note-search"
                placeholder="Search notes..."
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
                style={{padding: '6px 8px', borderRadius: 6, border: '1px solid #e6e9ef'}}
              />
              <button className="btn" type="submit">Search</button>
              <button className="btn" type="button" onClick={onClear}>Clear</button>
              {isProfessor && <button className="btn" type="button" onClick={onDashboard} title="Open Professor Dashboard">Professor Dashboard</button>}
              <button className="btn" type="button" onClick={onNotes} title="Back to Notes">Notes</button>
            </form>
          ) : null}
        </div>
        {hasUser && (
          <button className="btn" type="button" onClick={onLogout} title="Logout">Logout</button>
        )}
      </div>
    </header>
  );
}

export default Topbar;
