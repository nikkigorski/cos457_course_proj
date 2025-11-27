function NotePage({ note, onBack }) {
  if (!note) {
    return (
      <div>
        <h2>Note</h2>
        <p>Note not found.</p>
        <button className="btn" onClick={onBack}>Back</button>
      </div>
    );
  }

  return (
    <div className="note-page">
      <h2>{note.Title}</h2>
      <div className="note-content">
        <p>Displaying note details for ResourceID: {note.ResourceID}</p>
      </div>
      <div style={{ marginTop: '1rem' }}>
        <button className="btn" onClick={onBack}>Back</button>
      </div>
    </div>
  );
}