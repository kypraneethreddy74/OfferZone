import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { compareByModel } from "../services/api";
import "./CompareResult.css";

/* ⭐ STAR RATING */
const StarRating = ({ rating }) => {
  const stars = Math.round(rating || 0);
  return (
    <div className="star-rating">
      {[1, 2, 3, 4, 5].map(i => (
        <span
          key={i}
          className={i <= stars ? "star filled" : "star"}
        >
          ★
        </span>
      ))}
      <span className="rating-text">
        {rating ? rating.toFixed(1) : "NA"}
      </span>
    </div>
  );
};

function CompareResult() {
  const { modelId } = useParams();
  const navigate = useNavigate();

  const [items, setItems] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!modelId || modelId === "undefined") {
      setError("Invalid TV selected. Please go back and select again.");
      return;
    }

    compareByModel(modelId)
      .then(res => setItems(res.data))
      .catch(() => {
        setError("No comparison data found for this TV.");
      });
  }, [modelId]);

  if (error) {
    return (
      <div className="container py-4">
        <button className="btn btn-link mb-3" onClick={() => navigate(-1)}>
          ← Back
        </button>
        <div className="alert alert-warning">{error}</div>
      </div>
    );
  }

  return (
    <div className="container py-4">
      <button className="btn btn-link mb-3" onClick={() => navigate(-1)}>
        ← Back
      </button>

      <h4 className="mb-4">TV Price Comparison</h4>

      <div className="row g-4">
        {items.map((p, i) => (
          <div className="col-md-6 col-lg-4" key={i}>
            <div className="card tv-compare-card h-100 shadow-sm">

              {/* IMAGE */}
              <div className="tv-image-wrapper">
                <img
                  src={p.image_url || "/tv-placeholder.png"}
                  alt={p.full_name}
                  className="tv-image"
                />
              </div>

              <div className="card-body">

                {/* TITLE */}
                <h6 className="tv-title">
                  {p.full_name}
                </h6>

                {/* RATING */}
                <StarRating rating={p.rating} />

                {/* DISPLAY */}
                <span className="badge bg-dark mb-2">
                  {p.display_type || "NA"}
                </span>

                {/* MODEL */}
                <div className="text-muted small mb-1">
                  Model ID: <strong>{p.model_id}</strong>
                </div>

                {/* PLATFORMS */}
                <div className="text-muted small mb-2">
                  Available on: <strong>{p.platform_count}</strong> platforms
                </div>

                {/* PRICE */}
                <div className="price-box">
                  <div className="best-price">
                    ₹{p.sale_price?.toLocaleString()}
                  </div>

                  {p.mrp && (
                    <div className="text-muted small">
                      <del>₹{p.mrp.toLocaleString()}</del>{" "}
                      <span className="text-danger fw-bold">
                        {p.discount_percent}% off
                      </span>
                    </div>
                  )}

                  {p.savings && (
                    <div className="text-success small">
                      Save up to ₹{p.savings.toLocaleString()}
                    </div>
                  )}
                </div>

                {/* PLATFORM */}
                <div className="mt-2">
                  <span className="badge bg-secondary">
                    {p.platform}
                  </span>
                </div>

                {/* STOCK */}
                <span
                  className={`badge mt-2 ${
                    p.stock_status === "in_stock"
                      ? "bg-success"
                      : "bg-danger"
                  }`}
                >
                  {p.stock_status === "in_stock"
                    ? "In Stock"
                    : "Out of Stock"}
                </span>

              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default CompareResult;
