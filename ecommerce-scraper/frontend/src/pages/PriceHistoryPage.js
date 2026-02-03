import React, { useState, useEffect, useCallback } from "react";
import { useParams, useSearchParams, useNavigate } from "react-router-dom";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine
} from "recharts";
import { getPriceHistoryData } from "../services/api";
import "./PriceHistoryPage.css";

const PLATFORM_COLORS = {
  amazon: { main: "#FF9900", light: "#FFF3E0" },
  Amazon: { main: "#FF9900", light: "#FFF3E0" },
  flipkart: { main: "#2874F0", light: "#E3F2FD" },
  Flipkart: { main: "#2874F0", light: "#E3F2FD" },
  CROMA: { main: "#00B0B9", light: "#E0F7FA" },
  Croma: { main: "#00B0B9", light: "#E0F7FA" },
  reliance: { main: "#E31837", light: "#FFEBEE" },
  Reliance: { main: "#E31837", light: "#FFEBEE" },
  vijay: { main: "#8B5CF6", light: "#EDE7F6" },
  Vijay: { main: "#8B5CF6", light: "#EDE7F6" },
  tatacliq: { main: "#E91E63", light: "#FCE4EC" },
  Tatacliq: { main: "#E91E63", light: "#FCE4EC" }
};

const getColor = (platform) => PLATFORM_COLORS[platform] || { main: "#2196F3", light: "#E3F2FD" };

const formatPrice = (value) => `₹${value?.toLocaleString("en-IN") || 0}`;

const formatDate = (dateStr) => {
  const date = new Date(dateStr);
  return date.toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" });
};

const formatShortDate = (dateStr) => {
  const date = new Date(dateStr);
  return date.toLocaleDateString("en-IN", { day: "numeric", month: "short" });
};

function PriceHistoryPage() {
  const { modelId } = useParams();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  
  const initialTab = searchParams.get("tab") || "history";
  const productNameParam = searchParams.get("name") || "";
  
  const [activeTab, setActiveTab] = useState(initialTab);
  const [days, setDays] = useState(30);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);

  // Fetch data function with useCallback
  const fetchData = useCallback(async () => {
    if (!modelId) return;
    
    setLoading(true);
    setError(null);
    try {
      const res = await getPriceHistoryData(modelId, days);
      setData(res.data);
    } catch (err) {
      setError("Failed to load price history. Please try again.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [modelId, days]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Custom Tooltip for individual platform charts
  const PlatformTooltip = ({ active, payload, label, platform }) => {
    if (!active || !payload?.length) return null;
    const price = payload[0]?.value;
    return (
      <div className="chart-tooltip">
        <div className="tooltip-platform" style={{ color: getColor(platform).main }}>
          {platform}
        </div>
        <div className="tooltip-date">{formatDate(label)}</div>
        <div className="tooltip-price">{formatPrice(price)}</div>
      </div>
    );
  };

  // Custom Tooltip for best price chart
  const BestPriceTooltip = ({ active, payload, label }) => {
    if (!active || !payload?.length) return null;
    const point = payload[0]?.payload;
    return (
      <div className="chart-tooltip">
        <div className="tooltip-platform" style={{ color: getColor(point?.platform).main }}>
          🏆 {point?.platform}
        </div>
        <div className="tooltip-date">{formatDate(label)}</div>
        <div className="tooltip-price">{formatPrice(point?.price)}</div>
      </div>
    );
  };

  const timeRanges = [
    { label: "7 Days", value: 7 },
    { label: "14 Days", value: 14 },
    { label: "30 Days", value: 30 },
    { label: "90 Days", value: 90 },
    { label: "180 Days", value: 180 },
    { label: "1 Year", value: 365 }
  ];

  return (
    <div className="price-history-page">
      {/* Header */}
      <div className="page-header">
        <button className="back-btn" onClick={() => navigate(-1)}>
          ← Back
        </button>
        <div className="header-content">
          <h1>📊 Price History</h1>
          <p className="product-name">{data?.product_name || productNameParam || modelId}</p>
        </div>
      </div>

      {/* Product Info Bar */}
      {data && (
        <div className="product-info-bar">
          {data.image_url && (
            <img src={data.image_url} alt={data.product_name} className="product-thumb" />
          )}
          <div className="product-details">
            <span className="brand-badge">{data.brand}</span>
            <span className="model-id">Model: {modelId}</span>
            <span className="platforms-count">
              Available on {data.platforms?.length || 0} platform{data.platforms?.length !== 1 ? 's' : ''}
            </span>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="tabs-container">
        <button
          className={`tab-btn ${activeTab === "history" ? "active" : ""}`}
          onClick={() => setActiveTab("history")}
        >
          📈 Price History
        </button>
        <button
          className={`tab-btn ${activeTab === "best" ? "active" : ""}`}
          onClick={() => setActiveTab("best")}
        >
          🏆 Best Price Tracker
        </button>
      </div>

      {/* Time Range Selector */}
      <div className="time-range-selector">
        <span className="label">Time Range:</span>
        <div className="time-buttons">
          {timeRanges.map((range) => (
            <button
              key={range.value}
              className={days === range.value ? "active" : ""}
              onClick={() => setDays(range.value)}
            >
              {range.label}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="page-content">
        {/* Loading State */}
        {loading && (
          <div className="loading-container">
            <div className="spinner"></div>
            <p>Loading price history...</p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="error-container">
            <span className="error-icon">⚠️</span>
            <p>{error}</p>
            <button onClick={fetchData}>Retry</button>
          </div>
        )}

        {/* No Data */}
        {!loading && !error && (!data || !data.platforms?.length) && (
          <div className="no-data-container">
            <span className="icon">📊</span>
            <p>No price history available for this product</p>
          </div>
        )}

        {/* Price History Tab - Multiple Platform Charts */}
        {!loading && !error && activeTab === "history" && data?.platforms_data && (
          <div className="charts-grid">
            {Object.entries(data.platforms_data).map(([platform, platformInfo]) => (
              <div key={platform} className="platform-chart-card">
                {/* Platform Header */}
                <div className="platform-header" style={{ borderLeftColor: getColor(platform).main }}>
                  <h3>
                    <span className="platform-dot" style={{ backgroundColor: getColor(platform).main }}></span>
                    {platform.toUpperCase()} Price History
                  </h3>
                </div>

                {/* Stats Bar */}
                <div className="stats-bar">
                  <div className="stat current">
                    <span className="label">Current Price*</span>
                    <span className="value">{formatPrice(platformInfo.stats.current)}</span>
                  </div>
                  <div className="stat lowest">
                    <span className="label">Lowest Price</span>
                    <span className="value">{formatPrice(platformInfo.stats.lowest)}</span>
                  </div>
                  <div className="stat highest">
                    <span className="label">Highest Price</span>
                    <span className="value">{formatPrice(platformInfo.stats.highest)}</span>
                  </div>
                </div>

                {/* Chart */}
                <div className="chart-wrapper">
                  <ResponsiveContainer width="100%" height={300}>
                    <AreaChart data={platformInfo.data} margin={{ top: 10, right: 30, left: 10, bottom: 10 }}>
                      <defs>
                        <linearGradient id={`gradient-${platform}`} x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#87CEEB" stopOpacity={0.8} />
                          <stop offset="95%" stopColor="#87CEEB" stopOpacity={0.3} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" vertical={false} />
                      <XAxis
                        dataKey="date"
                        tickFormatter={formatShortDate}
                        tick={{ fontSize: 11, fill: "#666" }}
                        axisLine={{ stroke: "#ccc" }}
                        tickLine={{ stroke: "#ccc" }}
                      />
                      <YAxis
                        tickFormatter={(v) => `₹${(v/1000).toFixed(0)}K`}
                        tick={{ fontSize: 11, fill: "#666" }}
                        axisLine={{ stroke: "#ccc" }}
                        tickLine={{ stroke: "#ccc" }}
                        domain={[
                          dataMin => Math.floor(dataMin * 0.95),
                          dataMax => Math.ceil(dataMax * 1.05)
                        ]}
                      />
                      <Tooltip content={<PlatformTooltip platform={platform} />} />
                      
                      {/* Highest Price Line - Red Dashed */}
                      <ReferenceLine
                        y={platformInfo.stats.highest}
                        stroke="#EF4444"
                        strokeDasharray="5 5"
                        strokeWidth={1.5}
                      />
                      
                      {/* Lowest Price Line - Green Dashed */}
                      <ReferenceLine
                        y={platformInfo.stats.lowest}
                        stroke="#22C55E"
                        strokeDasharray="5 5"
                        strokeWidth={1.5}
                      />
                      
                      {/* Area Chart - Light Blue Fill */}
                      <Area
                        type="stepAfter"
                        dataKey="price"
                        stroke="#1E90FF"
                        strokeWidth={2}
                        fill={`url(#gradient-${platform})`}
                        isAnimationActive={true}
                        animationDuration={500}
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>

                {/* Chart Footer */}
                <div className="chart-footer">
                  <span>Roll over the chart for price information</span>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Best Price Tracker Tab */}
        {!loading && !error && activeTab === "best" && data?.best_price_data && (
          <div className="best-price-section">
            {/* Best Price Card */}
            <div className="best-price-card">
              {/* Header */}
              <div className="best-price-header">
                <h3>🏆 Best Price Tracker</h3>
                <p>Showing the lowest price across all platforms</p>
              </div>

              {/* Stats Bar */}
              <div className="stats-bar best-stats">
                <div className="stat current">
                  <span className="label">Current Best Price</span>
                  <span className="value">{formatPrice(data.best_price_stats?.current)}</span>
                  <span className="platform-badge" style={{ backgroundColor: getColor(data.best_price_stats?.current_platform).main }}>
                    {data.best_price_stats?.current_platform}
                  </span>
                </div>
                <div className="stat lowest">
                  <span className="label">All-Time Lowest</span>
                  <span className="value">{formatPrice(data.best_price_stats?.lowest)}</span>
                </div>
                <div className="stat highest">
                  <span className="label">Period Highest</span>
                  <span className="value">{formatPrice(data.best_price_stats?.highest)}</span>
                </div>
              </div>

              {/* Chart */}
              <div className="chart-wrapper large">
                <ResponsiveContainer width="100%" height={400}>
                  <AreaChart data={data.best_price_data} margin={{ top: 10, right: 30, left: 10, bottom: 10 }}>
                    <defs>
                      <linearGradient id="bestPriceGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#87CEEB" stopOpacity={0.8} />
                        <stop offset="95%" stopColor="#87CEEB" stopOpacity={0.3} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" vertical={false} />
                    <XAxis
                      dataKey="date"
                      tickFormatter={formatShortDate}
                      tick={{ fontSize: 11, fill: "#666" }}
                      axisLine={{ stroke: "#ccc" }}
                      tickLine={{ stroke: "#ccc" }}
                    />
                    <YAxis
                      tickFormatter={(v) => `₹${(v/1000).toFixed(0)}K`}
                      tick={{ fontSize: 11, fill: "#666" }}
                      axisLine={{ stroke: "#ccc" }}
                      tickLine={{ stroke: "#ccc" }}
                      domain={[
                        dataMin => Math.floor(dataMin * 0.95),
                        dataMax => Math.ceil(dataMax * 1.05)
                      ]}
                    />
                    <Tooltip content={<BestPriceTooltip />} />
                    
                    {/* Highest Price Line - Red Dashed */}
                    <ReferenceLine
                      y={data.best_price_stats?.highest}
                      stroke="#EF4444"
                      strokeDasharray="5 5"
                      strokeWidth={1.5}
                    />
                    
                    {/* Lowest Price Line - Green Dashed */}
                    <ReferenceLine
                      y={data.best_price_stats?.lowest}
                      stroke="#22C55E"
                      strokeDasharray="5 5"
                      strokeWidth={1.5}
                    />
                    
                    <Area
                      type="stepAfter"
                      dataKey="price"
                      stroke="#1E90FF"
                      strokeWidth={2.5}
                      fill="url(#bestPriceGradient)"
                      isAnimationActive={true}
                      animationDuration={500}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>

              {/* Chart Footer */}
              <div className="chart-footer">
                <span>Roll over the chart for price information • Colored dots show which platform had the best price</span>
              </div>
            </div>

            {/* Platform Comparison Summary */}
            <div className="platform-summary-card">
              <h3>📊 Platform Comparison</h3>
              <div className="platform-comparison-grid">
                {data.platforms?.map((platform) => {
                  const pData = data.platforms_data[platform];
                  if (!pData) return null;
                  return (
                    <div key={platform} className="platform-summary-item">
                      <div className="platform-name" style={{ borderLeftColor: getColor(platform).main }}>
                        <span className="dot" style={{ backgroundColor: getColor(platform).main }}></span>
                        {platform}
                      </div>
                      <div className="platform-prices">
                        <div className="price-item">
                          <span className="label">Current</span>
                          <span className="value">{formatPrice(pData.stats.current)}</span>
                        </div>
                        <div className="price-item lowest">
                          <span className="label">Lowest</span>
                          <span className="value">{formatPrice(pData.stats.lowest)}</span>
                        </div>
                        <div className="price-item highest">
                          <span className="label">Highest</span>
                          <span className="value">{formatPrice(pData.stats.highest)}</span>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Price Drop Alert Section */}
            <div className="price-alert-card">
              <h3>🔔 Set Price Alert</h3>
              <p>Get notified when the price drops below your target</p>
              <div className="alert-form">
                <input type="number" placeholder="Enter target price (₹)" />
                <button className="set-alert-btn">Set Alert</button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default PriceHistoryPage;