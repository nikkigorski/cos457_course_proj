import React from 'react';

function NoteList({ notes, onOpenNote, user, filterByUser = true }){
  const list = notes || window.__SAMPLE_NOTES__ || [];
  // Filter notes to show only those by the current user (unless filterByUser is false)
  const displayNotes = filterByUser && user?.username ? list.filter(n => n.Author === user.username) : list;

  return (
    <div className="note-list">
      <div className="notes">
        {displayNotes.map(n => (
          <div key={n.ResourceID} style={{marginBottom: '8px'}}>
            <button
              className="btn"
              type="button"
              onClick={() => {
                if (onOpenNote) {
                  onOpenNote(n.ResourceID);
                } else {
                  const url = `/note/${n.ResourceID}`;
                  window.history.pushState({ route: 'note', id: n.ResourceID }, '', url);
                  window.dispatchEvent(new PopStateEvent('popstate'));
                }
              }}
            >
              {n.Title}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

export default NoteList;
