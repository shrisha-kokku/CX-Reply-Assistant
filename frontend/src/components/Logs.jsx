import { useEffect, useState } from "react";
import { api } from "../api";

// Read-only view of every "Generate Reply" click (the audit trail).
export default function Logs() {
  const [logs, setLogs] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api.listLogs().then(setLogs).catch((e) => setError(e.message));
  }, []);

  return (
    <div className="page">
      <h2>AI reply logs</h2>
      {error && <p className="error">{error}</p>}
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Time</th><th>Customer message</th><th>KB entries</th><th>AI reply</th>
              <th>Edited reply</th><th>Final reply</th><th>Confidence</th><th>Status</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((l) => (
              <tr key={l.id}>
                <td>{new Date(l.created_at).toLocaleString()}</td>
                <td>{l.customer_message}</td>
                <td>{l.retrieved_context.map((e) => e.title).join(", ") || "none"}</td>
                <td>{l.ai_reply}</td>
                <td>{l.edited_reply || "-"}</td>
                <td>{l.final_reply || "-"}</td>
                <td>{l.confidence}</td>
                <td>{l.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
