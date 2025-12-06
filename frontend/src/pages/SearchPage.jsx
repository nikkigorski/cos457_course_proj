import React from 'react';
import NoteList from '../NoteList.jsx';
import { sampleNotes } from '../data';

export default function SearchPage({ notes = sampleNotes, onOpenNote = () => {}, onBack = () => {}, user = {}, loading = false }){
  return (
    <div style={{width: '100%'}}>
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8}}>
        <h2 style={{margin: 0}}>Notes found{notes && notes.length > 0 ? ` (${notes.length})` : ''}</h2>
        <div>
          <button className="btn" onClick={onBack}>Back</button>
        </div>
      </div>
      {loading ? (
        <p>Searching...</p>
      ) : notes && notes.length > 0 ? (
        <NoteList notes={notes} onOpenNote={onOpenNote} user={user} filterByUser={false} />
      ) : (
        <p>No notes found. Try a different search term.</p>
      )}
    </div>
  );
}
