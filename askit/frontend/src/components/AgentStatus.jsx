const AGENTS = ["Researcher", "Writer", "Editor"];

function label(i, stage) {
  if (i < stage) return { text: "Completed ✓", cls: "done" };
  if (i === stage) return { text: "Running...", cls: "running" };
  return { text: "Waiting", cls: "waiting" };
}

export default function AgentStatus({ stage }) {
  return (
    <div className="card pipeline" aria-label="Agent pipeline">
      {AGENTS.map((name, i) => {
        const s = label(i, stage);
        return (
          <div key={name} className={`agent ${s.cls}`}>
            <span className="agent-name">{name}</span>
            <span className="agent-state">{s.text}</span>
            {i < AGENTS.length - 1 && <span className="arrow" aria-hidden="true">→</span>}
          </div>
        );
      })}
    </div>
  );
}
