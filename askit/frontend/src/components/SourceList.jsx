export default function SourceList({ sources = [] }) {
  const safe = sources.filter((s) => /^https?:\/\//i.test(s.url));
  return (
    <section className="card">
      <span className="label">Sources</span>
      {safe.length === 0 ? (
        <p className="muted">No sources were returned for this answer.</p>
      ) : (
        <ol className="sources">
          {safe.map((s) => (
            <li key={s.url}>
              <a href={s.url} target="_blank" rel="noopener noreferrer">{s.title}</a>
            </li>
          ))}
        </ol>
      )}
    </section>
  );
}
