import React, { useEffect, useState } from "react";
import { getProducts } from "../services/api";

function Products() {
  const [products, setProducts] = useState([]);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");

  useEffect(() => {
    const timer = setTimeout(() => {
      getProducts({ page }).then(res => setProducts(res.data));
    }, 500); // debounce

    return () => clearTimeout(timer);
  }, [page, search]);

  return (
    <div style={{ padding: 20 }}>
      <h2>Products</h2>

      <input
        placeholder="Search brand..."
        onChange={(e) => setSearch(e.target.value)}
      />

      <table border="1" width="100%">
        <thead>
          <tr>
            <th>Brand</th>
            <th>Model</th>
            <th>Price</th>
          </tr>
        </thead>
        <tbody>
          {products.map((p, i) => (
            <tr key={i}>
              <td>{p.brand}</td>
              <td>{p.model_id}</td>
              <td>₹{p.sale_price}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <button onClick={() => setPage(p => p - 1)} disabled={page === 1}>
        Prev
      </button>
      <button onClick={() => setPage(p => p + 1)}>
        Next
      </button>
    </div>
  );
}

export default Products;
