function inline(text) {
  return text.split(/(\*\*[^*]+\*\*)/g).map((p, i) =>
    p.startsWith("**") && p.endsWith("**") ? <strong key={i}>{p.slice(2, -2)}</strong> : p
  );
}

// Tiny safe Markdown renderer (headings, bullets, bold). No raw HTML is ever injected.
function render(text) {
  const out = [];
  let list = [];
  const flush = () => {
    if (list.length) {
      out.push(<ul key={`u${out.length}`}>{list.map((l, i) => <li key={i}>{inline(l)}</li>)}</ul>);
      list = [];
    }
  };
  text.split("\n").forEach((raw) => {
    const line = raw.trim();
    if (!line) return flush();
    const bullet = line.match(/^[-*•]\s+(.*)/);
    if (bullet) return list.push(bullet[1]);
    flush();
    const h = line.match(/^#{1,6}\s+(.*)/);
    out.push(h ? <h3 key={out.length}>{inline(h[1])}</h3> : <p key={out.length}>{inline(line)}</p>);
  });
  flush();
  return out;
}

export default function AnswerCard({ answer, time }) {
  return (
    <section className="card">
      <div className="card-head">
        <span className="label">Final answer</span>
        {time != null && <span className="meta">{time}s</span>}
      </div>
      <div className="answer">{render(answer)}</div>
    </section>
  );
}
