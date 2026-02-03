import React, { useState, useEffect } from "react";
import {
  getPriceHistoryCharts,
  getBestPriceChart
} from "../services/api";
import "./PriceHistoryModal.css";

function PriceHistoryModal({ isOpen, onClose, modelId, productName, initialTab = "history" }) {
  const [activeTab, setActiveTab] = useState(initialTab);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [days, setDays] = useState(30);
  const [charts, setCharts] = useState(null);
  const [activeChart, setActiveChart] = useState("line");
// Change this:
useEffect(() => {
  if (isOpen && modelId) {
    setActiveTab(initialTab);
    fetchCharts();
  }
}, [isOpen, modelId, days, initialTab]);

// To this:
// Change this:
useEffect(() => {
  if (isOpen && modelId) {
    setActiveTab(initialTab);
    fetchCharts();
  }
}, [isOpen, modelId, days, initialTab]);

// To this:
  useEffect(() => {
    const loadCharts = async () => {
      setLoading(true);
      setError(null);
      try {
        const [historyRes, bestRes] = await Promise.all([
          getPriceHistoryCharts(modelId, days),
          getBestPriceChart(modelId, days)
        ]);
        setCharts({
          history: historyRes.data,
          best: bestRes.data
        });
      } catch (err) {
        console.error("Error fetching charts:", err);
        setError("Failed to load price history. Please try again.");
      } finally {
        setLoading(false);
      }
    };

  if (isOpen && modelId) {
    setActiveTab(initialTab);
    loadCharts();
  }
}, [isOpen, modelId, days, initialTab]);

  if (isOpen && modelId) {
    setActiveTab(initialTab);
    loadCharts();
  }
}, [isOpen, modelId, days, initialTab]);


  const fetchCharts = async () => {
    setLoading(true);
    setError(null);

    try {
      const [historyRes, bestRes] = await Promise.all([
        getPriceHistoryCharts(modelId, days),
        getBestPriceChart(modelId, days)
      ]);

      setCharts({
        history: historyRes.data,
        best: bestRes.data
      });
    } catch (err) {
      console.error("Error fetching charts:", err);
      setError("Failed to load price history. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  const chartOptions = [
    { key: "line", label: "📈 Price Trends", icon: "📈" },
    { key: "combined", label: "🔀 All Platforms", icon: "🔀" },
    { key: "comparison", label: "📊 Comparison", icon: "📊" },
    { key: "heatmap", label: "🗓️ Heatmap", icon: "🗓️" }
  ];

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="price-history-modal" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="modal-header">
          <div className="header-content">
            <h2>📊 Price History</h2>
            <p className="product-name-modal">{productName}</p>
          </div>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        {/* Main Tabs */}
        <div className="modal-tabs">
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
        <div className="time-selector">
          <span>Time Range:</span>
          {[7, 14, 30, 90, 180, 365].map((d) => (
            <button
              key={d}
              className={`time-btn ${days === d ? "active" : ""}`}
              onClick={() => setDays(d)}
            >
              {d < 365 ? `${d} Days` : "1 Year"}
            </button>
          ))}
        </div>

        {/* Chart Type Selector (for history tab) */}
        {activeTab === "history" && !loading && !error && (
          <div className="chart-type-selector">
            {chartOptions.map((opt) => (
              <button
                key={opt.key}
                className={`chart-type-btn ${activeChart === opt.key ? "active" : ""}`}
                onClick={() => setActiveChart(opt.key)}
              >
                {opt.label}
              </button>
            ))}
          </div>
        )}

        {/* Content */}
        <div className="modal-content">
          {loading && (
            <div className="loading-state">
              <div className="spinner"></div>
              <p>Loading price history...</p>
            </div>
          )}

          {error && (
            <div className="error-state">
              <span className="error-icon">⚠️</span>
              <p>{error}</p>
              <button onClick={fetchCharts} className="retry-btn">Retry</button>
            </div>
          )}

          {!loading && !error && charts && (
            <div className="charts-content">
              {activeTab === "history" && charts.history && (
                <div className="chart-single">
                  {activeChart === "line" && (
                    <img
                      src={charts.history.charts?.line_chart}
                      alt="Price History"
                      className="chart-image-large"
                    />
                  )}
                  {activeChart === "combined" && (
                    <img
                      src={charts.history.charts?.combined_chart}
                      alt="All Platforms"
                      className="chart-image-large"
                    />
                  )}
                  {activeChart === "comparison" && (
                    <img
                      src={charts.history.charts?.comparison_chart}
                      alt="Price Comparison"
                      className="chart-image-large"
                    />
                  )}
                  {activeChart === "heatmap" && (
                    <img
                      src={charts.history.charts?.heatmap_chart}
                      alt="Price Heatmap"
                      className="chart-image-large"
                    />
                  )}
                </div>
              )}

              {activeTab === "best" && charts.best && (
                <div className="chart-single">
                  <img
                    src={charts.best.chart}
                    alt="Best Price Tracker"
                    className="chart-image-large"
                  />
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default PriceHistoryModal;