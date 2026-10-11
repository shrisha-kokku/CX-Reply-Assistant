import { useEffect, useState } from "react";
import { api } from "./api";
import ConversationList from "./components/ConversationList";
import ChatView from "./components/ChatView";
import KBManager from "./components/KBManager";
import Logs from "./components/Logs";

const TABS = [
  ["agent", "Agent view"],
  ["customer", "Customer view"],
  ["kb", "Knowledge base"],
  ["logs", "Logs"],
];

export default function App() {
  const [tab, setTab] = useState("agent");
  const [conversations, setConversations] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [error, setError] = useState("");

  function loadConversations() {
    api
      .listConversations()
      .then((list) => {
        setConversations(list);
        setSelectedId((current) => current ?? (list.length ? list[0].id : null));
      })
      .catch((e) => setError(e.message));
  }

  useEffect(() => {
    loadConversations();
  }, []);

  const isChatTab = tab === "agent" || tab === "customer";

  return (
    <div className="app">
      <header className="topbar">
        <h1>CX Reply Assistant</h1>
        <nav>
          {TABS.map(([key, label]) => (
            <button key={key} className={tab === key ? "tab active" : "tab"} onClick={() => setTab(key)}>
              {label}
            </button>
          ))}
        </nav>
      </header>

      {error && <p className="error">Could not reach the server: {error}</p>}

      {isChatTab && (
        <div className="layout">
          <ConversationList conversations={conversations} selectedId={selectedId} onSelect={setSelectedId} />
          {selectedId && (
            <ChatView
              key={selectedId}
              conversationId={selectedId}
              mode={tab}
              onChanged={loadConversations}
            />
          )}
        </div>
      )}
      {tab === "kb" && <KBManager />}
      {tab === "logs" && <Logs />}
    </div>
  );
}
