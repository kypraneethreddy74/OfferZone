import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Filters.css";

function Filters() {
  const [brand, setBrand] = useState("");
  const [minPrice, setMinPrice] = useState("");
  const [maxPrice, setMaxPrice] = useState("");
  const [screenSize, setScreenSize] = useState("");
  const [displayType, setDisplayType] = useState("");

  const navigate = useNavigate();

  const applyFilters = () => {
    navigate("/compare", {
      state: {
        brand,
        min_price: minPrice || null,
        max_price: maxPrice || null,
        screen_size: screenSize || null,
        display_type: displayType || null,
      },
    });
  };

  return (
    <div className="filters-container">
      <h1 className="filters-title">Filter TVs</h1>

      <div className="filters-form">
        {/* BRAND */}
        <input
          className="filters-input"
          placeholder="Brand (e.g. Samsung)"
          value={brand}
          onChange={(e) => setBrand(e.target.value)}
        />

        {/* MIN PRICE */}
        <input
          className="filters-input"
          type="number"
          placeholder="Min Price"
          value={minPrice}
          onChange={(e) => setMinPrice(e.target.value)}
        />

        {/* MAX PRICE */}
        <input
          className="filters-input"
          type="number"
          placeholder="Max Price"
          value={maxPrice}
          onChange={(e) => setMaxPrice(e.target.value)}
        />

        {/* SCREEN SIZE */}
        <select
          className="filters-input"
          value={screenSize}
          onChange={(e) => setScreenSize(e.target.value)}
        >
          <option value="">Screen Size</option>
          <option value="32">32"</option>
          <option value="40">40"</option>
          <option value="43">43"</option>
          <option value="50">50"</option>
          <option value="55">55"</option>
          <option value="65">65"</option>
          <option value="75">75"</option>
        </select>

        {/* DISPLAY TYPE */}
        <select
          className="filters-input"
          value={displayType}
          onChange={(e) => setDisplayType(e.target.value)}
        >
          <option value="">Display Type</option>
          <option value="LED">LED</option>
          <option value="QLED">QLED</option>
          <option value="OLED">OLED</option>
          <option value="Mini LED">Mini LED</option>
          <option value="LCD">LCD</option>
        </select>

        <button className="filters-button" onClick={applyFilters}>
          Apply Filters & Compare
        </button>
      </div>
    </div>
  );
}

export default Filters;
