function NotePage({ note, resource, onBack }) {
  const data = resource || note || null;

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
  const Link = data.Url || '';
  

  return (
    <div className="note-page">
      <h2>{title}</h2>

      <div className="note-meta" style={{ color: 'var(--muted)', marginBottom: '12px' }}>
        <div><strong>Author:</strong> {author}</div>
        <div><strong>Rating:</strong> {rating}</div>
        <div><strong>Date:</strong> {date}</div>
        <div><strong>Format:</strong> {format}</div>
      </div>

      {String(format).toLowerCase() === 'pdf' && Link ? (
        <div className="note-pdf" style={{ marginBottom: '12px' }}>
          <iframe
            src={Link}
            title={title + ' — PDF'}
            style={{ width: '100%', height: '720px', border: 'none' }}
          />
          <div style={{ color: 'var(--muted)', marginTop: '8px' }}>
            If the PDF doesn't display, <a href={Link} download>download here</a>.
          </div>
        </div>
      ) : null}

      {String(format).toLowerCase() === 'video' && Link ? (
        <div className="note-video" style={{ marginBottom: '12px' }}>
          {(/youtube\.com|youtu\.be/).test(Link) ? (
            (() => {
              let embed = Link;
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
            <video controls style={{ width: '100%' }} src={Link}>
              Your browser does not support the video tag.
            </video>
          )}
        </div>
      ) : null}

      <div style={{ marginTop: '1rem' }}>
        <button className="btn" onClick={onBack}>Back</button>
      </div>
    </div>
  );
}