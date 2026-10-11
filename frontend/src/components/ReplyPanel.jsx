import { useState } from "react";

const CONFIDENCE_LABEL = {
  high: "High confidence",
  low: "Low confidence",
  none: "No knowledge found",
};

// Shows the AI suggestion. The agent can edit it, regenerate it, or approve it.
export default function ReplyPanel({ generation, busy, onRegenerate, onApprove }) {
  const [draft, setDraft] = useState(generation.ai_reply || "");

  return (
    <section className="reply-panel">
      <div className="reply-head">
        <h3>Suggested reply</h3>
        <span className={`conf ${generation.confidence}`}>{CONFIDENCE_LABEL[generation.confidence]}</span>
      </div>

      {generation.needs_review && (
        <p className="warning">Needs review before sending. {generation.note}</p>
      )}
      {!generation.needs_review && generation.note && <p className="note">{generation.note}</p>}

      <textarea className="draft" value={draft} onChange={(e) => setDraft(e.target.value)} />

      <div className="row">
        <button className="primary" disabled={busy || !draft.trim()} onClick={() => onApprove(draft)}>
          Approve and send
        </button>
        <button disabled={busy} onClick={onRegenerate}>
          {busy ? "Working..." : "Regenerate"}
        </button>
      </div>

      <h4>Knowledge used</h4>
      {generation.retrieved_context.length === 0 && <p className="note">No knowledge base entries matched this question.</p>}
      {generation.retrieved_context.map((e) => (
        <div key={e.id} className={e.used ? "kb-card used" : "kb-card"}>
          <strong>{e.title}</strong> {e.used && <span className="badge">used by AI</span>}
          <p>{e.content}</p>
        </div>
      ))}
    </section>
  );
}
