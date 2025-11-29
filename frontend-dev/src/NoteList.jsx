import React from 'react';

function NoteList({ notes, onOpenNote, user }){
  const list = notes || window.__SAMPLE_NOTES__ || [];

  return (
    <div className="note-list">
      <h2>My Notes</h2>
      <div className="notes">
        {list.map(n => (
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
