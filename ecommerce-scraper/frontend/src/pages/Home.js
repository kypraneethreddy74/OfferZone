import React from "react";
import "./Home.css";
import { useNavigate } from "react-router-dom";

export default function Home() {
  const navigate = useNavigate();

  return (
    <div className="home">
      {/* HERO SECTION */}
      <section className="hero">
        <div className="hero-grid">
          <div className="hero-text">
            <h1>
              Stop Hunting. <br />
              Start <span>Saving.</span>
            </h1>
            <p>
              Compare prices across Amazon, Flipkart, and Croma in real-time. 
              We track 25,000+ products so you never pay full price again.
            </p>

            <div className="hero-buttons">
              <button className="btn-primary" onClick={() => navigate("/best-deals")}>
                Find Best Deals
              </button>
              <button className="btn-outline" onClick={() => navigate("/catalog")}>
                Browse Catalog
              </button>
            </div>
          </div>

          <div className="hero-image-wrap">
            <img
              src="https://illustrations.popsy.co/white/online-shopping.svg" 
              alt="Shopping Illustration"
              className="hero-image"
            />
          </div>
        </div>
      </section>

      {/* PROBLEM SECTION */}
      <section className="section">
        <div className="section-header">
            <h2>Shopping is broken 😤</h2>
            <p>Traditional shopping takes too much time and brainpower.</p>
        </div>
        <div className="grid-3">
          <div className="card">
            <span className="card-icon">💸</span>
            <h3>Price Volatility</h3>
            <p>Prices change every hour. You might buy today and regret tomorrow.</p>
          </div>
          <div className="card">
            <span className="card-icon">😵‍💫</span>
            <h3>Tab Overload</h3>
            <p>Opening 10 tabs to compare one phone? There's a better way.</p>
          </div>
          <div className="card">
            <span className="card-icon">📉</span>
            <h3>Hidden Fees</h3>
            <p>Fake discounts make you think you're saving when you aren't.</p>
          </div>
        </div>
      </section>

      {/* SOLUTION / FEATURES */}
      <section className="section" style={{background: '#fff', borderRadius: '60px'}}>
        <div className="section-header">
            <h2>The OfferZone Edge ⚡</h2>
        </div>
        <div className="grid-3">
          <div className="card">
            <span className="card-icon">🔍</span>
            <h3>Smart Search</h3>
            <p>One search, all platforms. We do the heavy lifting for you.</p>
          </div>
          <div className="card">
            <span className="card-icon">📈</span>
            <h3>Price History</h3>
            <p>See the lowest price a product has ever hit before you buy.</p>
          </div>
          <div className="card">
            <span className="card-icon">🔔</span>
            <h3>Real-time Alerts</h3>
            <p>Get notified the second your favorite gadget goes on sale.</p>
          </div>
        </div>
      </section>

      {/* CTA SECTION */}
      <div className="cta-wrapper">
        <section className="cta">
            <h2>Ready to save ₹10,000?</h2>
            <p style={{marginBottom: '30px', opacity: 0.8}}>Join thousands of smart shoppers using OfferZone today.</p>
            <button className="btn-primary" onClick={() => navigate("/best-deals")}>
            Get Started — It's Free
            </button>
        </section>
      </div>
    </div>
  );
}