const { useState, useEffect } = React;

const sampleNotes = [
  { ResourceID: 1,Title: "Computational music theory" ,Author: "mit ocw, lobster notes web scraper", Rating: "5", Date: "2025-11-15", Format: "Video", Url:"https://ocw.mit.edu/courses/21m-383-computational-music-theory-and-analysis-spring-2023/21m383-s23-video1a_tutorial_360p_16_9.mp4" },
  { ResourceID: 2,Title: "Computational Music teory and Analysis QUIZ 1" ,Author: "mit ocw, lobster notes web scraper", Rating: "4", Date: "2025-11-15", Format: "PDF", Url:"https://ocw.mit.edu/courses/21m-383-computational-music-theory-and-analysis-spring-2023/mit21m383s23_quiz_1.pdf" },
  { ResourceID: 3,Title: "Male northern cardinal in Central Park" ,Author: "khan accademy, lobster notes web scraper", Rating: "3", Date: "2025-11-11", Format: "Image", Url:"https://upload.wikimedia.org/wikipedia/commons/6/60/Male_northern_cardinal_in_Central_Park_%2852598%29.jpg" },
  { ResourceID: 4,Title: "text note" ,Author: "Nikki", Rating: "2", Date: "2025-11-27", Format: "Note", Body: "This is a sample text note created by Nikki in Lobster Notes application." },
  { ResourceID: 5,Title: "website note" ,Author: "Author5", Rating: "4", Date: "2024-05-05", Format: "Website", Url: "https://www.example.com" },
  { ResourceID: 6,Title: "test title6" ,Author: "Author6", Rating: "3", Date: "2024-06-15", Format: "PDF" },
  { ResourceID: 7,Title: "test title7" , Author: "Author7", Rating: "5", Date: "2024-07-22", Format: "PDF" },
  { ResourceID: 8,Title: "test title8" ,Author: "Author8", Rating: "4", Date: "2024-08-30", Format: "PDF" },
  { ResourceID: 9,Title: "test title9" ,Author: "Author9", Rating: "3", Date: "2024-09-15", Format: "PDF" },
  { ResourceID: 10,Title: "test title10" ,Author: "Author10", Rating: "4", Date: "2024-10-10", Format: "PDF" }
  
];
const sampleSearch = [
  { ResourceID: 1,Title: "Computational music theory" ,Author: "mit ocw, lobster notes web scraper", Rating: "5", Date: "2025-11-15", Format: "Video", Url:"https://ocw.mit.edu/courses/21m-383-computational-music-theory-and-analysis-spring-2023/21m383-s23-video1a_tutorial_360p_16_9.mp4" },
  { ResourceID: 2,Title: "Computational Music teory and Analysis QUIZ 1" ,Author: "mit ocw, lobster notes web scraper", Rating: "4", Date: "2025-11-15", Format: "PDF", Url:"https://ocw.mit.edu/courses/21m-383-computational-music-theory-and-analysis-spring-2023/mit21m383s23_quiz_1.pdf" },
  { ResourceID: 3,Title: "Male northern cardinal in Central Park" ,Author: "khan accademy, lobster notes web scraper", Rating: "3", Date: "2025-11-11", Format: "Image", Url:"https://upload.wikimedia.org/wikipedia/commons/6/60/Male_northern_cardinal_in_Central_Park_%2852598%29.jpg" },
  { ResourceID: 4,Title: "text note" ,Author: "Nikki", Rating: "2", Date: "2025-11-27", Format: "Note", Body: "This is a sample text note created by Nikki in Lobster Notes application." },
  { ResourceID: 5,Title: "website note" ,Author: "Author5", Rating: "4", Date: "2024-05-05", Format: "Website", Url: "https://www.example.com" },
]


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


function App(){
  const [route, setRoute] = useState({ name: 'list', id: null });
  const [searchActive, setSearchActive] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

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

    setSearchActive(false);
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
        <div style={{display: 'flex', alignItems: 'center', gap: '12px'}}>
          <div className="brand">Lobster Notes</div>
          <form onSubmit={(e) => { e.preventDefault(); setSearchActive(true); setRoute({ name: 'list', id: null }); }} style={{display:'flex', alignItems:'center', gap: '8px'}}>
            <input
              className="note-search"
              placeholder="Search notes..."
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              style={{padding: '6px 8px', borderRadius: 6, border: '1px solid #e6e9ef'}}
            />
            <button className="btn" type="submit">Search</button>
            <button className="btn" type="button" onClick={() => { setSearchQuery(''); setSearchActive(false); }}>Clear</button>
          </form>
        </div>
      </header>
      <main className="main">
        {searchActive ? (
          // pass sample notes rather than search for now
          <section style={{width: '100%'}}>
            <NoteList notes={sampleSearch} onOpenNote={openNote} />
          </section>
        ) : route.name === 'note' ? (
          <section className="note-full">
            <NotePage note={activeNote} onBack={goBack} />
          </section>
        ) : (
          <React.Fragment>
            <section className="left">
              <NoteEditor />
            </section>
            <section className="right">
              <NoteList notes={sampleNotes} onOpenNote={openNote} />
            </section>
          </React.Fragment>
        )}
      </main>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
