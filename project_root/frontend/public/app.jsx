const { useState, useEffect } = React;

const sampleNotes = [
  { ResourceID: 1,Title: "Computational music theory" ,Author: "mit ocw, lobster notes web scraper", Rating: "5", Date: "2025-11-15", Format: "Video", Url:"https://ocw.mit.edu/courses/21m-383-computational-music-theory-and-analysis-spring-2023/21m383-s23-video1a_tutorial_360p_16_9.mp4" },
  { ResourceID: 2,Title: "test title2" ,Author: "Author2", Rating: "4", Date: "2024-02-15", Format: "PDF" },
  { ResourceID: 3,Title: "test title3" ,Author: "Author3", Rating: "3", Date: "2024-03-10", Format: "PDF" },
  { ResourceID: 4,Title: "test title4" ,Author: "Author4", Rating: "2", Date: "2024-04-20", Format: "PDF" },
  { ResourceID: 5,Title: "test title5" ,Author: "Author5", Rating: "4", Date: "2024-05-05", Format: "PDF" },
  { ResourceID: 6,Title: "test title6" ,Author: "Author6", Rating: "3", Date: "2024-06-15", Format: "PDF" },
  { ResourceID: 7,Title: "test title7" , Author: "Author7", Rating: "5", Date: "2024-07-22", Format: "PDF" },
  { ResourceID: 8,Title: "test title8" ,Author: "Author8", Rating: "4", Date: "2024-08-30", Format: "PDF" },
  { ResourceID: 9,Title: "test title9" ,Author: "Author9", Rating: "3", Date: "2024-09-15", Format: "PDF" },
  { ResourceID: 10,Title: "test title10" ,Author: "Author10", Rating: "4", Date: "2024-10-10", Format: "PDF" }
  
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
