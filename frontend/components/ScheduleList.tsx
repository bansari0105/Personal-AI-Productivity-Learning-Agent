"use client";

import { useEffect, useState } from "react";
import { listScheduledTasks, deleteScheduledTask } from "@/lib/api";

interface ScheduleListProps {
  refreshTrigger?: any;
}

export default function ScheduleList({ refreshTrigger }: ScheduleListProps) {
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    const data = await listScheduledTasks();
    setItems(data);
    setLoading(false);
  };

  useEffect(() => {
    load();
    // re-run when parent notifies of new schedule
  }, [refreshTrigger]);

  const handleDelete = async (id: number) => {
    await deleteScheduledTask(id);
    load();
  };

  if (loading) {
    return <p>Loading schedule...</p>;
  }

  if (items.length === 0) {
    return <p>No scheduled tasks yet.</p>;
  }

  return (
    <div className="bg-white p-4 rounded shadow">
      <h2 className="text-xl font-semibold mb-4">Today's Schedule</h2>
      {items.map((it) => (
        <div
          key={it.id}
          className="border-b py-2 flex justify-between items-center"
        >
          <div>
            <p><strong>{it.task}</strong></p>
            <p className="text-sm text-gray-600">
              {it.start} – {it.end} ({it.duration_minutes} min)
            </p>
          </div>
          <button
            onClick={() => handleDelete(it.id)}
            className="text-red-500 hover:underline text-sm"
          >
            Delete
          </button>
        </div>
      ))}
    </div>
  );
}