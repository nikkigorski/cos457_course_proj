const { useState } = React;

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

function NoteList(){
  return (
    
    <div className="note-list">
      <h2>My Notes</h2>
      <div className="notes">No notes yet — create one.</div>
    </div>
  );
}

function App(){
  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">Lobster Notes — Notes</div>
      </header>
      <main className="main">
        <section className="left">
          <NoteEditor />
        </section>
        <section className="right">
          <NoteList />
        </section>
      </main>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
