export default function ConversationList({ conversations, selectedId, onSelect }) {
  return (
    <aside className="sidebar">
      <h2>Conversations</h2>
      {conversations.map((c) => (
        <button
          key={c.id}
          className={c.id === selectedId ? "convo active" : "convo"}
          onClick={() => onSelect(c.id)}
        >
          <strong>{c.customer_name}</strong>
          <span className="badge">{c.brand_name}</span>
          <p>{c.last_message}</p>
        </button>
      ))}
    </aside>
  );
}
