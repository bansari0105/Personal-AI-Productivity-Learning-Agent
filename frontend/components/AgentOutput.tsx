export default function AgentOutput({ results }: any) {
  if (!results.length) return null;

  return (
    <div>
      {results.map((item: any, idx: number) => (
        <div
          key={idx}
          className="bg-white p-4 rounded shadow mb-4"
        >
          <p><strong>Task:</strong> {item.task}</p>
          <p><strong>Action Intensity:</strong> {item.action.toFixed(2)}</p>
          <p><strong>Reward:</strong> {item.reward.toFixed(2)}</p>
        </div>
      ))}
    </div>
  );
}
