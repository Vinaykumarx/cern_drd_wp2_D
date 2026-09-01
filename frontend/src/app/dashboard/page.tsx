"use client";

import { useEffect, useState } from 'react';
import Head from 'next/head';

type Service = {
  name: string;
  ok: boolean;
  detail?: string;
};

export default function Dashboard() {
  const [services, setServices] = useState<Service[]>([]);
  const [log, setLog] = useState<string>('');
  const [running, setRunning] = useState<boolean>(false);

  // Poll FastAPI's /api/dashboard_status endpoint every 5s
  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const res = await fetch('/api/dashboard_status');
        if (res.ok) {
          const data = await res.json();
          setServices(data.services);
        }
      } catch (err) {
        console.error("Dashboard offline", err);
      }
    };
    fetchStatus();
    const interval = setInterval(fetchStatus, 15000);

    return () => clearInterval(interval);
  }, []);

  // Send autonomous task request to Gemma 4 (Python Backend)
  const runAgentTask = async (taskName: string, instruction: string) => {
    setRunning(true);
    setLog(`[Initiating Task]: ${taskName}...\nWaiting for Autonomous reasoning...`);
    try {
      const res = await fetch('/api/agent', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task: taskName, instruction }),
      });
      const data = await res.json();
      setLog(`[Completed]: ${taskName}\n\nAgent Response:\n${data.agent_response}\n\nInternal Action Executed:\n${JSON.stringify(data.tool_result, null, 2)}`);
    } catch (e: any) {
      setLog(`[ERROR]: ${e.message}`);
    } finally {
      setRunning(false);
    }
  };

  return (
    <>
      <div style={{ maxWidth: '1000px', margin: '2rem auto', padding: '1rem', fontFamily: 'Inter, sans-serif' }}>
        <h1 style={{ fontSize: '2.5rem', color: '#0f62fe', textAlign: 'center' }}>🧪 Autonomous Scientific Agent</h1>
        <p style={{ textAlign: 'center', color: '#666', marginBottom: '2rem' }}>Powered natively by Claude 3.5 & Hermes 3 (OpenRouter)</p>

        {/* System Health */}
        <div style={{ background: '#f4f4f4', padding: '1.5rem', borderRadius: '12px', marginBottom: '2rem', boxShadow: '0 4px 12px rgba(0,0,0,0.05)' }}>
          <h2 style={{ marginBottom: '1rem', borderBottom: '2px solid #ddd', paddingBottom: '0.5rem' }}>System Integrity Check</h2>
          <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
            {services.length > 0 ? services.map(s => (
              <div key={s.name} style={{ background: '#fff', padding: '1rem', borderRadius: '8px', minWidth: '200px', borderLeft: `6px solid ${s.ok ? '#28a745' : '#dc3545'}`, boxShadow: '0 2px 5px rgba(0,0,0,0.02)' }}>
                <strong>{s.name}</strong><br/>
                <span style={{ color: s.ok ? '#28a745' : '#dc3545', fontWeight: 'bold' }}>{s.ok ? '✅ ONLINE' : '❌ OFFLINE'}</span>
              </div>
            )) : <p>Checking metrics...</p>}
          </div>
        </div>

        {/* Action Panel */}
        <div style={{ background: '#f4f4f4', padding: '1.5rem', borderRadius: '12px', marginBottom: '2rem', boxShadow: '0 4px 12px rgba(0,0,0,0.05)' }}>
          <h2 style={{ marginBottom: '1rem', borderBottom: '2px solid #ddd', paddingBottom: '0.5rem' }}>Agent Operations</h2>
          <p style={{ marginBottom: '1rem', color: '#555' }}>Issue high-level commands to Hermes 3. It will autonomously execute data structuring jobs in the background.</p>
          <div style={{ display: 'flex', gap: '1rem' }}>
            <button 
              disabled={running} 
              style={{ padding: '0.8rem 1.5rem', background: '#0f62fe', color: '#fff', border: 'none', borderRadius: '8px', cursor: running ? 'not-allowed' : 'pointer', fontWeight: 'bold' }}
              onClick={() => runAgentTask("reindex", "Scan the outputs folder and ensure LanceDB's vector store is fully up to date.")}
            >
              🔄 Reindex Vector DB
            </button>
            <button 
              disabled={running} 
              style={{ padding: '0.8rem 1.5rem', background: '#42a5f5', color: '#fff', border: 'none', borderRadius: '8px', cursor: running ? 'not-allowed' : 'pointer', fontWeight: 'bold' }}
              onClick={() => runAgentTask("review", "Reflect on the backend logs and give a short 2-sentence summary of recent operations.")}
            >
              🧠 Self-Review Logs
            </button>
          </div>
        </div>

        {/* Live Terminal */}
        <div style={{ background: '#111', padding: '1.5rem', borderRadius: '12px', color: '#0f0', minHeight: '200px', fontFamily: 'monospace', boxShadow: 'inset 0 0 10px #000' }}>
          <h3 style={{ margin: '0 0 1rem 0', color: '#888', textTransform: 'uppercase', fontSize: '0.8rem' }}>Agent Console Details</h3>
          <pre style={{ whiteSpace: 'pre-wrap', wordWrap: 'break-word', margin: 0 }}>
            {log || 'No tasks dispatched. Agent is sleeping.'}
          </pre>
        </div>
      </div>
    </>
  );
}
