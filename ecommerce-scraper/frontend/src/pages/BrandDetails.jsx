import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import "./Details.css";

const BrandDetails = () => {
  const { brandName } = useParams();
  const [tvs, setTvs] = useState([]);

  useEffect(() => {
    fetch(`http://localhost:8000/products/filter?brand=${brandName}`)
      .then(r => r.json())
      .then(setTvs);
  }, [brandName]);

  return (
    <div className="details-page">
      <h2> {brandName} TVs</h2>

      <div className="card-grid">
        {tvs.map(tv => (
          <div key={tv.model_id} className="detail-card">
            <h3>{tv.full_name}</h3>
            <p><b>Price:</b> ₹{tv.sale_price}</p>
            <p><b>Rating:</b> ⭐ {tv.rating}</p>
            <p><b>Display:</b> {tv.display_type}</p>
            <p><b>Platform:</b> {tv.platform}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default BrandDetails;
