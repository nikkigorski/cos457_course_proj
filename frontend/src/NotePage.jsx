import React, { useState, useEffect } from 'react';

function NotePage({ noteId, note, resource, onBack, user, apiBaseUrl }) {
  const [resourceData, setResourceData] = useState(resource || note || null);
  const [loading, setLoading] = useState(false);
  const [ratingScore, setRatingScore] = useState('');
  const [ratingMessage, setRatingMessage] = useState('');
  const [submittingRating, setSubmittingRating] = useState(false);

  // Fetch resource details from API if noteId provided and no initial data
  useEffect(() => {
    if (noteId && !note && !resource && apiBaseUrl) {
      const fetchResource = async () => {
        setLoading(true);
        try {
          const response = await fetch(`${apiBaseUrl}/resources/${noteId}`);
          if (response.ok) {
            const data = await response.json();
            setResourceData(data);
          } else {
            console.error('Failed to fetch resource details');
          }
        } catch (error) {
          console.error('Error fetching resource:', error);
        } finally {
          setLoading(false);
        }
      };
      fetchResource();
    } else if (note || resource) {
      setResourceData(note || resource);
    }
  }, [noteId, note, resource, apiBaseUrl]);

  const data = resourceData;

  if (loading) {
    return (
      <div>
        <h2>Loading...</h2>
        <button className="btn" onClick={onBack}>Back</button>
      </div>
    );
  }

  if (!data) {
    return (
      <div>
        <h2>Note</h2>
        <p>Note not found.</p>
        <button className="btn" onClick={onBack}>Back</button>
      </div>
    );
  }

  const title = data.Title || 'Untitled';
  const author = data.Author || 'Unknown';
  const rating = data.Rating || '—';
  const date = data.Date || 'Unknown';
  const format = data.Format || 'Unknown';
  const link = data.Url || '';
  const body = data.Body || '';

  const handleRatingSubmit = async (e) => {
    e.preventDefault();
    
    if (!ratingScore || !apiBaseUrl || !noteId) {
      setRatingMessage('Please enter a rating');
      return;
    }

    const score = parseFloat(ratingScore);
    if (isNaN(score) || score < 0 || score > 5) {
      setRatingMessage('Rating must be between 0 and 5');
      return;
    }

    setSubmittingRating(true);
    setRatingMessage('');

    try {
      const response = await fetch(`${apiBaseUrl}/resources/${noteId}/ratings`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          Poster: user?.username || 'Anonymous',
          Score: score,
          Date: new Date().toISOString().split('T')[0],
        }),
      });

      if (response.ok) {
        setRatingMessage('Rating submitted successfully!');
        setRatingScore('');
        
        // Refresh resource data to get updated rating
        const refreshResponse = await fetch(`${apiBaseUrl}/resources/${noteId}`);
        if (refreshResponse.ok) {
          const updatedData = await refreshResponse.json();
          setResourceData(updatedData);
        }
      } else {
        const error = await response.json();
        setRatingMessage(`Error: ${error.error || 'Failed to submit rating'}`);
      }
    } catch (error) {
      console.error('Error submitting rating:', error);
      setRatingMessage('Error: Failed to submit rating');
    } finally {
      setSubmittingRating(false);
    }
  };

  return (
    <div className="note-page">
      <h2>{title}</h2>

      <div className="note-meta" style={{ color: 'var(--muted)', marginBottom: '12px' }}>
        <div><strong>Author:</strong> {author}</div>
        <div><strong>Rating:</strong> {rating}</div>
        <div><strong>Date:</strong> {date}</div>
        <div><strong>Format:</strong> {format}</div>
      </div>

      {String(format).toLowerCase() === 'pdf' && link ? (
        <div className="note-pdf" style={{ marginBottom: '12px' }}>
          <iframe
            src={link}
            title={title + ' — PDF'}
            style={{ width: '100%', height: '720px', border: 'none' }}
          />
          <div style={{ color: 'var(--muted)', marginTop: '8px' }}>
            If the PDF doesn't display, <a href={link} download>download here</a>.
          </div>
        </div>
      ) : null}

      {String(format).toLowerCase() === 'image' && link ? (
        <div className="note-image" style={{ marginBottom: '12px' }}>
          <img src={link} alt={title} style={{ width: '100%', borderRadius: 8 }} />
          <div style={{ color: 'var(--muted)', marginTop: '8px' }}>{title}</div>
        </div>
      ) : null}

      {String(format).toLowerCase() === 'note' && body ? (
        <div className="note-body" style={{ marginBottom: '12px', whiteSpace: 'pre-wrap' }}>
          {body}
        </div>
      ) : null}

      {String(format).toLowerCase() === 'website' && link ? (
        <div className="note-website" style={{ marginBottom: '12px' }}>
          <a href={link} target="_blank" rel="noopener noreferrer">{link}</a>
        </div>
      ) : null}

      {String(format).toLowerCase() === 'video' && link ? (
        <div className="note-video" style={{ marginBottom: '12px' }}>
          {(/youtube\.com|youtu\.be/).test(link) ? (
            (() => {
              let embed = link;
              if (embed.includes('watch?v=')) embed = embed.replace('watch?v=', 'embed/');
              if (embed.includes('youtu.be/')) embed = embed.replace('youtu.be/', 'www.youtube.com/embed/');
              if (!/^https?:\/\//.test(embed)) embed = 'https://' + embed;
              return (
                <div style={{ position: 'relative', paddingBottom: '56.25%', height: 0 }}>
                  <iframe
                    src={embed}
                    title={title}
                    style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%' }}
                    frameBorder="0"
                    allow="autoplay; encrypted-media; picture-in-picture"
                    allowFullScreen
                  />
                </div>
              );
            })()
          ) : (
            <video controls style={{ width: '100%' }} src={link}>
              Your browser does not support the video tag.
            </video>
          )}
        </div>
      ) : null}

      <div style={{ marginTop: '1.5rem', padding: '1rem', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
        <h3 style={{ marginTop: 0 }}>Rate this resource</h3>
        <form onSubmit={handleRatingSubmit} style={{ display: 'flex', gap: '8px', alignItems: 'flex-start' }}>
          <input
            type="number"
            min="0"
            max="5"
            step="0.1"
            value={ratingScore}
            onChange={(e) => setRatingScore(e.target.value)}
            placeholder="0.0 - 5.0"
            style={{ padding: '8px', borderRadius: '4px', border: '1px solid #ccc', width: '120px' }}
            disabled={submittingRating}
          />
          <button 
            type="submit" 
            className="btn btn-primary"
            disabled={submittingRating}
          >
            {submittingRating ? 'Submitting...' : 'Submit Rating'}
          </button>
        </form>
        {ratingMessage && (
          <div style={{ 
            marginTop: '8px', 
            padding: '8px', 
            borderRadius: '4px',
            backgroundColor: ratingMessage.includes('Error') ? '#f8d7da' : '#d4edda',
            color: ratingMessage.includes('Error') ? '#721c24' : '#155724'
          }}>
            {ratingMessage}
          </div>
        )}
      </div>

      <div style={{ marginTop: '1rem' }}>
        <button className="btn" onClick={onBack}>Back</button>
      </div>
    </div>
  );
}

export default NotePage;