import { useEffect, useState } from "react";
import { api } from "../api";
import ReplyPanel from "./ReplyPanel";

// mode = "customer": send messages as the customer (to test the loop)
// mode = "agent":    generate AI replies or send a manual message
export default function ChatView({ conversationId, mode, onChanged }) {
  const [convo, setConvo] = useState(null);
  const [text, setText] = useState("");
  const [generation, setGeneration] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  function load() {
    api.getConversation(conversationId).then(setConvo).catch((e) => setError(e.message));
  }

  useEffect(load, [conversationId]);

  async function send(sender) {
    if (!text.trim()) return;
    setError("");
    try {
      await api.sendMessage(conversationId, sender, text);
      setText("");
      load();
      onChanged();
    } catch (e) {
      setError(e.message);
    }
  }

  async function generate() {
    setBusy(true);
    setError("");
    try {
      setGeneration(await api.generateReply(conversationId));
    } catch (e) {
      setError(e.message);
    }
    setBusy(false);
  }

  async function approve(finalText) {
    setBusy(true);
    setError("");
    try {
      await api.approveReply(generation.id, finalText);
      setGeneration(null);
      load();
      onChanged();
    } catch (e) {
      setError(e.message);
    }
    setBusy(false);
  }

  if (!convo) return <main className="chat">Loading...</main>;

  const { customer, brand, order, messages, latest_customer_message } = convo;

  return (
    <main className="chat">
      <div className="chat-header">
        <h2>{customer.name}</h2>
        <span className="badge">{brand.name}</span>
        {order && (
          <p className="order">
            Order: {order.product} | Rs {order.amount} | {order.status}
            {order.delivered_at && ` | delivered ${new Date(order.delivered_at).toLocaleString()}`}
          </p>
        )}
      </div>

      <div className="messages">
        {messages.map((m) => (
          <div key={m.id} className={`bubble ${m.sender}`}>
            <small>
              {m.sender === "customer" ? "Customer" : "Agent"}
              {m.sent_by_ai && " (AI-assisted)"}
            </small>
            {m.body}
          </div>
        ))}
      </div>

      {error && <p className="error">{error}</p>}

      {mode === "customer" && (
        <div className="composer">
          <textarea value={text} onChange={(e) => setText(e.target.value)} placeholder="Type a message as the customer..." />
          <button onClick={() => send("customer")}>Send as customer</button>
        </div>
      )}

      {mode === "agent" && (
        <>
          {latest_customer_message && (
            <div className="latest">
              <small>Latest customer message</small>
              {latest_customer_message.body}
            </div>
          )}

          <button className="primary" onClick={generate} disabled={busy || !latest_customer_message}>
            {busy && !generation ? "Generating..." : "Generate Reply"}
          </button>

          {generation && (
            <ReplyPanel
              key={generation.id}
              generation={generation}
              busy={busy}
              onRegenerate={generate}
              onApprove={approve}
            />
          )}

          <div className="composer">
            <textarea value={text} onChange={(e) => setText(e.target.value)} placeholder="Or write a manual reply (no AI)..." />
            <button onClick={() => send("agent")}>Send manual message</button>
          </div>
        </>
      )}
    </main>
  );
}
