const { useState, useEffect } = React;

const sampleNotes = [
  { ResourceID: 1,Title: "test title1" },
  { ResourceID: 2,Title: "test title2" },
  { ResourceID: 3,Title: "test title3" },
  { ResourceID: 4,Title: "test title4" },
  { ResourceID: 5,Title: "test title5" },
  { ResourceID: 6,Title: "test title6" },
  { ResourceID: 7,Title: "test title7" },
  { ResourceID: 8,Title: "test title8" },
  { ResourceID: 9,Title: "test title9" },
  { ResourceID: 10,Title: "test title10" }
  
];

window.__SAMPLE_NOTES__ = sampleNotes;

function NoteEditor(){
  const [title, setTitle] = useState('');
  const [body, setBody] = useState('');

  function submit(e){
    e.preventDefault();
    return;
  }

  return (
    <form className="note-editor" onSubmit={submit}>
      <h2>Note Editor</h2>
      <input className="note-title" placeholder="Title" value={title} onChange={e=>setTitle(e.target.value)} />
      <textarea className="note-body" placeholder="Write your note here..." value={body} onChange={e=>setBody(e.target.value)} />
      <div className="note-actions">
        <button className="btn btn-primary" type="submit">Save Note</button>
      </div>
    </form>
  );
}

function NoteList({ onOpenNote }){
  return (
    <div className="note-list">
      <h2>My Notes</h2>
      <div className="notes">
        {sampleNotes.map(n => (
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

function App(){
  const [route, setRoute] = useState({ name: 'list', id: null });

  useEffect(() => {
    const syncRouteFromLocation = () => {
      const m = window.location.pathname.match(/^\/note\/(\d+)$/);
      if (m) {
        setRoute({ name: 'note', id: Number(m[1]) });
      } else {
        setRoute({ name: 'list', id: null });
      }
    };

    syncRouteFromLocation();

    const onPop = () => syncRouteFromLocation();
    window.addEventListener('popstate', onPop);
    return () => window.removeEventListener('popstate', onPop);
  }, []);

  const openNote = (id) => {
    if (typeof console !== 'undefined' && console.log) console.log('openNote called with', id);
    const noteUrl = `/note/${id}`;
    window.history.pushState({ route: 'note', id }, '', noteUrl);
    setRoute({ name: 'note', id });
  };

  const goBack = () => {
    window.history.pushState({}, '', '/');
    setRoute({ name: 'list', id: null });
    window.dispatchEvent(new PopStateEvent('popstate'));
  };

  const activeNote = sampleNotes.find(n => n.ResourceID === route.id) || null;

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">Lobster Notes</div>
      </header>
      <main className="main">
        {route.name === 'note' ? (
          <section className="note-full">
            <NotePage note={activeNote} onBack={goBack} />
          </section>
        ) : (
          <React.Fragment>
            <section className="left">
              <NoteEditor />
            </section>
            <section className="right">
              <NoteList onOpenNote={openNote} />
            </section>
          </React.Fragment>
        )}
      </main>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
