import { useEffect, useState } from "react";
import { getBrands } from "../services/api";

export default function Brands() {
  const [brands, setBrands] = useState([]);

  useEffect(() => {
    getBrands().then(res => setBrands(res.data));
  }, []);

  return (
    <div>
      <h2>🏷️ Brands</h2>
      <ul>
        {brands.map((b, i) => (
          <li key={i}>{b.brand}</li>
        ))}
      </ul>
    </div>
  );
}
