import React, { useEffect, useState, useCallback } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { getBestDeals, getAllBrands, getPriceRange } from "../services/api";
import "./BestDeals.css";
import WishlistButton from "../components/WishlistButton";

/* ===============================
   STORAGE KEYS
================================ */
const STORAGE_KEY = "bestDeals_filters";
const SCROLL_KEY = "bestDeals_scrollPosition";

/* ===============================
   STAR RATING COMPONENT
================================ */
const StarRating = ({ rating }) => {
  const stars = [];
  const fullStars = Math.floor(rating || 0);
  const hasHalf = (rating || 0) - fullStars >= 0.5;

  for (let i = 0; i < 5; i++) {
    if (i < fullStars) {
      stars.push(<span key={i} className="star filled">★</span>);
    } else if (i === fullStars && hasHalf) {
      stars.push(<span key={i} className="star half">★</span>);
    } else {
      stars.push(<span key={i} className="star empty">☆</span>);
    }
  }

  return <span className="star-rating">{stars}</span>;
};

/* ===============================
   IMAGE WITH FALLBACK
================================ */
const ProductImage = ({ src, alt }) => {
  const [hasError, setHasError] = useState(false);

  if (!src || hasError) {
    return (
      <div className="product-image-placeholder">
        <span>📺</span>
      </div>
    );
  }

  return (
    <img
      src={src}
      alt={alt}
      className="product-image"
      onError={() => setHasError(true)}
    />
  );
};

/* ===============================
   PRODUCT CARD COMPONENT
================================ */
const ProductCard = ({ product, onClick, onPriceHistory, onBestPriceTracker }) => {
  const savings = product.price_difference || 0;
  const savingsPercent = product.savings_percent || 0;

  const handleButtonClick = (e, action) => {
    e.stopPropagation();
    action();
  };

  return (
    <div className="product-card" onClick={onClick}>
      {/* Wishlist Button */}
      <div className="wishlist-btn-container">
        <WishlistButton modelId={product.model_id} />
      </div>

      {/* Hot Deal Badge */}
      {savingsPercent > 20 && (
        <span className="hot-deal-badge">Hot Deal</span>
      )}

      {/* Product Image */}
      <div className="product-image-container">
        <ProductImage src={product.image_url} alt={product.full_name} />
      </div>

      {/* Product Info */}
      <div className="product-info">
        <h3 className="product-name">{product.full_name}</h3>

        {/* Rating */}
        <div className="product-rating">
          <span className="rating-badge">
            {(product.avg_rating || 0).toFixed(1)} <StarRating rating={product.avg_rating} />
          </span>
        </div>

        {/* Specs */}
        <ul className="product-specs">
          <li><strong>{product.display_type || "LED"}</strong></li>
          <li>Model ID: <strong>{product.model_id}</strong></li>
          <li>Available on: <strong>{product.platform_count} platforms</strong></li>
        </ul>

        {/* Price Comparison */}
        <div className="price-comparison">
          {product.platform_prices && Object.entries(product.platform_prices).map(([platform, price]) => (
            <div key={platform} className="platform-price">
              <span className="platform-name">{platform}</span>
              <span className="platform-price-value">₹{Number(price).toLocaleString("en-IN")}</span>
            </div>
          ))}
        </div>

        {/* Price Section */}
        <div className="product-price-section">
          <span className="current-price">₹{Number(product.min_price).toLocaleString("en-IN")}</span>
          {product.original_cost > product.min_price && (
            <>
              <span className="original-price">₹{Number(product.original_cost).toLocaleString("en-IN")}</span>
              <span className="discount-badge">{product.max_discount}% off</span>
            </>
          )}
        </div>

        {/* Savings */}
        {savings > 0 && (
          <div className="savings-info">
            <span className="savings-text">
              Save up to ₹{Number(savings).toLocaleString("en-IN")} ({savingsPercent}%)
            </span>
          </div>
        )}

        {/* Stock Status */}
        <div className={`stock-status ${product.stock_status === "in_stock" ? "in-stock" : "out-stock"}`}>
          {product.stock_status === "in_stock" ? "In Stock" : "Out of Stock"}
        </div>

        {/* Price History Buttons */}
        <div className="d-flex gap-2 mt-3">
          <button
            className="btn btn-success flex-fill d-flex align-items-center justify-content-center gap-2"
            onClick={(e) => handleButtonClick(e, onPriceHistory)}
          >
            <i className="bi bi-graph-up-arrow"></i>
            <span>Price History</span>
          </button>
          <button
            className="btn btn-warning flex-fill d-flex align-items-center justify-content-center gap-2 text-dark"
            onClick={(e) => handleButtonClick(e, onBestPriceTracker)}
          >
            <i className="bi bi-trophy-fill"></i>
            <span>Best Price</span>
          </button>
        </div>
      </div>
    </div>
  );
};

/* ===============================
   MAIN BEST DEALS PAGE
================================ */
function BestDeals() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();

  // ========== GET INITIAL FILTERS (URL → sessionStorage → defaults) ==========
  const getInitialFilters = useCallback(() => {
    // First check URL params
    const hasUrlParams = searchParams.toString().length > 0;
    
    if (hasUrlParams) {
      return {
        searchText: searchParams.get("search") || "",
        selectedBrands: searchParams.get("brands")?.split(",").filter(Boolean) || [],
        minPrice: Number(searchParams.get("minPrice")) || 0,
        maxPrice: Number(searchParams.get("maxPrice")) || 500000,
        minDiscount: searchParams.get("discount") ? Number(searchParams.get("discount")) : null,
        minRating: searchParams.get("rating") ? Number(searchParams.get("rating")) : null,
        sortBy: searchParams.get("sortBy") || "savings",
        sortOrder: searchParams.get("sortOrder") || "desc",
        page: Number(searchParams.get("page")) || 1,
      };
    }

    // Then check sessionStorage
    const saved = sessionStorage.getItem(STORAGE_KEY);
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        return {
          searchText: parsed.searchText || "",
          selectedBrands: parsed.selectedBrands || [],
          minPrice: parsed.minPrice || 0,
          maxPrice: parsed.maxPrice || 500000,
          minDiscount: parsed.minDiscount ?? null,
          minRating: parsed.minRating ?? null,
          sortBy: parsed.sortBy || "savings",
          sortOrder: parsed.sortOrder || "desc",
          page: parsed.page || 1,
        };
      } catch (e) {
        // Ignore parse errors
      }
    }

    // Default values
    return {
      searchText: "",
      selectedBrands: [],
      minPrice: 0,
      maxPrice: 500000,
      minDiscount: null,
      minRating: null,
      sortBy: "savings",
      sortOrder: "desc",
      page: 1,
    };
  }, [searchParams]);

  // State
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [brands, setBrands] = useState([]);
  const [priceRange, setPriceRange] = useState({ min: 0, max: 500000 });
  const [isInitialized, setIsInitialized] = useState(false);

  // Filters State - Initialize from URL or sessionStorage
  const initialFilters = getInitialFilters();
  const [searchText, setSearchText] = useState(initialFilters.searchText);
  const [selectedBrands, setSelectedBrands] = useState(initialFilters.selectedBrands);
  const [brandSearch, setBrandSearch] = useState("");
  const [minPrice, setMinPrice] = useState(initialFilters.minPrice);
  const [maxPrice, setMaxPrice] = useState(initialFilters.maxPrice);
  const [minDiscount, setMinDiscount] = useState(initialFilters.minDiscount);
  const [minRating, setMinRating] = useState(initialFilters.minRating);
  const [sortBy, setSortBy] = useState(initialFilters.sortBy);
  const [sortOrder, setSortOrder] = useState(initialFilters.sortOrder);
  const [page, setPage] = useState(initialFilters.page);
  const [showMoreBrands, setShowMoreBrands] = useState(false);

  // ========== SAVE FILTERS TO SESSION STORAGE ==========
  const saveFiltersToStorage = useCallback(() => {
    const filters = {
      searchText,
      selectedBrands,
      minPrice,
      maxPrice,
      minDiscount,
      minRating,
      sortBy,
      sortOrder,
      page,
    };
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(filters));
  }, [searchText, selectedBrands, minPrice, maxPrice, minDiscount, minRating, sortBy, sortOrder, page]);

  // ========== UPDATE URL WHEN FILTERS CHANGE ==========
  const updateURL = useCallback(() => {
    const params = new URLSearchParams();
    
    if (searchText) params.set("search", searchText);
    if (selectedBrands.length > 0) params.set("brands", selectedBrands.join(","));
    if (minPrice > 0) params.set("minPrice", minPrice.toString());
    if (maxPrice < priceRange.max && maxPrice !== 500000) params.set("maxPrice", maxPrice.toString());
    if (minDiscount !== null) params.set("discount", minDiscount.toString());
    if (minRating !== null) params.set("rating", minRating.toString());
    if (sortBy !== "savings") params.set("sortBy", sortBy);
    if (sortOrder !== "desc") params.set("sortOrder", sortOrder);
    if (page > 1) params.set("page", page.toString());

    setSearchParams(params, { replace: true });
  }, [searchText, selectedBrands, minPrice, maxPrice, minDiscount, minRating, sortBy, sortOrder, page, priceRange.max, setSearchParams]);

  // ========== SCROLL RESTORATION ==========
  useEffect(() => {
    const savedPosition = sessionStorage.getItem(SCROLL_KEY);
    if (savedPosition) {
      setTimeout(() => {
        window.scrollTo(0, parseInt(savedPosition, 10));
      }, 100);
    }

    return () => {
      sessionStorage.setItem(SCROLL_KEY, window.scrollY.toString());
    };
  }, []);

  // ========== SAVE SCROLL BEFORE NAVIGATION ==========
  const handleNavigate = (path) => {
    sessionStorage.setItem(SCROLL_KEY, window.scrollY.toString());
    saveFiltersToStorage();
    navigate(path);
  };

  // Navigate to Price History Page
  const handlePriceHistory = (product) => {
    sessionStorage.setItem(SCROLL_KEY, window.scrollY.toString());
    saveFiltersToStorage();
    const params = new URLSearchParams({
      tab: "history",
      name: product.full_name
    });
    navigate(`/price-history/${product.model_id}?${params.toString()}`);
  };

  const handleBestPriceTracker = (product) => {
    sessionStorage.setItem(SCROLL_KEY, window.scrollY.toString());
    saveFiltersToStorage();
    const params = new URLSearchParams({
      tab: "best",
      name: product.full_name
    });
    navigate(`/price-history/${product.model_id}?${params.toString()}`);
  };

  // Load initial data (brands & price range)
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        const [brandsRes, priceRes] = await Promise.all([
          getAllBrands(),
          getPriceRange()
        ]);
        setBrands(brandsRes.data);
        setPriceRange({ min: priceRes.data.min_price, max: priceRes.data.max_price });
        
        // Only set maxPrice if it's the default value
        if (maxPrice === 500000) {
          const savedFilters = sessionStorage.getItem(STORAGE_KEY);
          if (savedFilters) {
            const parsed = JSON.parse(savedFilters);
            if (parsed.maxPrice && parsed.maxPrice !== 500000) {
              setMaxPrice(parsed.maxPrice);
            } else {
              setMaxPrice(priceRes.data.max_price);
            }
          } else {
            setMaxPrice(priceRes.data.max_price);
          }
        }
        setIsInitialized(true);
      } catch (err) {
        console.error("Error loading initial data:", err);
        setIsInitialized(true);
      }
    };
    loadInitialData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Save filters to sessionStorage whenever they change
  useEffect(() => {
    if (isInitialized) {
      saveFiltersToStorage();
      updateURL();
    }
  }, [isInitialized, saveFiltersToStorage, updateURL]);

  // Load products when filters change
  useEffect(() => {
    if (!isInitialized) return;

    const fetchProducts = async () => {
      setLoading(true);
      try {
        const params = {
          page,
          page_size: 24,
          sort_by: sortBy,
          order: sortOrder,
		  min_price: minPrice,    // 👈 ADD THIS
		  max_price: maxPrice,
        };

        if (selectedBrands.length > 0) {
          params.brands = selectedBrands.join(",");
        }

        if (minDiscount) params.min_discount = minDiscount;
        if (minRating) params.min_rating = minRating;
        if (searchText) params.search = searchText;
		
		console.log("Fetching with params:", params);

        const res = await getBestDeals(params);
        setProducts(res.data);
      } catch (err) {
        console.error("Error loading products:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchProducts();
  }, [isInitialized, selectedBrands, minPrice, maxPrice, minDiscount, minRating, sortBy, sortOrder, page, searchText]);

  // Search handler
  const handleSearch = async () => {
    setPage(1);
  };

  // Brand filter handlers
  const toggleBrand = (brand) => {
    setSelectedBrands(prev =>
      prev.includes(brand)
        ? prev.filter(b => b !== brand)
        : [...prev, brand]
    );
    setPage(1);
  };

  // Filter brands by search
  const filteredBrands = brands.filter(b =>
    b.brand.toLowerCase().includes(brandSearch.toLowerCase())
  );

  const visibleBrands = showMoreBrands ? filteredBrands : filteredBrands.slice(0, 6);

  // Clear all filters
  const clearFilters = () => {
    setSelectedBrands([]);
    setMinPrice(0);
    setMaxPrice(priceRange.max);
    setMinDiscount(null);
    setMinRating(null);
    setSearchText("");
    setPage(1);
    // Clear storage
    sessionStorage.removeItem(STORAGE_KEY);
    setSearchParams({});
  };

  return (
    <div className="best-deals-page">
      {/* Search Bar */}
      <div className="search-section">
        <div className="search-bar">
          <input
            type="text"
            placeholder="Search TVs by brand, model, or name..."
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && handleSearch()}
          />
          <button onClick={handleSearch}>Search</button>
        </div>

        {/* Sort Options */}
        <div className="sort-section">
          <label>Sort by:</label>
          <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
            <option value="savings">Best Savings</option>
            <option value="price">Price</option>
            <option value="discount">Discount</option>
            <option value="rating">Rating</option>
          </select>
          <select value={sortOrder} onChange={(e) => setSortOrder(e.target.value)}>
            <option value="desc">High to Low</option>
            <option value="asc">Low to High</option>
          </select>
        </div>
      </div>

      <div className="content-wrapper">
        {/* Filters Sidebar - With Separate Scroll */}
        <aside className="filters-sidebar">
          <div className="filters-header">
            <h3>Filters</h3>
            <button className="clear-btn" onClick={clearFilters}>Clear All</button>
          </div>

          {/* Brand Filter */}
          <div className="filter-section">
            <h4>BRAND <span className="toggle-icon">▲</span></h4>
            <input
              type="text"
              placeholder="Search Brand"
              className="brand-search"
              value={brandSearch}
              onChange={(e) => setBrandSearch(e.target.value)}
            />
            <div className="filter-options">
              {visibleBrands.map(({ brand, count }) => (
                <label key={brand} className="filter-option">
                  <input
                    type="checkbox"
                    checked={selectedBrands.includes(brand)}
                    onChange={() => toggleBrand(brand)}
                  />
                  <span className="brand-name">{brand}</span>
                  <span className="brand-count">({count})</span>
                </label>
              ))}
            </div>
            {filteredBrands.length > 6 && (
              <button
                className="show-more-btn"
                onClick={() => setShowMoreBrands(!showMoreBrands)}
              >
                {showMoreBrands ? "Show Less" : `${filteredBrands.length - 6} MORE`}
              </button>
            )}
          </div>

          {/* Customer Ratings Filter */}
          <div className="filter-section">
            <h4>CUSTOMER RATINGS</h4>
            <div className="filter-options">
              {[4, 3, 2, 1].map(rating => (
                <label key={rating} className="filter-option">
                  <input
                    type="radio"
                    name="rating"
                    checked={minRating === rating}
                    onChange={() => setMinRating(minRating === rating ? null : rating)}
                  />
                  <span>{rating}★ & above</span>
                </label>
              ))}
            </div>
          </div>

          {/* Discount Filter */}
          <div className="filter-section">
            <h4>DISCOUNT</h4>
            <div className="filter-options">
              {[
                { label: "30% or more", value: 30 },
                { label: "20% or more", value: 20 },
                { label: "10% or more", value: 10 },
                { label: "10% and below", value: 0 },
              ].map(({ label, value }) => (
                <label key={value} className="filter-option">
                  <input
                    type="radio"
                    name="discount"
                    checked={minDiscount === value}
                    onChange={() => setMinDiscount(minDiscount === value ? null : value)}
                  />
                  <span>{label}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Price Filter - Simple Dropdowns Only */}
          <div className="filter-section">
            <div className="price-header">
              <h4>PRICE</h4>
              <button
                className="clear-price-btn"
                onClick={() => {
                  setMinPrice(0);
                  setMaxPrice(priceRange.max);
                }}
              >
                CLEAR
              </button>
            </div>

            {/* Price Dropdowns */}
            <div className="price-inputs">
              <select
                value={minPrice}
                onChange={(e) => setMinPrice(Number(e.target.value))}
              >
                <option value={0}>₹0+</option>
                <option value={10000}>₹10,000+</option>
                <option value={20000}>₹20,000+</option>
                <option value={30000}>₹30,000+</option>
                <option value={50000}>₹50,000+</option>
                <option value={75000}>₹75,000+</option>
                <option value={100000}>₹1,00,000+</option>
              </select>
              <span>to</span>
              <select
                value={maxPrice}
                onChange={(e) => setMaxPrice(Number(e.target.value))}
              >
                <option value={20000}>₹20,000</option>
                <option value={30000}>₹30,000</option>
                <option value={50000}>₹50,000</option>
                <option value={75000}>₹75,000</option>
                <option value={100000}>₹1,00,000</option>
                <option value={200000}>₹2,00,000</option>
                <option value={500000}>₹5,00,000</option>
                {priceRange.max > 500000 && (
                  <option value={priceRange.max}>₹{priceRange.max.toLocaleString("en-IN")}</option>
                )}
              </select>
            </div>
          </div>
        </aside>

        {/* Products Grid */}
        <main className="products-section">
          {/* Results Header */}
          <div className="results-header">
            <h2>Best TV Deals</h2>
            <span className="results-count">
              {loading ? "Loading..." : `${products.length} products found`}
            </span>
          </div>

          {/* Loading State */}
          {loading && (
            <div className="loading-container">
              <div className="spinner"></div>
              <p>Finding best deals...</p>
            </div>
          )}

          {/* Empty State */}
          {!loading && products.length === 0 && (
            <div className="empty-state">
              <span className="empty-icon">🔍</span>
              <h3>No products found</h3>
              <p>Try adjusting your filters or search terms</p>
              <button onClick={clearFilters}>Clear Filters</button>
            </div>
          )}

          {/* Products Grid */}
          {!loading && products.length > 0 && (
            <div className="products-grid">
              {products.map((product) => (
                <ProductCard
                  key={product.model_id}
                  product={product}
                  onClick={() => handleNavigate(`/compare/${product.model_id}`)}
                  onPriceHistory={() => handlePriceHistory(product)}
                  onBestPriceTracker={() => handleBestPriceTracker(product)}
                />
              ))}
            </div>
          )}

          {/* Pagination */}
          {!loading && products.length > 0 && (
            <div className="pagination">
              <button
                disabled={page === 1}
                onClick={() => setPage(p => p - 1)}
              >
                ← Previous
              </button>
              <span>Page {page}</span>
              <button
                disabled={products.length < 24}
                onClick={() => setPage(p => p + 1)}
              >
                Next →
              </button>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default BestDeals;