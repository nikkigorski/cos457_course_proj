import React from 'react';
import NoteList from '../NoteList.jsx';
import { sampleNotes } from '../data';

export default function SearchPage({ notes = sampleNotes, onOpenNote = () => {}, onBack = () => {}, user = {} }){
  return (
    <div style={{width: '100%'}}>
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8}}>
        <h2 style={{margin: 0}}>Notes found</h2>
        <div>
          <button className="btn" onClick={onBack}>Back</button>
        </div>
      </div>
      <NoteList notes={notes} onOpenNote={onOpenNote} user={user} />
    </div>
  );
}
