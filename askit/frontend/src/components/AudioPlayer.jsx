export default function AudioPlayer({ url, loading, error, onRetry }) {
  return (
    <section className="card">
      <span className="label">🔊 Listen to Answer</span>
      {loading && <p className="muted">Generating voice response...</p>}
      {error && (
        <p className="muted">
          {error} <button className="link" onClick={onRetry}>Retry</button>
        </p>
      )}
      {url && <audio controls src={url} style={{ width: "100%", marginTop: 8 }} />}
    </section>
  );
}
