"use client";

import { useState } from "react";
import { runAgent } from "@/lib/api";

export default function TaskInput({ setResults }: any) {
  const [text, setText] = useState("");

  const handleRun = async () => {
    const data = await runAgent(text);
    setResults(data);
  };

  return (
    <div className="bg-white p-4 rounded shadow mb-6">
      <textarea
        className="w-full border p-2 rounded"
        rows={4}
        placeholder="Enter your tasks..."
        value={text}
        onChange={(e) => setText(e.target.value)}
      />
      <button
        onClick={handleRun}
        className="mt-4 bg-black text-white px-4 py-2 rounded"
      >
        Run Agent
      </button>
    </div>
  );
}
