// frontend/src/App.js
import React, { useState } from 'react';
import axios from 'axios';
import { Upload, Send, FileText, Briefcase, Search, Loader2 } from 'lucide-react';

const API_BASE = "http://127.0.0.1:8000";

function App() {
  const [messages, setMessages] = useState([{ role: 'assistant', text: "Hello! Upload your CV and a Job Description to get started." }]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [cvUploaded, setCvUploaded] = useState(false);

  const handleUpload = async (e, type) => {
    const file = e.target.files[0];
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);
    formData.append("doc_type", type); // Send 'cv' or 'jd'
    try {
      setLoading(true);
      await axios.post(`${API_BASE}/upload`, formData);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        text: `✅ ${type.toUpperCase()} indexed: ${file.name}. I'm ready to use this context!` 
      }]);
    } catch (err) {
      alert("Upload failed. Check backend console.");
    } finally {
      setLoading(false);
    }
  };

  const handleQuery = async () => {
    if (!input) return;
    setLoading(true);
    const userMsg = { role: 'user', text: input };
    setMessages(prev => [...prev, userMsg]);
    try {
        const res = await axios.get(`${API_BASE}/agent`, { params: { question: input } });
        console.log("Backend Raw Response:", res.data); // <--- ADD THIS

        // Check if the key is 'response' or 'answer' or 'output'
        const botText = res.data.response || res.data.output || "I processed your request but have no text to display.";
        
        setMessages(prev => [...prev, { role: 'assistant', text: botText }]);
    } catch (err) {
        setMessages(prev => [...prev, { role: 'assistant', text: "Error: Could not reach the AI." }]);
    } finally {
        setLoading(false);
        setInput("");
    }
  };

  return (
    <div className="flex h-screen bg-slate-900 text-white font-sans">
      {/* Sidebar */}
      <div className="w-64 bg-slate-800 p-6 flex flex-col gap-6 border-r border-slate-700">
        <div className="flex flex-col gap-6">
          {/* Master CV Section */}
          <div className="flex flex-col gap-2">
            <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Your Profile</label>
            <label className="flex items-center gap-2 p-3 bg-blue-900/30 border border-blue-500/50 rounded-xl cursor-pointer hover:bg-blue-900/50 transition group">
              <FileText size={18} className="text-blue-400" />
              <div className="flex flex-col">
                <span className="text-sm font-medium">Update Master CV</span>
                <span className="text-[10px] text-slate-400">Main source of truth</span>
              </div>
              <input type="file" className="hidden" onChange={(e) => handleUpload(e, 'cv')} />
            </label>
          </div>

          {/* Job Description Section */}
          <div className="flex flex-col gap-2">
            <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Target Job</label>
            <label className="flex items-center gap-2 p-3 bg-emerald-900/30 border border-emerald-500/50 rounded-xl cursor-pointer hover:bg-emerald-900/50 transition group">
              <Upload size={18} className="text-emerald-400" />
              <div className="flex flex-col">
                <span className="text-sm font-medium">Upload Job JD</span>
                <span className="text-[10px] text-slate-400">Used for tailoring</span>
              </div>
              <input type="file" className="hidden" onChange={(e) => handleUpload(e, 'jd')} />
            </label>
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        <div className="flex-1 overflow-y-auto p-8 space-y-4">
          {messages.map((m, i) => (
            <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] p-4 rounded-2xl ${m.role === 'user' ? 'bg-blue-600' : 'bg-slate-800 border border-slate-700'}`}>
                <p className="text-sm whitespace-pre-line">{m.text}</p>
              </div>
            </div>
          ))}
          {loading && <div className="flex justify-start"><Loader2 className="animate-spin text-slate-500" /></div>}
        </div>

        {/* Input Bar */}
        <div className="p-6 bg-slate-900 border-t border-slate-800">
          <div className="max-w-4xl mx-auto relative">
            <input 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleQuery()}
              placeholder="Ask to tailor your CV or find jobs..."
              className="w-full bg-slate-800 border border-slate-700 rounded-xl py-4 px-6 focus:outline-none focus:ring-2 focus:ring-blue-500 pr-16"
            />
            <button 
              onClick={handleQuery}
              className="absolute right-3 top-3 p-2 bg-blue-600 rounded-lg hover:bg-blue-500 transition"
            >
              <Send size={20} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;