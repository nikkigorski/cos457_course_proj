const express = require('express');
const fs = require('fs');
const path = require('path');
const bodyParser = require('body-parser');
const cors = require('cors');

const app = express();
const DATA_FILE = path.join(__dirname, 'notes.json');

app.use(cors());
app.use(bodyParser.json());

// Serve frontend static files from ../frontend/public when present
app.use(express.static(path.join(__dirname, '..', 'frontend', 'public')));

function loadNotes(){
  try{
    const raw = fs.readFileSync(DATA_FILE, 'utf8');
    return JSON.parse(raw);
  }catch(e){
    return [];
  }
}

function saveNotes(notes){
  try{
    fs.writeFileSync(DATA_FILE, JSON.stringify(notes, null, 2), 'utf8');
  }catch(e){
    console.error('Failed to save notes', e);
  }
}

let notes = loadNotes();
let nextId = notes.reduce((m, n) => Math.max(m, n.id || 0), 0) + 1;

app.get('/api/notes', (req, res) => {
  res.json(notes);
});

app.post('/api/notes', (req, res) => {
  const { title, body } = req.body || {};
  const note = { id: nextId++, title: title || 'Untitled', body: body || '', created: new Date().toISOString() };
  notes.push(note);
  saveNotes(notes);
  res.json(note);
});

app.delete('/api/notes/:id', (req, res) => {
  const id = parseInt(req.params.id, 10);
  notes = notes.filter(n => n.id !== id);
  saveNotes(notes);
  res.json({ ok: true });
});

// Fallback to index.html for SPA
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, '..', 'frontend', 'public', 'index.html'));
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server listening on http://localhost:${PORT}`));
