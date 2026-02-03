import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Statistics.css";

const Statistics = () => {
  const navigate = useNavigate();

  const [brandStats, setBrandStats] = useState([]);
  const [platformStats, setPlatformStats] = useState([]);
  const [kpis, setKpis] = useState({
    avgPrice: 0,
    avgDiscount: 0,
    avgRating: 0,
    totalProducts: 0,

    totalPlatforms: 0,
    inStockCount: 0,
    outStockCount: 0,

    bestPrice: 0,
    bestRating: 0,
    bestReviews: 0,
  });

  /* ✅ ADDED: Best Analytics State */
  const [bestAnalytics, setBestAnalytics] = useState({
    highestPrice: 0,
    lowestPrice: 0,
    medianPrice: 0,
    priceRange: 0,

    avgSavings: 0,

    topDiscount: 0,
    dealPercent: 0,

    qualityPercent: 0,

    bestValueScore: 0,

    premiumCount: 0,
    budgetCount: 0,

    stockPercent: 0,

    topStockPlatform: "",
    topStockCount: 0,

    topListingsBrand: "",
    topListingsCount: 0,
  });

  const [searchQuery, setSearchQuery] = useState("");
  const [displayType, setDisplayType] = useState("");
  const [screenSize, setScreenSize] = useState("");
  const [searchResults, setSearchResults] = useState([]);

  const [loading, setLoading] = useState(true);

  /* ================= LOAD STATS ================= */
  useEffect(() => {
    Promise.all([
      fetch("http://localhost:8000/analytics/brands").then(r => r.json()),
      fetch("http://localhost:8000/analytics/platforms").then(r => r.json()),
      fetch("http://localhost:8000/analytics/products").then(r => r.json()),
      // ✅ This API has real price data (sale_price)
      fetch("http://localhost:8000/products/filter?").then(r => r.json()),
    ])
      .then(([brands, platforms, products, allProducts]) => {
        setBrandStats(Array.isArray(brands) ? brands : []);
        setPlatformStats(Array.isArray(platforms) ? platforms : []);

        /* ✅ TOTAL PLATFORMS + STOCK COUNT (FROM PLATFORM API) */
        const totalPlatforms = Array.isArray(platforms) ? platforms.length : 0;

        const totalListings = Array.isArray(platforms)
          ? platforms.reduce((s, p) => s + (p.total_listings || 0), 0)
          : 0;

        const inStockCount = Array.isArray(platforms)
          ? platforms.reduce((s, p) => s + (p.in_stock_count || 0), 0)
          : 0;

        const outStockCount = totalListings - inStockCount;

        setKpis(prev => ({
          ...prev,
          totalPlatforms,
          inStockCount,
          outStockCount,
        }));

        /* ✅ AVG KPIs FROM analytics/products */
        if (Array.isArray(products) && products.length > 0) {
          const total = products.length;

          setKpis(prev => ({
            ...prev,
            avgPrice:
              products.reduce((s, p) => s + (p.avg_price || 0), 0) / total,
            avgDiscount:
              products.reduce((s, p) => s + (p.avg_discount || 0), 0) / total,
            avgRating:
              products.reduce((s, p) => s + (p.avg_rating || 0), 0) / total,
            totalProducts: total,
          }));
        }

        /* ✅ BEST PRICE + BEST REVIEWS FROM /products/filter */
        if (Array.isArray(allProducts) && allProducts.length > 0) {
          // Best Price
          const bestPriceProduct = allProducts.reduce((best, p) => {
            const price = Number(p.sale_price ?? p.price ?? 0);
            const bestPrice = Number(best?.sale_price ?? best?.price ?? Infinity);
            return price > 0 && price < bestPrice ? p : best;
          }, null);

          // Best Rating
          const bestRatingProduct = allProducts.reduce((best, p) => {
            const rating = Number(p.rating ?? 0);
            const bestRating = Number(best?.rating ?? 0);
            return rating > bestRating ? p : best;
          }, null);

          // Best Reviews
          const bestReviewProduct = allProducts.reduce((best, p) => {
            const reviews = Number(
              p.review_count ??
                p.reviews ??
                p.total_reviews ??
                p.total_ratings ??
                0
            );
            const bestReviews = Number(
              best?.review_count ??
                best?.reviews ??
                best?.total_reviews ??
                best?.total_ratings ??
                0
            );
            return reviews > bestReviews ? p : best;
          }, null);

          setKpis(prev => ({
            ...prev,
            bestPrice: Number(
              bestPriceProduct?.sale_price ?? bestPriceProduct?.price ?? 0
            ),
            bestRating: Number(bestRatingProduct?.rating ?? 0),
            bestReviews: Number(
              bestReviewProduct?.review_count ??
                bestReviewProduct?.reviews ??
                bestReviewProduct?.total_reviews ??
                bestReviewProduct?.total_ratings ??
                0
            ),
          }));

          /* ================= BEST ANALYTICS (POWERBI LEVEL) ================= */
          const validProducts = allProducts.filter(
            p => Number(p.sale_price ?? p.price ?? 0) > 0
          );

          if (validProducts.length > 0) {
            const prices = validProducts.map(p =>
              Number(p.sale_price ?? p.price ?? 0)
            );

            const highestPrice = Math.max(...prices);
            const lowestPrice = Math.min(...prices);

            // Median price
            const sortedPrices = [...prices].sort((a, b) => a - b);
            const medianPrice = sortedPrices[Math.floor(sortedPrices.length / 2)];

            // Price Range
            const priceRange = highestPrice - lowestPrice;

            // Avg Savings (₹) = original_cost - sale_price
            const savingsList = validProducts.map(p => {
              const sp = Number(p.sale_price ?? 0);
              const oc = Number(p.original_cost ?? 0);
              return oc > 0 && sp > 0 ? oc - sp : 0;
            });

            const avgSavings =
              savingsList.length > 0
                ? savingsList.reduce((s, v) => s + v, 0) / savingsList.length
                : 0;

            // Top Discount
            const topDiscountProduct = validProducts.reduce((best, p) => {
              const d = Number(p.discount ?? 0);
              const bd = Number(best?.discount ?? 0);
              return d > bd ? p : best;
            }, null);

            // Deal Percent (discount >= 20)
            const dealCount = validProducts.filter(
              p => Number(p.discount ?? 0) >= 20
            ).length;

            const dealPercent =
              validProducts.length > 0
                ? (dealCount / validProducts.length) * 100
                : 0;

            // Quality Percent (rating >= 4)
            const qualityCount = validProducts.filter(
              p => Number(p.rating ?? 0) >= 4
            ).length;

            const qualityPercent =
              validProducts.length > 0
                ? (qualityCount / validProducts.length) * 100
                : 0;

            // Best Value Score = discount * rating (ONLY SCORE)
            const bestValueProduct = validProducts.reduce((best, p) => {
              const score = Number(p.discount ?? 0) * Number(p.rating ?? 0);
              const bestScore =
                Number(best?.discount ?? 0) * Number(best?.rating ?? 0);
              return score > bestScore ? p : best;
            }, null);

            const bestValueScore =
              Number(bestValueProduct?.discount ?? 0) *
              Number(bestValueProduct?.rating ?? 0);

            // Budget vs Premium counts
            const budgetCount = validProducts.filter(
              p => Number(p.sale_price ?? p.price ?? 0) < medianPrice
            ).length;

            const premiumCount = validProducts.filter(
              p => Number(p.sale_price ?? p.price ?? 0) >= 50000
            ).length;

            // Stock %
            const stockPercent =
              inStockCount + outStockCount > 0
                ? (inStockCount / (inStockCount + outStockCount)) * 100
                : 0;

            // Top Stock Platform
            const topStockPlatformObj = Array.isArray(platforms)
              ? platforms.reduce((best, p) => {
                  return (p.in_stock_count || 0) > (best.in_stock_count || 0)
                    ? p
                    : best;
                }, platforms[0] || {})
              : {};

            // Top Listings Brand
            const topBrandObj = Array.isArray(brands)
              ? brands.reduce((best, b) => {
                  return (b.total_listings || 0) > (best.total_listings || 0)
                    ? b
                    : best;
                }, brands[0] || {})
              : {};

            setBestAnalytics({
              highestPrice,
              lowestPrice,
              medianPrice,
              priceRange,

              avgSavings: Number(avgSavings.toFixed(0)),

              topDiscount: Number(topDiscountProduct?.discount ?? 0),
              dealPercent: Number(dealPercent.toFixed(1)),

              qualityPercent: Number(qualityPercent.toFixed(1)),

              bestValueScore: Number(bestValueScore.toFixed(2)),

              premiumCount,
              budgetCount,

              stockPercent: Number(stockPercent.toFixed(1)),

              topStockPlatform: topStockPlatformObj?.platform || "",
              topStockCount: topStockPlatformObj?.in_stock_count || 0,

              topListingsBrand: topBrandObj?.brand || "",
              topListingsCount: topBrandObj?.total_listings || 0,
            });
          }
        }
      })
      .finally(() => setLoading(false));
  }, []);

  /* ================= SEARCH ================= */
  const handleSearch = async () => {
    let url = searchQuery
      ? `http://localhost:8000/products/search?q=${encodeURIComponent(
          searchQuery
        )}`
      : "http://localhost:8000/products/filter?";

    const params = new URLSearchParams();
    if (displayType) params.append("display_type", displayType);
    if (screenSize) params.append("display_type", `${screenSize}"`);

    const res = await fetch(url + "&" + params.toString());
    const data = await res.json();
    setSearchResults(Array.isArray(data) ? data : []);
  };

  if (loading) return <div className="stats-loading">Loading…</div>;

  return (
    <div className="statistics-page">
      <h2> TV Market Statistics</h2>

      {/* ================= KPI ================= */}
      <div className="kpi-grid">
        <div className="kpi-card">
          <span>Total Platforms</span>
          <h3>{kpis.totalPlatforms}</h3>
        </div>

        <div className="kpi-card">
          <span>Total Products</span>
          <h3>{kpis.totalProducts}</h3>
        </div>

        <div className="kpi-card">
          <span>In Stock</span>
          <h3>{kpis.inStockCount}</h3>
        </div>

        <div className="kpi-card">
          <span>Out of Stock</span>
          <h3>{kpis.outStockCount}</h3>
        </div>

        <div className="kpi-card">
          <span>Avg Price</span>
          <h3>₹{Math.round(kpis.avgPrice)}</h3>
        </div>

        <div className="kpi-card">
          <span>Avg Discount</span>
          <h3>{kpis.avgDiscount.toFixed(1)}%</h3>
        </div>

        <div className="kpi-card">
          <span>Avg Rating</span>
          <h3>⭐ {kpis.avgRating.toFixed(2)}</h3>
        </div>

        <div className="kpi-card">
          <span>Best Price</span>
          <h3>₹{Math.round(kpis.bestPrice)}</h3>
        </div>

        <div className="kpi-card">
          <span>Best Rating</span>
          <h3>⭐ {Number(kpis.bestRating).toFixed(2)}</h3>
        </div>

        <div className="kpi-card">
          <span>Best Reviews</span>
          <h3>{kpis.bestReviews}</h3>
        </div>
      </div>

      {/* ================= BEST ANALYTICS KPI (POWERBI LEVEL) ================= */}
      <h3 style={{ marginTop: "25px" }}>🔥 Best Analytics</h3>

      <div className="kpi-grid">
        <div className="kpi-card">
          <span>Highest Price</span>
          <h3>₹{Math.round(bestAnalytics.highestPrice)}</h3>
        </div>

        <div className="kpi-card">
          <span>Lowest Price</span>
          <h3>₹{Math.round(bestAnalytics.lowestPrice)}</h3>
        </div>

        <div className="kpi-card">
          <span>Median Price</span>
          <h3>₹{Math.round(bestAnalytics.medianPrice)}</h3>
        </div>

        <div className="kpi-card">
          <span>Price Range</span>
          <h3>₹{Math.round(bestAnalytics.priceRange)}</h3>
        </div>

        <div className="kpi-card">
          <span>Avg Savings</span>
          <h3>₹{Math.round(bestAnalytics.avgSavings)}</h3>
        </div>

        <div className="kpi-card">
          <span>Top Discount</span>
          <h3>{bestAnalytics.topDiscount}%</h3>
        </div>

        <div className="kpi-card">
          <span>Deal % (20%+)</span>
          <h3>{bestAnalytics.dealPercent}%</h3>
        </div>

        <div className="kpi-card">
          <span>Quality % (4⭐+)</span>
          <h3>{bestAnalytics.qualityPercent}%</h3>
        </div>

        <div className="kpi-card">
          <span>Best Value Score</span>
          <h3>{bestAnalytics.bestValueScore}</h3>
        </div>

        <div className="kpi-card">
          <span>Budget TVs</span>
          <h3>{bestAnalytics.budgetCount}</h3>
        </div>

        <div className="kpi-card">
          <span>Premium TVs (₹50K+)</span>
          <h3>{bestAnalytics.premiumCount}</h3>
        </div>

        <div className="kpi-card">
          <span>Stock %</span>
          <h3>{bestAnalytics.stockPercent}%</h3>
        </div>

        <div className="kpi-card">
          <span>Top Stock Platform</span>
          <h3>{bestAnalytics.topStockPlatform}</h3>
          <p style={{ fontSize: "12px", marginTop: "4px", color: "#6b7280" }}>
            Stock: {bestAnalytics.topStockCount}
          </p>
        </div>

        <div className="kpi-card">
          <span>Top Brand Listings</span>
          <h3>{bestAnalytics.topListingsBrand}</h3>
          <p style={{ fontSize: "12px", marginTop: "4px", color: "#6b7280" }}>
            Listings: {bestAnalytics.topListingsCount}
          </p>
        </div>
      </div>

      {/* ================= SEARCH ================= */}
      <section className="stats-section">
        <h3> Search TVs</h3>

        <div className="filter-grid">
          <input
            placeholder="Brand / Model"
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
          />

          <select
            value={displayType}
            onChange={e => setDisplayType(e.target.value)}
          >
            <option value="">Display Type</option>
            <option value="LED">LED</option>
            <option value="QLED">QLED</option>
            <option value="OLED">OLED</option>
          </select>

          <select
            value={screenSize}
            onChange={e => setScreenSize(e.target.value)}
          >
            <option value="">Size</option>
            <option value="43">43"</option>
            <option value="55">55"</option>
            <option value="65">65"</option>
          </select>

          <button onClick={handleSearch}>Search</button>
        </div>

        {searchResults.length > 0 && (
          <table>
            <thead>
              <tr>
                <th>Brand</th>
                <th>Model</th>
                <th>Price</th>
                <th>Rating</th>
              </tr>
            </thead>
            <tbody>
              {searchResults.map(tv => (
                <tr
                  key={tv.model_id}
                  className="clickable-row"
                  onClick={() => navigate(`/tv/${tv.model_id}`)}
                >
                  <td>{tv.brand}</td>
                  <td>{tv.full_name}</td>
                  <td>₹{tv.sale_price}</td>
                  <td>{tv.rating}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>

      {/* ================= BRAND ANALYTICS ================= */}
      <section className="stats-section">
        <h3> Brand Analytics</h3>
        <table>
          <thead>
            <tr>
              <th>Brand</th>
              <th>Total Models</th>
              <th>Total Listings</th>
            </tr>
          </thead>
          <tbody>
            {brandStats.map(b => (
              <tr key={b.brand}>
                <td
                  className="clickable"
                  onClick={() => navigate(`/brand/${b.brand}`)}
                >
                  {b.brand}
                </td>
                <td>{b.total_models}</td>
                <td>{b.total_listings}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      {/* ================= PLATFORM ANALYTICS ================= */}
      <section className="stats-section">
        <h3>Market Analytics</h3>
        <table>
          <thead>
            <tr>
              <th>Platform</th>
              <th>Unique Models</th>
              <th>Total Listings</th>
              <th>In Stock</th>
            </tr>
          </thead>
          <tbody>
            {platformStats.map(p => (
              <tr key={p.platform}>
                <td>{p.platform}</td>
                <td>{p.unique_models}</td>
                <td>{p.total_listings}</td>
                <td>{p.in_stock_count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
};

export default Statistics;
