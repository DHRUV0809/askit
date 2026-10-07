import { useEffect, useRef, useState } from "react";
import { ask, tts } from "./api";
import SearchBox from "./components/SearchBox.jsx";
import AgentStatus from "./components/AgentStatus.jsx";
import AnswerCard from "./components/AnswerCard.jsx";
import SourceList from "./components/SourceList.jsx";
import AudioPlayer from "./components/AudioPlayer.jsx";

export default function App() {
  const [phase, setPhase] = useState("idle"); // idle | running | done | error
  const [stage, setStage] = useState(0); // 0 researcher, 1 writer, 2 editor, 3 all done
  const [query, setQuery] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [audio, setAudio] = useState({ url: "", loading: false, error: "" });
  const timers = useRef([]);

  const clearTimers = () => { timers.current.forEach(clearTimeout); timers.current = []; };
  useEffect(() => clearTimers, []);

  async function loadAudio(text) {
    setAudio({ url: "", loading: true, error: "" });
    try {
      setAudio({ url: await tts(text), loading: false, error: "" });
    } catch (e) {
      setAudio({ url: "", loading: false, error: e.message });
    }
  }

  async function onSubmit(q) {
    clearTimers();
    setQuery(q); setResult(null); setError(""); setStage(0); setPhase("running");
    setAudio({ url: "", loading: false, error: "" });
    // Stage display is simulated from backend stages (the API call itself is synchronous).
    timers.current = [setTimeout(() => setStage(1), 7000), setTimeout(() => setStage(2), 15000)];
    try {
      const data = await ask(q);
      clearTimers();
      setStage(3); setResult(data); setPhase("done");
      loadAudio(data.answer);
    } catch (e) {
      clearTimers();
      setError(e.message); setPhase("error");
    }
  }

  function reset() {
    clearTimers();
    setPhase("idle"); setResult(null); setError(""); setQuery("");
    setAudio({ url: "", loading: false, error: "" });
  }

  return (
    <div className="app">
      <header className="header">
        <h1>ASKIT</h1>
        <p className="subtitle">AI-Powered Multi-Agent Research Assistant</p>
        <p className="tagline">Ask anything. Research everything.</p>
      </header>

      <main className="main">
        {phase === "idle" || phase === "error" ? <SearchBox onSubmit={onSubmit} initial={query} /> : null}
        {phase === "error" && <div className="card error" role="alert">{error}</div>}

        {phase !== "idle" && phase !== "error" && (
          <div className="card question"><span className="label">Your question</span><p>{query}</p></div>
        )}
        {phase === "running" && <p className="researching">Researching...</p>}
        {phase !== "idle" && phase !== "error" && <AgentStatus stage={stage} />}

        {phase === "done" && result && (
          <>
            <AnswerCard answer={result.answer} time={result.processing_time} />
            <SourceList sources={result.sources} />
            <AudioPlayer {...audio} onRetry={() => loadAudio(result.answer)} />
            <button className="btn secondary" onClick={reset}>New Research</button>
          </>
        )}
      </main>

      <footer className="footer">ASKIT · CrewAI · FastAPI · n8n · ElevenLabs</footer>
    </div>
  );
}
