import React from 'react';
import NoteList from '../NoteList.jsx';
import { sampleNotes } from '../data';

export default function SearchPage({ notes = sampleNotes, onOpenNote = () => {}, user = {} }){
  return (
    <div style={{width: '100%'}}>
      <h2>Notes found</h2>
      <NoteList notes={notes} onOpenNote={onOpenNote} user={user} />
    </div>
  );
}
