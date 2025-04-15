"use client";

import { useState } from "react";

export default function Home() {
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState({ past: "", current: "" });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await fetch("http://127.0.0.1:8000/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: "user123", query }),
      });
      const data = await res.json();
      const [past, current] = data.response.split("\nCurrent response:");
      setResponse({ past: past || "", current: current || "" });
    } catch (error) {
      setResponse({ past: "", current: "Error: Could not fetch response" });
    }
    setLoading(false);
  };

  const handleStartNewChat = async () => {
    try {
      await fetch("http://127.0.0.1:8000/memory/user123", {
        method: "DELETE",
      });
      setResponse({ past: "", current: "New chat started" });
    } catch (error) {
      setResponse({ past: "", current: "Error: Could not start new chat" });
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-gray-100 p-6 flex flex-col items-center">
      <h1 className="text-4xl font-extrabold text-blue-800 mb-8">Market Sentiment Agent</h1>
      <form onSubmit={handleSubmit} className="w-full max-w-lg bg-white rounded-lg shadow-lg p-6 mb-8">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask about sentiment or trends (e.g., AI, energy sector)..."
          className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 mb-4 text-black"
        />
        <button
          type="submit"
          disabled={loading}
          className="w-full p-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 transition-colors duration-200"
        >
          {loading ? "Loading..." : "Submit"}
        </button>
      </form>
      <button
        onClick={handleStartNewChat}
        className="mb-8 p-3 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors duration-200"
      >
        Start a New Chat
      </button>
      {(response.past || response.current) && (
        <div className="w-full max-w-lg space-y-6">
          {response.past && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-lg font-semibold text-black mb-2">Past Context</h2>
              <pre className="text-sm text-black whitespace-pre-wrap">{response.past}</pre>
            </div>
          )}
          {response.current && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-lg font-semibold text-black mb-2">Current Response</h2>
              <pre className="text-sm text-black whitespace-pre-wrap">{response.current}</pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}