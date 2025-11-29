import React from 'react';

function Topbar({ searchQuery, setSearchQuery, onSearch, onClear, onDashboard, onNotes, user }){
  // `user` is available here for potential personalization (not used yet)
  return (
    <header className="topbar">
      <div style={{display: 'flex', alignItems: 'center', gap: '12px'}}>
        <div className="brand">Lobster Notes</div>
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
          <button className="btn" type="button" onClick={onDashboard} title="Open Professor Dashboard">Dashboard</button>
          <button className="btn" type="button" onClick={onNotes} title="Back to Notes">Notes</button>
          
        </form>
      </div>
    </header>
  );
}

export default Topbar;
