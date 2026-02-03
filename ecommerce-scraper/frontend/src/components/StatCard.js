export default function StatCard({ title, value }) {
  return (
    <div style={{
      padding: 20,
      background: "#111827",
      color: "white",
      borderRadius: 12,
      width: 180
    }}>
      <h4>{title}</h4>
      <h1>{value}</h1>
    </div>
  );
}
