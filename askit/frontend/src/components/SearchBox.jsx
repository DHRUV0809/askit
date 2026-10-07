import { useState } from "react";

export default function SearchBox({ onSubmit, initial = "" }) {
  const [value, setValue] = useState(initial);
  const submit = (e) => {
    e.preventDefault();
    const q = value.trim();
    if (q) onSubmit(q);
  };
  return (
    <div className="card">
      <div className="searchbox">
        <textarea
          rows={3}
          maxLength={5000}
          placeholder="Ask me anything..."
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) submit(e); }}
          aria-label="Your question"
        />
        <button className="btn" onClick={submit} disabled={!value.trim()}>Research</button>
      </div>
    </div>
  );
}
