"use client";

import { useState } from "react";
import Header from "@/components/Header";
import TaskInput from "@/components/TaskInput";
import AgentOutput from "@/components/AgentOutput";
import ScheduleForm from "@/components/ScheduleForm";
import ScheduleList from "@/components/ScheduleList";

export default function Home() {
  const [results, setResults] = useState([]);
  const [schedule, setSchedule] = useState<any[]>([]);

  return (
    <main className="p-6 max-w-4xl mx-auto">
      <Header />

      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-4">Agent Runner</h2>
        <TaskInput setResults={setResults} />
        <AgentOutput results={results} />
      </section>

      <section>
        <ScheduleForm onScheduled={(items) => setSchedule(items)} />
        {schedule.length > 0 && (
          <p className="text-green-700 mb-4">
            Scheduled {schedule.length} task{schedule.length > 1 ? "s" : ""}.
          </p>
        )}
        <ScheduleList refreshTrigger={schedule} />
      </section>
    </main>
  );
}
