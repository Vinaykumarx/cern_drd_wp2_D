"use client";

import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import { 
  Server, 
  Settings, 
  MessageSquare, 
  Activity, 
  Cpu, 
  Send, 
  FileText, 
  ExternalLink,
  Search,
  PlusCircle,
  Hash,
  Terminal,
  Zap,
  RefreshCw,
  Microscope,
  Plus,
  Brain,
  Shield,
  Layers,
  ChevronRight,
  Maximize2,
  Network
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import dynamic from 'next/dynamic';

const ForceGraph2D = dynamic(() => import('react-force-graph-2d'), { ssr: false });
const API_BASE = "/api";

export default function AgentZeroSwarm() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [sessions, setSessions] = useState<any[]>([]);
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [metrics, setMetrics] = useState<any>({
    vector_pages: 0,
    ingested_docs: 0,
    sqlite_sessions: 0,
    logs: []
  });
  const [pdfModal, setPdfModal] = useState<{ docId: string; page: number } | null>(null);
  const [swarmPulse, setSwarmPulse] = useState(0);
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [selectedModel, setSelectedModel] = useState("llama-3.3-70b-versatile");
  const [dimensions, setDimensions] = useState({ width: 1200, height: 800 });
  const [uploadStatus, setUploadStatus] = useState<string | null>(null);
  const [uploadDocs, setUploadDocs] = useState<any[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [docRelevance, setDocRelevance] = useState<any[]>([]);
  const [showRelevancePanel, setShowRelevancePanel] = useState(false);
  const [allDocuments, setAllDocuments] = useState<any[]>([]);
  const [showDocSelector, setShowDocSelector] = useState(false);
  const [docPreview, setDocPreview] = useState<any>(null);


  const bottomRef = useRef<HTMLDivElement>(null);
  const graphContainerRef = useRef<HTMLDivElement>(null);


  // Initialize
  useEffect(() => {
    fetchSessions();
    fetchMetrics();
    fetchGraphData();
    fetchUploadStatus(); // initial upload status fetch
    const interval = setInterval(fetchMetrics, 5000);
    const statusInterval = setInterval(fetchUploadStatus, 8000); // poll upload status

    const pulseInterval = setInterval(() => setSwarmPulse(p => (p + 1) % 100), 2000);

    const updateDimensions = () => {
        if (graphContainerRef.current) {
            setDimensions({
                width: graphContainerRef.current.clientWidth,
                height: graphContainerRef.current.clientHeight
            });
        }
    };
    window.addEventListener('resize', updateDimensions);
    updateDimensions();

    return () => {
        clearInterval(interval);
        clearInterval(statusInterval);
        clearInterval(pulseInterval);
        window.removeEventListener('resize', updateDimensions);
    };
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const fetchSessions = async () => {
    try {
      const res = await axios.get(`${API_BASE}/sessions`);
      setSessions(res.data);
      if (res.data.length > 0 && !sessionId) {
        setSessionId(res.data[0].id);
        fetchMessages(res.data[0].id);
      }
    } catch (err) {
      console.error("Failed to fetch sessions:", err);
    }
  };

  const fetchMessages = async (sid: string) => {
    try {
      const res = await axios.get(`${API_BASE}/chat/${sid}`);
      setMessages(res.data || []);
    } catch (err) {
      console.error("Failed to fetch messages:", err);
    }
  };

  const fetchMetrics = async () => {
    try {
      const res = await axios.get(`${API_BASE}/dashboard`);
      setMetrics(res.data);
    } catch (err) {
      console.error("Metrics unreachable");
    }
  };

  const fetchGraphData = async () => {
    try {
      const res = await axios.get(`${API_BASE}/knowledge_graph`);
      setGraphData(res.data);
    } catch (err) {
      console.log("Graph fetch failed:", err);
    }
  };

  const fetchDocRelevance = async (query: string) => {
    try {
      const res = await axios.get(`${API_BASE}/document_relevance?query=${encodeURIComponent(query)}`);
      setDocRelevance(res.data.documents || []);
    } catch (err) {
      console.log("Relevance fetch failed:", err);
    }
  };

  const injectDocument = async (docId: string) => {
    try {
      setUploadStatus(`⏳ Injecting ${docId}...`);
      const res = await axios.post(`${API_BASE}/ingest_document`, null, { params: { doc_id: docId } });
      if (res.data.success) {
        setUploadStatus(`✅ ${res.data.message}`);
        fetchMetrics();
      } else {
        setUploadStatus(`❌ ${res.data.message}`);
      }
    } catch (err: any) {
      setUploadStatus(`❌ Injection failed: ${err?.response?.data?.detail || err.message}`);
    }
  };

  const fetchAllDocuments = async () => {
    try {
      const res = await axios.get(`${API_BASE}/all_documents`);
      setAllDocuments(res.data.documents || []);
      setShowDocSelector(true);
    } catch (err) {
      console.log("Fetch documents failed:", err);
    }
  };

  // New: fetch upload status for all documents (processing, indexed, etc.)
  const fetchUploadStatus = async () => {
    try {
      const res = await axios.get(`${API_BASE}/upload_status`);
      setUploadDocs(res.data.documents || []);
    } catch (err) {
      console.log('Upload status fetch failed:', err);
    }
  };

  const previewDocument = async (docId: string) => {
    try {
      const res = await axios.get(`${API_BASE}/document_info?doc_id=${docId}`);
      setDocPreview(res.data);
    } catch (err) {
      console.log("Preview failed:", err);
    }
  };

  const uploadPdf = async (files: File | FileList | File[]) => {
    // Normalize to an array of File objects
    let fileArray: File[] = [];
    if (files instanceof File) {
      fileArray = [files];
    } else if (files instanceof FileList) {
      fileArray = Array.from(files);
    } else {
      fileArray = files;
    }
    // Filter PDF files only
    const pdfFiles = fileArray.filter((f) => f.name.toLowerCase().endsWith('.pdf'));
    if (pdfFiles.length === 0) {
      setUploadStatus('❌ Only PDF files are supported.');
      return;
    }

    // If a single file, keep previous behavior (shows simple status)
    if (pdfFiles.length === 1) {
      const file = pdfFiles[0];
      setUploadStatus(`⏳ Uploading ${file.name}...`);
      const formData = new FormData();
      formData.append('file', file);
      try {
        const res = await axios.post(`${API_BASE}/upload`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        setUploadStatus(`✅ ${res.data.message}`);
        setTimeout(fetchMetrics, 5000); // refresh metrics after 5s
      } catch (err: any) {
        setUploadStatus(`❌ Upload failed: ${err?.response?.data?.detail || err.message}`);
      }
      return;
    }

    // Multiple files: use the new bulk endpoint
    setUploadStatus('⏳ Uploading multiple PDFs...');
    const formData = new FormData();
    pdfFiles.forEach((f) => formData.append('files', f));
    try {
      const res = await axios.post(`${API_BASE}/upload_multiple`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      // Expect response shape: { results: [{filename, doc_id, status, message}] }
      const results = res.data.results || [];
      // Build a combined status string for UI
      const messages = results.map((r: any) => `${r.status === 'processing' ? '✅' : '❌'} ${r.filename}: ${r.message}`).join('\n');
      setUploadStatus(messages);
      // Refresh metrics after uploads are queued
      setTimeout(fetchMetrics, 5000);
    } catch (err: any) {
      setUploadStatus(`❌ Bulk upload failed: ${err?.response?.data?.detail || err.message}`);
    }
  };

  const createSession = async () => {
    try {
        const res = await axios.post(`${API_BASE}/sessions`, { title: "New Physics Inquiry" });
        setSessions([res.data, ...sessions]);
        setSessionId(res.data.id);
        setMessages([]);
        setActiveTab("chat");
    } catch (err) {
        console.error("Failed to create session:", err);
    }
  };

  const sendMessage = async () => {
    if (!input.trim()) return;
    
    // Auto-heal session if missing
    let currentSid = sessionId;
    if (!currentSid) {
        try {
            const res = await axios.post(`${API_BASE}/sessions`, { title: input.substring(0, 30) + "..." });
            currentSid = res.data.id;
            setSessionId(currentSid);
            setSessions([res.data, ...sessions]);
        } catch (err) {
            alert("Swarm offline. Please check backend.");
            return;
        }
    }

    const userMsg = { role: "user", content: input };
    setMessages(prev => [...prev, userMsg]);
    const queryToCheck = input;
    setInput("");
    setLoading(true);
    setShowRelevancePanel(true);

    try {
      const res = await axios.post(`${API_BASE}/chat`, {
        session_id: currentSid,
        message: queryToCheck,
        temperature: 0.1,
        model: selectedModel
      });
      setMessages(prev => [...prev, { 
          role: "assistant", 
          content: res.data.content,
          hits: res.data.hits,
          suggested_links: res.data.suggested_links
      }]);
      // Fetch document relevance after getting response
      fetchDocRelevance(queryToCheck);
    } catch (err) {
      setMessages(prev => [...prev, { role: "assistant", content: "⚠️ Neural link interrupted. Re-establishing connection..." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen w-screen bg-drift text-neutral-200 overflow-hidden font-sans">
      
      {/* 1. NEURAL SIDEBAR */}
      <div className="w-72 flex flex-col glass-panel border-r border-white/5 z-20">
        <div className="p-6">
            <div className="flex items-center gap-3 mb-8">
                <div className="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center animate-pulse-glow shadow-lg shadow-indigo-500/20">
                    <Brain className="text-white" size={22} />
                </div>
                <div>
                    <h1 className="font-bold tracking-tight text-white">AGENT ZERO</h1>
                    <div className="text-[10px] text-emerald-400 font-mono flex items-center gap-1.5 uppercase tracking-widest">
                        <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse"></span>
                        Neural Node Active
                    </div>
                </div>
            </div>

            <button 
                onClick={createSession}
                className="w-full flex items-center justify-center gap-2 py-3 px-4 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl transition-all shadow-lg shadow-indigo-600/20 font-semibold text-sm mb-8 active:scale-95"
            >
                <Plus size={18}/> New Inquiry
            </button>

            <nav className="space-y-1">
                <button 
                    onClick={() => setActiveTab("dashboard")}
                    className={`w-full flex items-center gap-3 p-3 rounded-xl transition-all text-sm group ${activeTab === 'dashboard' ? 'bg-white/10 text-white' : 'hover:bg-white/5 text-neutral-400'}`}
                >
                    <Server size={18} className={activeTab === 'dashboard' ? 'text-indigo-400' : 'group-hover:text-neutral-300'}/> 
                    Telemetry Hub
                </button>
                <button 
                    onClick={() => setActiveTab("chat")}
                    className={`w-full flex items-center gap-3 p-3 rounded-xl transition-all text-sm group ${activeTab === 'chat' ? 'bg-white/10 text-white' : 'hover:bg-white/5 text-neutral-400'}`}
                >
                    <MessageSquare size={18} className={activeTab === 'chat' ? 'text-indigo-400' : 'group-hover:text-neutral-300'}/> 
                    Neural Chat
                </button>
                <button 
                    onClick={() => setActiveTab("map")}
                    className={`w-full flex items-center gap-3 p-3 rounded-xl transition-all text-sm group ${activeTab === 'map' ? 'bg-white/10 text-white' : 'hover:bg-white/5 text-neutral-400'}`}
                >
                    <Network size={18} className={activeTab === 'map' ? 'text-indigo-400' : 'group-hover:text-neutral-300'}/> 
                    Neuro Map
                </button>
            </nav>

            <button 
                onClick={fetchAllDocuments}
                className="w-full mt-6 flex items-center justify-center gap-2 py-3 px-4 bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-400 border border-emerald-500/30 rounded-xl transition-all text-sm font-bold"
            >
                <FileText size={16}/> Document Library
            </button>

            <div className="mt-8">
                <div className="text-[10px] text-neutral-500 uppercase font-bold tracking-[0.2em] mb-4 px-3">History</div>
                <div className="space-y-1 max-h-[300px] overflow-y-auto custom-scrollbar pr-2">
                    {sessions.map((s) => (
                        <button 
                            key={s.id}
                            onClick={() => { setSessionId(s.id); fetchMessages(s.id); setActiveTab("chat"); }}
                            className={`w-full flex items-center gap-3 p-3 rounded-xl transition-all text-xs text-left group ${sessionId === s.id && activeTab === 'chat' ? 'bg-indigo-500/10 text-indigo-300' : 'hover:bg-white/5 text-neutral-500'}`}
                        >
                            <Hash size={14} className="shrink-0 opacity-50"/>
                            <span className="truncate">{s.title || "Observation Chunk"}</span>
                        </button>
                    ))}
                </div>
            </div>
        </div>

        {/* UPLOAD ZONE — NotebookLM style */}
        <div className="px-4 pb-2">
            <div
                onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
                onDragLeave={() => setIsDragging(false)}
                onDrop={(e) => {
                    e.preventDefault();
                    setIsDragging(false);
                    const files = e.dataTransfer.files;
                    if (files && files.length > 0) uploadPdf(files);
                }}
                onClick={() => { const i = document.createElement('input'); i.type='file'; i.accept='.pdf'; i.multiple = true; i.onchange = (e: any) => { const fileList = e.target.files as FileList; if (fileList && fileList.length > 0) uploadPdf(fileList); }; i.click(); }}
                className={`cursor-pointer border-2 border-dashed rounded-xl p-4 text-center transition-all ${isDragging ? 'border-indigo-400 bg-indigo-500/10' : 'border-white/10 hover:border-indigo-500/50 hover:bg-white/5'}`}
            >
                <div className="text-2xl mb-1">📄</div>
                <div className="text-[10px] text-neutral-400 font-semibold">Drop any PDF here</div>
                <div className="text-[9px] text-neutral-600 mt-0.5">Auto-extracts & indexes like NotebookLM</div>
            </div>
            {uploadStatus && (
                <div className={`mt-2 text-[10px] rounded-lg px-3 py-2 font-mono leading-snug ${uploadStatus.startsWith('✅') ? 'bg-emerald-500/10 text-emerald-400' : uploadStatus.startsWith('⏳') ? 'bg-indigo-500/10 text-indigo-400' : 'bg-red-500/10 text-red-400'}`}>
                    {uploadStatus}
                </div>
            )}
            {/* New: Show per-document upload processing status */}
            {uploadDocs.length > 0 && (
                <div className="mt-4">
                    <h4 className="text-xs font-bold text-neutral-400 uppercase mb-2">Upload & Index Status</h4>
                    <div className="space-y-2 max-h-48 overflow-y-auto custom-scrollbar">
                        {uploadDocs.map((doc, idx) => (
                            <div key={idx} className="flex items-center justify-between text-[10px] px-2 py-1 rounded bg-black/30 border border-white/10">
                                <span className="font-mono truncate max-w-[150px]">{doc.filename || doc.doc_id}</span>
                                <span className={`font-medium ${doc.status === 'indexed' ? 'text-emerald-400' : doc.status === 'processing' ? 'text-indigo-400' : 'text-yellow-400'}`}>{doc.status?.toUpperCase() || 'UNKNOWN'}</span>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>

        <div className="p-6 border-t border-white/5">
            <div className="glass-card p-4 rounded-2xl flex flex-col gap-3">
                <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-blue-600/20 flex items-center justify-center text-blue-400">
                        <Cpu size={16} />
                    </div>
                    <div className="text-[10px] font-bold text-white uppercase tracking-widest">Active Core</div>
                </div>
                <select 
                    value={selectedModel}
                    onChange={e => setSelectedModel(e.target.value)}
                    className="w-full bg-black/40 border border-white/10 text-white text-[11px] rounded-lg p-2 outline-none focus:border-indigo-500"
                >
                    <option value="llama-3.3-70b-versatile">⚡ Llama 3.3 70B (Primary)</option>
                    <option value="gemma4">🏠 Gemma 4 (Local Fallback)</option>
                    <option value="anthropic/claude-3.5-sonnet">Claude 3.5 Sonnet</option>
                    <option value="nousresearch/hermes-3-llama-3.1-405b">Hermes 3 405B</option>
                    <option value="google/gemma-2-27b-it">Gemma 2 27B (Requires OpenRouter key)</option>
                </select>
            </div>
        </div>

      </div>

      {/* 2. MAIN CONTENT AREA */}
      <div className="flex-1 flex flex-col relative overflow-hidden">
        
        {/* DASHBOARD TAB */}
        {activeTab === "dashboard" && (
          <div className="flex-1 overflow-y-auto p-12 custom-scrollbar">
            <div className="max-w-6xl mx-auto">
                <div className="flex items-center justify-between mb-12">
                    <div>
                        <h2 className="text-4xl font-extrabold text-white tracking-tight mb-2">Core Telemetry</h2>
                        <p className="text-neutral-400">Monitoring real-time ingestion and vector stability across the Swarm.</p>
                    </div>
                    <div className="flex gap-4">
                        <div className="glass-panel px-4 py-2 rounded-full flex items-center gap-2 text-xs font-mono">
                            <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
                            GPU: 48GB / 0.4ms
                        </div>
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
                    <div className="glass-card p-8 rounded-3xl relative overflow-hidden group">
                        <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                            <Layers size={80} />
                        </div>
                        <div className="text-neutral-400 text-xs font-bold uppercase tracking-widest mb-4">Vector Chunks</div>
                        <div className="text-5xl font-black text-white mb-2">{metrics.vector_pages || 0}</div>
                        <div className="text-[11px] text-blue-400 flex items-center gap-1">
                            <Zap size={12}/> High-Dimensional Sync
                        </div>
                    </div>

                    <div className="glass-card p-8 rounded-3xl relative overflow-hidden group">
                        <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                            <FileText size={80} />
                        </div>
                        <div className="text-neutral-400 text-xs font-bold uppercase tracking-widest mb-4">Physics Models</div>
                        <div className="text-5xl font-black text-white mb-2">{metrics.ingested_docs || 0}</div>
                        <div className="text-[11px] text-emerald-400 flex items-center gap-1">
                            <Shield size={12}/> Validated Registry
                        </div>
                    </div>

                    <div className="glass-card p-8 rounded-3xl relative overflow-hidden group">
                        <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                            <RefreshCw size={80} />
                        </div>
                        <div className="text-neutral-400 text-xs font-bold uppercase tracking-widest mb-4">Transactions</div>
                        <div className="text-5xl font-black text-white mb-2">{metrics.sqlite_sessions || 0}</div>
                        <div className="text-[11px] text-purple-400 flex items-center gap-1">
                            <Settings size={12}/> Active Session Persistence
                        </div>
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    <div className="space-y-6">
                        <h3 className="text-lg font-bold text-white flex items-center gap-2">
                            <Terminal size={20} className="text-indigo-400" />
                            Swarm Logs
                        </h3>
                        <div className="bg-black/80 rounded-3xl border border-white/5 p-6 font-mono text-[11px] h-[350px] overflow-y-auto custom-scrollbar shadow-inner">
                            {metrics.logs?.map((l: string, i: number) => (
                                <div key={i} className="mb-2 flex gap-4">
                                    <span className="text-neutral-600">[{new Date().toLocaleTimeString()}]</span>
                                    <span className="text-emerald-500/80">{l}</span>
                                </div>
                            ))}
                            {!metrics.logs?.length && <div className="text-neutral-600 italic">Listening to Orchestrator heartbeat...</div>}
                        </div>
                    </div>

                    <div className="space-y-6">
                        <h3 className="text-lg font-bold text-white flex items-center gap-2">
                            <Activity size={20} className="text-emerald-400" />
                            Inference Latency
                        </h3>
                        <div className="glass-card rounded-3xl p-8 flex flex-col items-center justify-center h-[350px]">
                            {/* Neural Pulse Visualization */}
                            <div className="relative w-48 h-48 flex items-center justify-center">
                                <div className="absolute inset-0 rounded-full border-2 border-indigo-500/20 animate-ping"></div>
                                <div className="absolute inset-4 rounded-full border-2 border-indigo-400/30 animate-pulse"></div>
                                <div className="w-24 h-24 rounded-full bg-indigo-600 flex items-center justify-center shadow-2xl shadow-indigo-600/50">
                                    <Zap size={40} className="text-white" />
                                </div>
                            </div>
                            <div className="mt-8 text-center">
                                <div className="text-2xl font-bold text-white">0.42 ms</div>
                                <div className="text-xs text-neutral-500 uppercase tracking-widest mt-1">Average Jitter</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
          </div>
        )}

        {/* CHAT TAB */}
        {activeTab === "chat" && (
          <div className="flex-1 flex flex-col h-full bg-black/20">
            
            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-8 space-y-10 custom-scrollbar pb-40">
                {messages.length === 0 && (
                    <div className="h-full flex flex-col items-center justify-center opacity-40">
                        <Microscope size={80} className="text-indigo-400 mb-6" />
                        <h3 className="text-2xl font-bold text-white">Awaiting Discovery</h3>
                        <p className="text-neutral-500 mt-2">The Swarm is ready to synthesize your scientific data.</p>
                    </div>
                )}
                
                {messages.map((m, i) => (
                    <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'} animate-in fade-in slide-in-from-bottom-2 duration-300`}>
                        <div className={`flex flex-col gap-3 max-w-[85%] ${m.role === 'user' ? 'items-end' : 'items-start'}`}>
                            <div className={`p-6 rounded-3xl shadow-2xl border ${
                                m.role === 'user' 
                                ? 'bg-indigo-600 border-indigo-500 text-white' 
                                : 'glass-panel border-white/10 text-neutral-200'
                            }`}>
                                <div className="markdown-body">
                                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                        {m.content}
                                    </ReactMarkdown>
                                </div>
                                <div className="flex gap-2 mt-2 flex-wrap">
                                    {m.content.match(/\[C\d+\]/g)?.filter((v: string, i: number, a: string[]) => a.indexOf(v) === i).map((cite: string, i: number) => (
                                        <button 
                                            key={i}
                                            onClick={() => {
                                                const hit = m.hits?.find((h: any) => h.citation_id === cite);
                                                if (hit) {
                                                    setPdfModal({ docId: hit.doc_id, page: hit.page || 1 });
                                                }
                                            }}
                                            className="px-2 py-0.5 rounded bg-indigo-500/20 border border-indigo-500/30 text-indigo-300 text-xs font-mono hover:bg-indigo-500/40 transition-colors flex items-center gap-1"
                                        >
                                            <span className="opacity-70 text-[10px]">SOURCE</span> {cite}
                                        </button>
                                    ))}
                                </div>
                            </div>

                            {/* SOURCE DISCOVERY LINKS */}
                            {m.suggested_links?.length > 0 && (
                                <div className="flex gap-2 flex-wrap mt-2">
                                    {m.suggested_links.map((link: any, idx: number) => (
                                        <button 
                                            key={idx}
                                            onClick={() => {
                                                if (link.url && link.url.startsWith('http')) {
                                                    window.open(link.url, '_blank');
                                                } else {
                                                    setPdfModal({ docId: link.doc_id, page: 1 });
                                                }
                                            }}
                                            className="glass-card px-4 py-2 rounded-full text-[10px] font-bold text-indigo-400 flex items-center gap-2 hover:bg-indigo-500/20 active:scale-95 transition-all"
                                        >
                                            <Search size={12}/> {link.filename}
                                            <ChevronRight size={10} className="opacity-50"/>
                                        </button>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                ))}
                
                {loading && (
                    <div className="flex justify-start animate-fade-in">
                        <div className="glass-panel p-4 rounded-3xl flex items-center gap-3">
                            <div className="flex gap-1.5">
                                <div className="w-2 h-2 bg-indigo-500 rounded-full animate-bounce"></div>
                                <div className="w-2 h-2 bg-indigo-500 rounded-full animate-bounce delay-75"></div>
                                <div className="w-2 h-2 bg-indigo-500 rounded-full animate-bounce delay-150"></div>
                            </div>
                            <span className="text-[10px] font-bold uppercase tracking-widest text-indigo-400">Synthesizing...</span>
                        </div>
                    </div>
                )}
                <div ref={bottomRef} className="h-4" />
            </div>

            {/* Input Pinned Box */}
            <div className="absolute bottom-10 left-10 right-10">
                <div className="max-w-4xl mx-auto glass-panel p-2 rounded-3xl flex items-center gap-2 shadow-2xl ring-1 ring-white/10">
                    <div className="flex items-center justify-center w-12 h-12 text-neutral-500 pl-2">
                        <Zap size={20} className={input ? "text-indigo-400" : ""} />
                    </div>
                    <input 
                        type="text" 
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); sendMessage(); } }}
                        placeholder="Inquire about particle physics, radiation safety, or system telemetry..."
                        className="flex-1 bg-transparent border-none outline-none text-white placeholder:text-neutral-600 text-sm py-4"
                    />
                    <button 
                        onClick={sendMessage}
                        disabled={loading || !input.trim()}
                        className={`w-12 h-12 flex items-center justify-center rounded-2xl transition-all ${input.trim() ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/30' : 'bg-white/5 text-neutral-600'}`}
                    >
                        <Send size={20} />
                    </button>
                </div>
                <div className="mt-3 text-center text-[9px] text-neutral-600 uppercase tracking-[0.3em]">
                    Powered by OpenRouter Claude / Hermes Intelligence Swarm • CERN Physics Safety Certified
                </div>

                {/* Document Relevance Panel */}
                {docRelevance.length > 0 && (
                    <div className="absolute bottom-32 left-10 right-10 max-w-4xl mx-auto">
                        <div className="glass-panel rounded-2xl p-4 border border-indigo-500/30">
                            <div className="flex items-center justify-between mb-3">
                                <h4 className="text-sm font-bold text-indigo-400 flex items-center gap-2">
                                    <Zap size={14} /> Document Relevance
                                </h4>
                                <button 
                                    onClick={() => { setDocRelevance([]); setShowRelevancePanel(false); }}
                                    className="text-neutral-500 hover:text-white text-xs"
                                >
                                    ✕
                                </button>
                            </div>
                            <div className="flex gap-2 flex-wrap">
                                {docRelevance.map((doc: any, idx: number) => (
                                    <div key={idx} className="flex items-center gap-2 bg-black/40 rounded-lg px-3 py-2 border border-white/10">
                                        <div className="flex flex-col">
                                            <span className="text-xs text-white font-medium truncate max-w-[150px]">{doc.filename}</span>
                                            <div className="flex items-center gap-2 mt-1">
                                                <div className="w-16 h-1.5 bg-neutral-700 rounded-full overflow-hidden">
                                                    <div 
                                                        className={`h-full rounded-full ${doc.relevance_percent > 50 ? 'bg-emerald-500' : doc.relevance_percent > 25 ? 'bg-yellow-500' : 'bg-red-500'}`}
                                                        style={{ width: `${Math.min(doc.relevance_percent, 100)}%` }}
                                                    />
                                                </div>
                                                <span className="text-[10px] text-neutral-400">{doc.relevance_percent}%</span>
                                                {doc.status !== 'indexed' && (
                                                    <button
                                                        onClick={() => injectDocument(doc.doc_id)}
                                                        className="ml-1 px-2 py-0.5 bg-indigo-600 hover:bg-indigo-500 text-white text-[9px] rounded font-bold"
                                                    >
                                                        Inject
                                                    </button>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                )}
            </div>
          </div>
        )}

        {/* MAP TAB */}
        {activeTab === "map" && (
          <div ref={graphContainerRef} className="flex-1 w-full h-full relative overflow-hidden" style={{ background: '#0a0a0a' }}>
             <div className="absolute top-10 left-10 z-10 glass-panel p-6 rounded-2xl pointer-events-none">
                 <h2 className="text-2xl font-bold text-white mb-2">Neuro-Map Context</h2>
                 <p className="text-sm text-neutral-400 max-w-sm mb-4">
                     Interactive force-directed graph of local memory chunks. Topics (purple), source documents (green), and embedded chunks (blue) cluster autonomously.
                 </p>
                 <button onClick={fetchGraphData} className="px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg text-xs font-bold uppercase cursor-pointer pointer-events-auto">
                    Sync Clusters
                 </button>
             </div>
             
             {graphData.nodes.length > 0 ? (
                 <ForceGraph2D
                    graphData={graphData}
                    width={dimensions.width}
                    height={dimensions.height}
                    nodeColor={node => {
                        if ((node as any).group === 1) return '#10b981'; // Green Doc
                        if ((node as any).group === 2) return '#8b5cf6'; // Purple Topic
                        return '#3b82f6'; // Blue Chunk
                    }}
                    nodeRelSize={6}
                    linkColor={() => 'rgba(255,255,255,0.1)'}
                    backgroundColor="#0a0a0a"
                 />
             ) : (
                 <div className="w-full h-full flex items-center justify-center text-neutral-500">
                    No graph data acquired. Is LanceDB populated?
                 </div>
             )}
          </div>
        )}

      </div>

      {/* PDF MODAL LIGHTBOX */}
      {pdfModal && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/90 backdrop-blur-sm p-12">
            <div className="w-full h-full max-w-7xl glass-panel rounded-3xl overflow-hidden flex flex-col">
                <div className="p-6 border-b border-white/5 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <FileText className="text-indigo-400" />
                        <h2 className="text-xl font-bold text-white tracking-tight">{pdfModal.docId}</h2>
                        <span className="text-xs text-neutral-500 uppercase font-bold bg-white/5 px-2 py-1 rounded">Page {pdfModal.page}</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <button className="p-2 hover:bg-white/10 rounded-lg text-neutral-400"><Maximize2 size={20}/></button>
                        <button 
                            onClick={() => setPdfModal(null)}
                            className="bg-white/10 hover:bg-red-500/20 text-neutral-100 hover:text-red-400 px-4 py-2 rounded-xl text-sm font-bold transition-all"
                        >
                            Close Swarm Viewer
                        </button>
                    </div>
                </div>
                <div className="flex-1 bg-neutral-900 overflow-hidden">
                    <iframe 
                        src={`/api/pdf/${pdfModal.docId}#page=${pdfModal.page}`}
                        className="w-full h-full border-none"
                    />
                </div>
            </div>
        </div>
      )}

      {/* DOCUMENT SELECTOR MODAL */}
      {showDocSelector && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/90 backdrop-blur-sm p-8">
            <div className="w-full max-w-4xl glass-panel rounded-3xl overflow-hidden flex flex-col max-h-[80vh]">
                <div className="p-6 border-b border-white/5 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <FileText className="text-indigo-400" />
                        <h2 className="text-xl font-bold text-white tracking-tight">Document Library</h2>
                    </div>
                    <button 
                        onClick={() => setShowDocSelector(false)}
                        className="bg-white/10 hover:bg-red-500/20 text-neutral-100 hover:text-red-400 px-4 py-2 rounded-xl text-sm font-bold transition-all"
                    >
                        Close
                    </button>
                </div>
                <div className="flex-1 overflow-y-auto p-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {allDocuments.map((doc: any, idx: number) => (
                            <div 
                                key={idx} 
                                className={`p-4 rounded-xl border cursor-pointer transition-all ${
                                    doc.status === 'indexed' 
                                    ? 'bg-emerald-500/10 border-emerald-500/30 hover:bg-emerald-500/20'
                                    : doc.file_exists
                                    ? 'bg-indigo-500/10 border-indigo-500/30 hover:bg-indigo-500/20'
                                    : 'bg-yellow-500/10 border-yellow-500/30 opacity-60'
                                }`}
                                onClick={() => doc.file_exists && previewDocument(doc.doc_id)}
                            >
                                <div className="flex items-start justify-between">
                                    <div className="flex-1">
                                        <h4 className="text-sm font-bold text-white truncate">{doc.filename}</h4>
                                        <div className="flex items-center gap-2 mt-2">
                                            <span className={`text-[10px] px-2 py-0.5 rounded font-bold ${
                                                doc.status === 'indexed' ? 'bg-emerald-500 text-white' :
                                                doc.status === 'registered' ? 'bg-indigo-500 text-white' :
                                                'bg-yellow-500 text-black'
                                            }`}>
                                                {doc.status.toUpperCase()}
                                            </span>
                                            {doc.file_exists && (
                                                <span className="text-[10px] text-neutral-400">Ready to inject</span>
                                            )}
                                            {!doc.file_exists && (
                                                <span className="text-[10px] text-yellow-400">File missing</span>
                                            )}
                                        </div>
                                    </div>
                                    {doc.file_exists && doc.status !== 'indexed' && (
                                        <button
                                            onClick={(e) => { e.stopPropagation(); injectDocument(doc.doc_id); }}
                                            className="px-3 py-1 bg-indigo-600 hover:bg-indigo-500 text-white text-xs rounded font-bold"
                                        >
                                            Inject
                                        </button>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
      )}

      {/* DOCUMENT PREVIEW MODAL */}
      {docPreview && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/90 backdrop-blur-sm p-8">
            <div className="w-full max-w-lg glass-panel rounded-3xl overflow-hidden flex flex-col">
                <div className="p-6 border-b border-white/5 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <FileText className="text-indigo-400" />
                        <h2 className="text-xl font-bold text-white tracking-tight">Document Preview</h2>
                    </div>
                    <button 
                        onClick={() => setDocPreview(null)}
                        className="bg-white/10 hover:bg-red-500/20 text-neutral-100 hover:text-red-400 px-4 py-2 rounded-xl text-sm font-bold transition-all"
                    >
                        Close
                    </button>
                </div>
                <div className="p-6 space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="text-[10px] text-neutral-500 uppercase font-bold">Filename</label>
                            <p className="text-sm text-white">{docPreview.filename}</p>
                        </div>
                        <div>
                            <label className="text-[10px] text-neutral-500 uppercase font-bold">Status</label>
                            <p className={`text-sm font-bold ${docPreview.status === 'indexed' ? 'text-emerald-400' : 'text-indigo-400'}`}>
                                {docPreview.status?.toUpperCase()}
                            </p>
                        </div>
                        <div>
                            <label className="text-[10px] text-neutral-500 uppercase font-bold">File Size</label>
                            <p className="text-sm text-white">{docPreview.file_size_mb} MB</p>
                        </div>
                        <div>
                            <label className="text-[10px] text-neutral-500 uppercase font-bold">File Exists</label>
                            <p className={`text-sm font-bold ${docPreview.file_exists ? 'text-emerald-400' : 'text-red-400'}`}>
                                {docPreview.file_exists ? 'YES' : 'NO'}
                            </p>
                        </div>
                    </div>
                    <div className="pt-4 border-t border-white/10">
                        <label className="text-[10px] text-neutral-500 uppercase font-bold">Path</label>
                        <p className="text-xs text-neutral-400 break-all">{docPreview.path}</p>
                    </div>
                    {docPreview.url && (
                        <div className="pt-4 border-t border-white/10">
                            <label className="text-[10px] text-neutral-500 uppercase font-bold">External URL</label>
                            <a href={docPreview.url} target="_blank" className="text-xs text-indigo-400 hover:underline block truncate">
                                {docPreview.url}
                            </a>
                        </div>
                    )}
                </div>
                <div className="p-6 border-t border-white/5 flex justify-end gap-3">
                    <button 
                        onClick={() => setDocPreview(null)}
                        className="px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-xl text-sm font-bold"
                    >
                        Cancel
                    </button>
                    {docPreview.file_exists && docPreview.status !== 'indexed' && (
                        <button 
                            onClick={() => { injectDocument(docPreview.doc_id); setDocPreview(null); }}
                            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-sm font-bold"
                        >
                            Inject Document
                        </button>
                    )}
                </div>
            </div>
        </div>
      )}

      {/* GLOBAL GLOW EFFECTS */}
      <div className="fixed top-[-20%] right-[-10%] w-[60%] h-[60%] bg-indigo-600/10 blur-[120px] pointer-events-none rounded-full"></div>
      <div className="fixed bottom-[-10%] left-[-10%] w-[40%] h-[40%] bg-purple-600/5 blur-[100px] pointer-events-none rounded-full"></div>
    </div>
  );
}
