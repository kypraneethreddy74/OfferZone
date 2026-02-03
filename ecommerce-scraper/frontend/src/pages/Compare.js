import React, { useEffect, useState, useCallback } from "react";
import { filterProducts, searchProducts } from "../services/api";
import { useNavigate, useLocation, useSearchParams } from "react-router-dom";
import "./Compare.css";

/* ===============================
   STORAGE KEYS
================================ */
const STORAGE_KEY = "compare_state";
const SCROLL_KEY = "compare_scrollPosition";

/* ===============================
   TV IMAGE WITH FALLBACK
================================ */
const ImageWithFallback = ({ src, alt }) => {
  const [hasError, setHasError] = useState(false);

  if (!src || hasError) {
    return (
      <div
        style={{
          width: 80,
          height: 60,
          backgroundColor: "#f5f5f5",
          borderRadius: 8,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          border: "1px solid #e0e0e0",
        }}
      >
        <span style={{ fontSize: 28 }}>📺</span>
      </div>
    );
  }

  return (
    <img
      src={src}
      alt={alt || "TV"}
      width={80}
      height={60}
      style={{
        objectFit: "contain",
        backgroundColor: "#f5f5f5",
        borderRadius: 8,
        border: "1px solid #e0e0e0",
      }}
      onError={() => setHasError(true)}
    />
  );
};

/* ===============================
   EXTRACT SCREEN SIZE
================================ */
const getScreenSize = (name) => {
  if (!name) return "";
  
  const inchMatch = name.match(/(\d{2,3})\s*inch/i);
  if (inchMatch) return `${inchMatch[1]}"`;
  
  const cmMatch = name.match(/(\d{2,3})\s*cm/i);
  if (cmMatch) {
    const inches = Math.round(parseInt(cmMatch[1]) / 2.54);
    return `${inches}"`;
  }
  
  return "";
};

/* ===============================
   REMOVE DUPLICATES
================================ */
const deduplicateModels = (data) => {
  const map = {};
  data.forEach((p) => {
    if (!map[p.model_id]) map[p.model_id] = p;
  });
  return Object.values(map);
};

function Compare() {
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams, setSearchParams] = useSearchParams();

  // ========== GET INITIAL STATE (URL → sessionStorage → defaults) ==========
  const getInitialState = useCallback(() => {
    // First check URL params
    const urlSearch = searchParams.get("search");
    if (urlSearch) {
      return { searchText: urlSearch, products: [], fromUrl: true };
    }

    // Then check sessionStorage
    const saved = sessionStorage.getItem(STORAGE_KEY);
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        return {
          searchText: parsed.searchText || "",
          products: parsed.products || [],
          fromUrl: false
        };
      } catch (e) {
        // Ignore
      }
    }

    return { searchText: "", products: [], fromUrl: false };
  }, [searchParams]);

  const initialState = getInitialState();
  const [searchText, setSearchText] = useState(initialState.searchText);
  const [products, setProducts] = useState(initialState.products);
  const [loading, setLoading] = useState(false);
  const [isInitialized, setIsInitialized] = useState(false);

  // ========== SAVE STATE TO SESSION STORAGE ==========
  const saveState = useCallback(() => {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify({
      searchText,
      products
    }));
  }, [searchText, products]);

  // ========== SCROLL RESTORATION ==========
  useEffect(() => {
    const savedPosition = sessionStorage.getItem(SCROLL_KEY);
    if (savedPosition && products.length > 0) {
      setTimeout(() => {
        window.scrollTo(0, parseInt(savedPosition, 10));
      }, 100);
    }

    return () => {
      sessionStorage.setItem(SCROLL_KEY, window.scrollY.toString());
    };
  }, [products.length]);

  // ========== UPDATE URL ==========
  useEffect(() => {
    if (searchText && isInitialized) {
      setSearchParams({ search: searchText }, { replace: true });
    }
  }, [searchText, isInitialized, setSearchParams]);

  // ========== SAVE STATE ON CHANGE ==========
  useEffect(() => {
    if (isInitialized) {
      saveState();
    }
  }, [isInitialized, saveState]);

  // ========== INITIAL LOAD ==========
  useEffect(() => {
    // If coming from Filters page with state
    if (location.state) {
      const { brand, min_price, max_price, display_type, screen_size } = location.state;
      setSearchText(brand || "");
      setLoading(true);

      filterProducts({ brand, min_price, max_price, display_type })
        .then((res) => {
          let data = deduplicateModels(res.data);
          if (screen_size) {
            data = data.filter((p) =>
              p.full_name?.toLowerCase().includes(`${screen_size} inch`)
            );
          }
          setProducts(data);
          setIsInitialized(true);
        })
        .catch((err) => console.error("Filter error:", err))
        .finally(() => setLoading(false));
    } 
    // If URL has search param but no products (came from URL directly)
    else if (initialState.fromUrl && initialState.searchText) {
      setLoading(true);
      searchProducts(initialState.searchText)
        .then((res) => {
          setProducts(deduplicateModels(res.data));
          setIsInitialized(true);
        })
        .catch((err) => console.error("Search error:", err))
        .finally(() => setLoading(false));
    }
    // If we have saved products from sessionStorage
    else if (initialState.products.length > 0) {
      setIsInitialized(true);
    }
    // Fresh start
    else {
      setIsInitialized(true);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.state]);

  /* Search handler */
  const searchTV = async () => {
    if (!searchText.trim()) return;
    setLoading(true);
    try {
      const res = await searchProducts(searchText);
      const data = deduplicateModels(res.data);
      setProducts(data);
    } catch (err) {
      console.error("Search error:", err);
    } finally {
      setLoading(false);
    }
  };

  /* Enter key handler */
  const handleKeyPress = (e) => {
    if (e.key === "Enter") searchTV();
  };

  /* Navigate to compare result */
  const handleNavigate = (modelId) => {
    saveState();
    sessionStorage.setItem(SCROLL_KEY, window.scrollY.toString());
    navigate(`/compare/${modelId}`);
  };

  return (
    <div className="container py-4">
      <h4 className="mb-4 fw-semibold text-primary">Compare TVs</h4>

      {/* Search Bar */}
      <div className="row g-2 mb-4">
        <div className="col-md-9">
          <input
            className="form-control form-control-lg"
            placeholder="Search TV (Brand, Model, Name)"
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            onKeyPress={handleKeyPress}
          />
        </div>
        <div className="col-md-3">
          <button
            className="btn btn-warning btn-lg w-100 fw-semibold"
            onClick={searchTV}
            disabled={loading}
          >
            {loading ? "Searching..." : "Search"}
          </button>
        </div>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="text-center py-5">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      )}

      {/* Empty State */}
      {!loading && products.length === 0 && (
        <div className="text-muted text-center py-5">
          <span style={{ fontSize: 48 }}>🔍</span>
          <p className="mt-3">No TVs found. Try searching for a brand or model.</p>
        </div>
      )}

      {/* Results */}
      {!loading && products.length > 0 && (
        <div className="list-group shadow-sm">
          {products.map((p) => (
            <div
              key={p.model_id}
              className="list-group-item list-group-item-action py-3"
              onClick={() => handleNavigate(p.model_id)}
              style={{ cursor: "pointer" }}
            >
              <div className="d-flex align-items-center gap-3">
                <ImageWithFallback src={p.image_url} alt={p.full_name} />

                <div className="flex-grow-1">
                  <div className="fw-semibold text-dark">{p.full_name}</div>
                  <small className="text-muted">
                    {getScreenSize(p.full_name)} {p.display_type && `| ${p.display_type}`}
                  </small>
                </div>

                <div className="text-end">
                  <div className="fw-bold text-success fs-5">
                    ₹{p.sale_price?.toLocaleString("en-IN")}
                  </div>
                  {p.discount > 0 && (
                    <small className="text-danger">{p.discount}% off</small>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default Compare;