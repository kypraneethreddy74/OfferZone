import React, { useEffect, useMemo, useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  LineChart,
  Line,
  Legend,
  ComposedChart,
  PieChart,
  Pie,
  Cell,
  ScatterChart,
  Scatter,
  ZAxis,
} from "recharts";

import "./Graphs.css";

const PIE_COLORS = [
  "#fb923c",
  "#22c55e",
  "#3b82f6",
  "#a855f7",
  "#ef4444",
  "#14b8a6",
  "#f59e0b",
];

const Graphs = () => {
  const [products, setProducts] = useState([]);
  const [platforms, setPlatforms] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetch("http://localhost:8000/analytics/products").then((r) => r.json()),
      fetch("http://localhost:8000/analytics/platforms").then((r) => r.json()),
    ])
      .then(([p, pl]) => {
        setProducts(Array.isArray(p) ? p : []);
        setPlatforms(Array.isArray(pl) ? pl : []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  /* ================= CLEAN PRODUCTS ================= */
  const cleanProducts = useMemo(() => {
    return products
      .filter((p) => p && p.brand)
      .map((p, idx) => ({
        id: p.id || idx + 1,
        brand: String(p.brand),
        platform: p.platform || p.Platform || "Unknown",
        model: p.model || p.title || "TV Model",
        avg_price: Number(p.avg_price) || 0,
        avg_rating: Number(p.avg_rating) || 0,
        avg_discount: Number(p.avg_discount) || 0,
        in_stock: Number(p.in_stock) || 0,
      }));
  }, [products]);

  /* ================= CLEAN PLATFORMS (FIX DONUT) ================= */
  const cleanPlatforms = useMemo(() => {
    return platforms
      .filter((p) => p)
      .map((p) => ({
        platform: p.platform || p.Platform || "Unknown",
        stock: Number(p.in_stock_count ?? p.stock ?? 0),
        total: Number(p.total_products ?? p.total ?? 0),
      }))
      .filter((p) => p.platform);
  }, [platforms]);

  /* ================= PLATFORM STOCK BAR ================= */
  const platformStockBar = useMemo(() => {
    return cleanPlatforms.map((p) => ({
      platform: p.platform,
      stock: p.stock,
    }));
  }, [cleanPlatforms]);

  /* ================= PLATFORM SHARE DONUT (WORKING) ================= */
  const platformShareDonut = useMemo(() => {
    const hasTotal = cleanPlatforms.some((p) => p.total > 0);

    // if backend gives total_products -> use share %
    if (hasTotal) {
      return cleanPlatforms.map((p) => ({
        platform: p.platform,
        value: p.total > 0 ? Number(((p.stock / p.total) * 100).toFixed(1)) : 0,
      }));
    }

    // if total missing -> use stock itself for donut
    return cleanPlatforms.map((p) => ({
      platform: p.platform,
      value: p.stock,
    }));
  }, [cleanPlatforms]);

  /* ================= BRAND AGGREGATION ================= */
  const brandAgg = useMemo(() => {
    const map = new Map();

    cleanProducts.forEach((p) => {
      if (!map.has(p.brand)) {
        map.set(p.brand, {
          brand: p.brand,
          count: 0,
          priceSum: 0,
          ratingSum: 0,
          discountSum: 0,
        });
      }

      const b = map.get(p.brand);
      b.count += 1;
      b.priceSum += p.avg_price;
      b.ratingSum += p.avg_rating;
      b.discountSum += p.avg_discount;
    });

    return Array.from(map.values()).map((b) => ({
      brand: b.brand,
      count: b.count,
      avg_price: b.count ? Math.round(b.priceSum / b.count) : 0,
      avg_rating: b.count ? Number((b.ratingSum / b.count).toFixed(2)) : 0,
      avg_discount: b.count ? Number((b.discountSum / b.count).toFixed(1)) : 0,
    }));
  }, [cleanProducts]);

  /* ================= BEST GRAPHS ================= */

  const topAvgPriceBrands = useMemo(() => {
    return [...brandAgg].sort((a, b) => b.avg_price - a.avg_price).slice(0, 12);
  }, [brandAgg]);

  const topAvgRatingBrands = useMemo(() => {
    return [...brandAgg]
      .filter((b) => b.avg_rating > 0)
      .sort((a, b) => b.avg_rating - a.avg_rating)
      .slice(0, 12);
  }, [brandAgg]);

  const topAvgDiscountBrands = useMemo(() => {
    return [...brandAgg]
      .filter((b) => b.avg_discount > 0)
      .sort((a, b) => b.avg_discount - a.avg_discount)
      .slice(0, 12);
  }, [brandAgg]);

  const countVsPrice = useMemo(() => {
    return [...brandAgg].sort((a, b) => b.count - a.count).slice(0, 12);
  }, [brandAgg]);

  const scatterPriceRating = useMemo(() => {
    return cleanProducts
      .filter((p) => p.avg_price > 0 && p.avg_rating > 0)
      .slice(0, 90)
      .map((p) => ({
        price: Math.round(p.avg_price),
        rating: Number(p.avg_rating.toFixed(2)),
        bubble: Math.max(10, Math.min(100, p.avg_discount * 2)),
      }));
  }, [cleanProducts]);

  const discountVsPrice = useMemo(() => {
    return cleanProducts
      .filter((p) => p.avg_price > 0 && p.avg_discount > 0)
      .sort((a, b) => a.avg_price - b.avg_price)
      .slice(0, 35)
      .map((p) => ({
        price: Math.round(p.avg_price),
        discount: Number(p.avg_discount.toFixed(1)),
      }));
  }, [cleanProducts]);

  const priceBuckets = useMemo(() => {
    const buckets = [
      { range: "0-20K", min: 0, max: 20000, count: 0 },
      { range: "20K-40K", min: 20000, max: 40000, count: 0 },
      { range: "40K-60K", min: 40000, max: 60000, count: 0 },
      { range: "60K-80K", min: 60000, max: 80000, count: 0 },
      { range: "80K-1L", min: 80000, max: 100000, count: 0 },
      { range: "1L+", min: 100000, max: Infinity, count: 0 },
    ];

    cleanProducts.forEach((p) => {
      const b = buckets.find((x) => p.avg_price >= x.min && p.avg_price < x.max);
      if (b) b.count += 1;
    });

    return buckets;
  }, [cleanProducts]);

  const discountBuckets = useMemo(() => {
    const buckets = [
      { range: "0-10%", min: 0, max: 10, count: 0 },
      { range: "10-20%", min: 10, max: 20, count: 0 },
      { range: "20-30%", min: 20, max: 30, count: 0 },
      { range: "30-40%", min: 30, max: 40, count: 0 },
      { range: "40%+", min: 40, max: Infinity, count: 0 },
    ];

    cleanProducts.forEach((p) => {
      const b = buckets.find((x) => p.avg_discount >= x.min && p.avg_discount < x.max);
      if (b) b.count += 1;
    });

    return buckets;
  }, [cleanProducts]);

  if (loading) return <div className="graphs-loading">Loading dashboard…</div>;

  return (
    <div className="graphs-page">
      <h2>📊 Premium TV Analytics Graphs</h2>

      <div className="dashboard-grid">
        {/* 1 Platform Stock Bar */}
        <div className="dashboard-card span-6">
          <h4>🏬 Platform Stock (Bar)</h4>
          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={platformStockBar}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="platform" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="stock" fill="#16a34a" radius={[12, 12, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* 2 Platform Share Donut FIXED */}
        <div className="dashboard-card span-6">
          <h4>🍩 Platform Stock Share (Donut)</h4>
          <ResponsiveContainer width="100%" height={320}>
            <PieChart>
              <Tooltip />
              <Legend />
              <Pie
                data={platformShareDonut}
                dataKey="value"
                nameKey="platform"
                cx="50%"
                cy="50%"
                innerRadius={70}
                outerRadius={110}
                paddingAngle={2}
              >
                {platformShareDonut.map((_, i) => (
                  <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* 3 Avg Price by Brand */}
        <div className="dashboard-card span-12">
          <h4>💰 Avg Price by Brand (Top 12)</h4>
          <ResponsiveContainer width="100%" height={420}>
            <BarChart data={topAvgPriceBrands} layout="vertical" margin={{ left: 110 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis type="category" dataKey="brand" width={180} />
              <Tooltip />
              <Bar dataKey="avg_price" fill="#2563eb" radius={[0, 12, 12, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* 4 Avg Rating by Brand */}
        <div className="dashboard-card span-6">
          <h4>⭐ Avg Rating by Brand (Top 12)</h4>
          <ResponsiveContainer width="100%" height={340}>
            <BarChart data={topAvgRatingBrands}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="brand" hide />
              <YAxis domain={[0, 5]} />
              <Tooltip />
              <Bar dataKey="avg_rating" fill="#f59e0b" radius={[12, 12, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* 5 Avg Discount by Brand */}
        <div className="dashboard-card span-6">
          <h4>🔥 Avg Discount by Brand (Top 12)</h4>
          <ResponsiveContainer width="100%" height={340}>
            <BarChart data={topAvgDiscountBrands}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="brand" hide />
              <YAxis unit="%" />
              <Tooltip />
              <Bar dataKey="avg_discount" fill="#ef4444" radius={[12, 12, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* 6 Composed Count vs Avg Price */}
        <div className="dashboard-card span-12">
          <h4>📌 Brand Count + Avg Price (Composed)</h4>
          <ResponsiveContainer width="100%" height={380}>
            <ComposedChart data={countVsPrice}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="brand" hide />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="count" fill="#7c3aed" radius={[12, 12, 0, 0]} />
              <Line type="monotone" dataKey="avg_price" stroke="#f97316" strokeWidth={3} />
            </ComposedChart>
          </ResponsiveContainer>
        </div>

        {/* 7 Scatter Bubble */}
        <div className="dashboard-card span-12">
          <h4>🟠 Price vs Rating Scatter (Bubble = Discount)</h4>
          <ResponsiveContainer width="100%" height={380}>
            <ScatterChart>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" dataKey="price" tickFormatter={(v) => `₹${v / 1000}K`} />
              <YAxis type="number" dataKey="rating" domain={[0, 5]} />
              <ZAxis type="number" dataKey="bubble" range={[60, 200]} />
              <Tooltip />
              <Scatter data={scatterPriceRating} fill="#fb923c" />
            </ScatterChart>
          </ResponsiveContainer>
        </div>

        {/* 8 Discount vs Price */}
        <div className="dashboard-card span-12">
          <h4>📉 Discount vs Price Trend</h4>
          <ResponsiveContainer width="100%" height={380}>
            <LineChart data={discountVsPrice}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="price" tickFormatter={(v) => `₹${v / 1000}K`} />
              <YAxis unit="%" />
              <Tooltip />
              <Line type="monotone" dataKey="discount" stroke="#ef4444" strokeWidth={3} dot={{ r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* 9 Price Distribution */}
        <div className="dashboard-card span-6">
          <h4>📦 Price Distribution</h4>
          <ResponsiveContainer width="100%" height={340}>
            <BarChart data={priceBuckets}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="range" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#0ea5e9" radius={[12, 12, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* 10 Discount Distribution */}
        <div className="dashboard-card span-6">
          <h4>🔥 Discount Distribution</h4>
          <ResponsiveContainer width="100%" height={340}>
            <BarChart data={discountBuckets}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="range" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#22c55e" radius={[12, 12, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default Graphs;
