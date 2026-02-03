import React, { useEffect, useState } from "react";
import {
  getPlatformList,
  getBrandsByPlatform,
  getModelsByPlatformBrand
} from "../services/api";
import "./Catalog.css";

export default function Catalog() {
  const [platforms, setPlatforms] = useState([]);
  const [brands, setBrands] = useState([]);
  const [models, setModels] = useState([]);

  const [selectedPlatform, setSelectedPlatform] = useState(null);
  const [selectedBrand, setSelectedBrand] = useState(null);
  const [page, setPage] = useState(1);

  const pageSize = 20;

  useEffect(() => {
    getPlatformList().then(res => setPlatforms(res.data));
  }, []);

  const selectPlatform = async (platform) => {
    setSelectedPlatform(platform);
    setSelectedBrand(null);
    setModels([]);
    setPage(1);

    const res = await getBrandsByPlatform(platform);
    setBrands(res.data);
  };

  const selectBrand = async (brand) => {
    setSelectedBrand(brand);
    setPage(1);

    const res = await getModelsByPlatformBrand(
      selectedPlatform,
      brand,
      1,
      pageSize
    );
    setModels(res.data);
  };

  const changePage = async (newPage) => {
    setPage(newPage);
    const res = await getModelsByPlatformBrand(
      selectedPlatform,
      selectedBrand,
      newPage,
      pageSize
    );
    setModels(res.data);
  };

  return (
    <div className="catalog">
      <h2>TV Catalog</h2>

      {/* PLATFORMS */}
      <div className="platforms">
        {platforms.map(p => (
          <button
            key={p}
            className={p === selectedPlatform ? "active" : ""}
            onClick={() => selectPlatform(p)}
          >
            {p.toUpperCase()}
          </button>
        ))}
      </div>

      <div className="content">
        {/* BRANDS */}
        <div className="brands">
          <h4>Brands</h4>
          {brands.map(b => (
            <div
              key={b}
              className={`brand ${b === selectedBrand ? "active" : ""}`}
              onClick={() => selectBrand(b)}
            >
              {b}
            </div>
          ))}
        </div>

        {/* MODELS */}
        <div className="models">
          <h4>Models</h4>

          <table>
            <thead>
              <tr>
                <th>Model</th>
                <th>Price</th>
                <th>Rating</th>
                <th>Stock</th>
              </tr>
            </thead>
            <tbody>
              {models.map(m => (
                <tr key={m.model_id + m.platform}>
                  <td>{m.full_name}</td>
                  <td>₹{m.sale_price}</td>
                  <td>{m.rating}</td>
                  <td>{m.stock_status}</td>
                </tr>
              ))}
            </tbody>
          </table>

          {/* PAGINATION */}
          {models.length > 0 && (
            <div className="pagination">
              <button
                disabled={page === 1}
                onClick={() => changePage(page - 1)}
              >
                ◀ Prev
              </button>

              <span>Page {page}</span>

              <button
                disabled={models.length < pageSize}
                onClick={() => changePage(page + 1)}
              >
                Next ▶
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
