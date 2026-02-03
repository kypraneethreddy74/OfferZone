import { useEffect, useState } from "react";

export default function SearchBar({ onSearch }) {
  const [value, setValue] = useState("");

  useEffect(() => {
    const t = setTimeout(() => onSearch(value), 500);
    return () => clearTimeout(t);
  }, [value]);

  return (
    <input
      placeholder="Search brand..."
      value={value}
      onChange={e => setValue(e.target.value)}
      style={{ padding: 8, marginBottom: 10 }}
    />
  );
}
