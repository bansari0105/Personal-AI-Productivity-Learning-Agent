"use client";

import { useState } from "react";
import { scheduleTasks } from "@/lib/api";

interface ScheduleFormProps {
  onScheduled: (items: any[]) => void;
}

export default function ScheduleForm({ onScheduled }: ScheduleFormProps) {
  const [text, setText] = useState("");
  const [start, setStart] = useState("09:00");
  const [end, setEnd] = useState("17:00");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!text.trim()) return;
    setLoading(true);
    const payload: any = { text, start_time: start, end_time: end };
    const data = await scheduleTasks(payload);
    onScheduled(data);
    setLoading(false);
  };

  return (
    <div className="bg-white p-4 rounded shadow mb-6">
      <h2 className="text-xl font-semibold mb-4">Schedule Tasks</h2>

      <label className="block mb-2">
        <span className="text-sm font-medium">Task description</span>
        <textarea
          className="w-full border p-2 rounded mt-1"
          rows={3}
          placeholder="E.g. study, gym, meeting"
          value={text}
          onChange={(e) => setText(e.target.value)}
        />
      </label>

      <div className="flex gap-4 mb-4">
        <label className="block">
          <span className="text-sm font-medium">Start time</span>
          <input
            type="time"
            value={start}
            onChange={(e) => setStart(e.target.value)}
            className="border p-2 rounded mt-1"
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium">End time</span>
          <input
            type="time"
            value={end}
            onChange={(e) => setEnd(e.target.value)}
            className="border p-2 rounded mt-1"
          />
        </label>
      </div>

      <button
        onClick={handleSubmit}
        disabled={loading}
        className="bg-black text-white px-4 py-2 rounded"
      >
        {loading ? "Scheduling..." : "Create Schedule"}
      </button>
    </div>
  );
}