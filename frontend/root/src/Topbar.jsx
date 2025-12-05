import React from 'react';

function Topbar({ searchQuery, setSearchQuery, onSearch, onClear, onDashboard, onNotes, onHome, onLoginButton, onCreateAccount, user }){
  // `user` is available here for potential personalization (not used yet)
  return (
    <header className="topbar">
      <div style={{display: 'flex', alignItems: 'center', gap: '12px'}}>
        <div className="brand">Lobster Notes</div>
        <form onSubmit={onSearch} style={{display:'flex', alignItems:'center', gap: '8px'}}>
          <button className="btn" type="button" onClick={onHome} title="Homepage">Home</button>
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
        <button className='btn' type='button' onClick={onCreateAccount} title='Account Creation'>Create Account</button>
        <button className="btn" style={{float:'right'}} type="button" onClick={onLoginButton} title="Login page" >Login</button>
      </div>
    </header>
  );
}

export default Topbar;
