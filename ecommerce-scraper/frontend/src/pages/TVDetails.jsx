import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import "./Details.css";

const TVDetails = () => {
  const { modelId } = useParams();
  const [items, setItems] = useState([]);

  useEffect(() => {
    fetch(`http://localhost:8000/products/compare?model_id=${modelId}`)
      .then(r => r.json())
      .then(data => setItems(Array.isArray(data) ? data : []));
  }, [modelId]);

  if (!items.length) return null;

  /* ================= PLATFORM ANALYTICS ================= */

  const lowestPrice = Math.min(...items.map(i => i.sale_price));
  const highestPrice = Math.max(...items.map(i => i.sale_price));
  const avgPrice =
    items.reduce((s, i) => s + i.sale_price, 0) / items.length;

  const bestDiscount = Math.max(...items.map(i => i.discount || 0));
  const bestRating = Math.max(...items.map(i => i.rating || 0));

  const cheapestPlatform = items.find(i => i.sale_price === lowestPrice);
  const expensivePlatform = items.find(i => i.sale_price === highestPrice);

  return (
    <div className="details-page">
      <h2> {items[0].full_name}</h2>

      {/* ================= PLATFORM ANALYTICS ================= */}
      <div className="card-grid" style={{ marginBottom: "24px" }}>
        <div className="detail-card">
          <h3>Lowest Price</h3>
          <p><b>Platform:</b> {cheapestPlatform.platform}</p>
          <p><b>Price:</b> ₹{lowestPrice}</p>
        </div>

        <div className="detail-card">
          <h3>Highest Price</h3>
          <p><b>Platform:</b> {expensivePlatform.platform}</p>
          <p><b>Price:</b> ₹{highestPrice}</p>
        </div>

        <div className="detail-card">
          <h3>Average Price</h3>
          <p><b>₹{Math.round(avgPrice)}</b></p>
        </div>

        <div className="detail-card">
          <h3>Best Discount</h3>
          <p><b>{bestDiscount}%</b></p>
        </div>

        <div className="detail-card">
          <h3>Best Rating</h3>
          <p><b>⭐ {bestRating}</b></p>
        </div>
      </div>

      {/* ================= PLATFORM LISTINGS ================= */}
      <h3 style={{ marginBottom: "14px" }}>🛒 Available Platforms</h3>

      <div className="card-grid">
        {items.map((tv, i) => (
          <div key={i} className="detail-card">
            <p><b>Platform:</b> {tv.platform}</p>
            <p><b>Price:</b> ₹{tv.sale_price}</p>
            <p><b>Discount:</b> {tv.discount}%</p>
            <p><b>Rating:</b> ⭐ {tv.rating}</p>

            <a href={tv.product_url} target="_blank" rel="noreferrer">
              View on {tv.platform}
            </a>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TVDetails;
