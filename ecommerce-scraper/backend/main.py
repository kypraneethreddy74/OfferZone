"""
Main FastAPI Application - OfferZone TV Price Intelligence
"""

from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, text
from typing import List, Optional
from contextlib import asynccontextmanager
from datetime import date, timedelta
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from alert_engine import run_alert_engine
from admin import admin_router
from user_settings import settings_router

load_dotenv()
scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - start scheduler on startup"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables ready")
    
    # Start alert scheduler (every 30 minutes)
    scheduler.add_job(run_alert_engine, 'interval', minutes=30, id='alert_engine')
    scheduler.start()
    print("✅ Alert scheduler started (runs every 30 min)")
    
    yield
    
    # Shutdown
    scheduler.shutdown()
    print("👋 Shutting down")


# ================= DB & MODELS =================
from db import get_db, engine
from models import (
    Base,
    TVPlatformLatest,
    TVBrandMaster,
    TVPlatformMaster,
    User,
    RefreshSession
)
from schemas import (
    TVProductOut,
    BrandAnalyticsOut,
    PlatformAnalyticsOut
)

# ================= AUTH =================
from auth import auth_router, get_current_active_user, require_admin
from wishlist import wishlist_router
from alerts import alerts_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - create tables on startup"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables ready")
    yield
    print("👋 Shutting down")


app = FastAPI(
    title="OfferZone TV Price Intelligence API",
    version="2.0.0",
    lifespan=lifespan
)

# Static files
if os.path.exists("images"):
    app.mount("/images", StaticFiles(directory="images"), name="images")

# ======================================================
# CORS (REACT + CREDENTIALS SUPPORT)
# ======================================================
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_URL,
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======================================================
# INCLUDE AUTH ROUTER
# ======================================================
app.include_router(auth_router)

app.include_router(wishlist_router)

app.include_router(alerts_router)

app.include_router(admin_router)

app.include_router(settings_router)

# ======================================================
# HEALTH CHECK
# ======================================================
@app.get("/")
def health():
    return {"status": "API running", "auth": "enabled"}


# ======================================================
# PRODUCTS ENDPOINTS
# ======================================================

@app.get("/products", response_model=List[TVProductOut])
def get_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("sale_price"),
    order: str = Query("asc"),
    db: Session = Depends(get_db)
):
    query = db.query(TVPlatformLatest).filter(
        TVPlatformLatest.sale_price > 0,
        TVPlatformLatest.original_cost > 0
    )

    if hasattr(TVPlatformLatest, sort_by):
        column = getattr(TVPlatformLatest, sort_by)
        query = query.order_by(
            column.desc() if order == "desc" else column.asc()
        )

    return (
        query
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )


@app.get("/products/filter", response_model=List[TVProductOut])
def filter_products(
    brand: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    display_type: Optional[str] = None,
    in_stock_only: bool = False,
    db: Session = Depends(get_db)
):
    query = db.query(TVPlatformLatest).filter(
        TVPlatformLatest.sale_price > 0,
        TVPlatformLatest.original_cost > 0
    )

    if brand:
        query = query.filter(TVPlatformLatest.brand.ilike(f"%{brand}%"))
    if min_price is not None:
        query = query.filter(TVPlatformLatest.sale_price >= min_price)
    if max_price is not None:
        query = query.filter(TVPlatformLatest.sale_price <= max_price)
    if display_type:
        query = query.filter(TVPlatformLatest.display_type == display_type)
    if in_stock_only:
        query = query.filter(TVPlatformLatest.stock_status == "in_stock")

    return query.all()


@app.get("/products/compare", response_model=List[TVProductOut])
def compare_products(model_id: str, db: Session = Depends(get_db)):
    results = (
        db.query(TVPlatformLatest)
        .filter(
            TVPlatformLatest.model_id == model_id,
            TVPlatformLatest.sale_price > 0,
            TVPlatformLatest.original_cost > 0
        )
        .order_by(TVPlatformLatest.sale_price.asc())
        .all()
    )

    if not results:
        raise HTTPException(status_code=404, detail="No valid priced products found")

    return results


@app.get("/products/search", response_model=List[TVProductOut])
def search_products(q: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    keyword = f"%{q.strip().lower()}%"

    return (
        db.query(TVPlatformLatest)
        .filter(
            TVPlatformLatest.sale_price > 0,
            TVPlatformLatest.original_cost > 0,
            or_(
                func.lower(TVPlatformLatest.brand).like(keyword),
                func.lower(TVPlatformLatest.full_name).like(keyword),
                func.lower(TVPlatformLatest.display_type).like(keyword),
                func.lower(TVPlatformLatest.model_id).like(keyword),
            )
        )
        .order_by(TVPlatformLatest.sale_price.asc())
        .limit(50)
        .all()
    )


@app.get("/products/best-deals")
def get_best_deals(
    search: Optional[str] = None,
    brands: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_discount: Optional[float] = None,
    min_rating: Optional[float] = None,
    sort_by: str = Query("savings", regex="^(savings|price|discount|rating)$"),
    order: str = Query("desc", regex="^(asc|desc)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(24, ge=1, le=100),
    db: Session = Depends(get_db)
):
    try:
        query = text("""
            WITH price_stats AS (
                SELECT 
                    model_id,
                    MIN(full_name) as full_name,
                    MIN(brand) as brand,
                    MIN(display_type) as display_type,
                    MIN(image_url) as image_url,
                    COUNT(DISTINCT platform) as platform_count,
                    MIN(sale_price) as min_price,
                    MAX(sale_price) as max_price,
                    AVG(sale_price) as avg_price,
                    MAX(sale_price) - MIN(sale_price) as price_difference,
                    MAX(original_cost) as original_cost,
                    MAX(discount) as max_discount,
                    AVG(rating) as avg_rating,
                    GROUP_CONCAT(DISTINCT platform) as platforms,
                    GROUP_CONCAT(DISTINCT CONCAT(platform, ':', sale_price)) as platform_prices,
                    MIN(stock_status) as stock_status
                FROM tv_platform_latest_master
                WHERE sale_price > 0 AND original_cost > 0
                GROUP BY model_id
                HAVING COUNT(DISTINCT platform) >= 1
            )
            SELECT 
                model_id, full_name, brand, display_type, image_url,
                platform_count, min_price, max_price, avg_price,
                price_difference, original_cost, max_discount, avg_rating,
                platforms, platform_prices, stock_status,
                ROUND((price_difference / max_price) * 100, 1) as savings_percent
            FROM price_stats
            WHERE 1=1
            {brand_filter}
            {price_filter}
            {discount_filter}
            {rating_filter}
            {search_filter}
            ORDER BY {sort_column} {sort_order}
            LIMIT :limit OFFSET :offset
        """.format(
            brand_filter="AND brand IN ({})".format(
                ",".join([f"'{b.strip()}'" for b in brands.split(",")])
            ) if brands else "",
            price_filter=f"AND min_price >= {min_price}" if min_price else "" +
                        f" AND min_price <= {max_price}" if max_price else "",
            discount_filter=f"AND max_discount >= {min_discount}" if min_discount else "",
            rating_filter=f"AND avg_rating >= {min_rating}" if min_rating else "",
            search_filter=f"AND (LOWER(full_name) LIKE '%{search.lower()}%' OR LOWER(brand) LIKE '%{search.lower()}%' OR LOWER(model_id) LIKE '%{search.lower()}%')" if search else "",
            sort_column={
                "savings": "price_difference",
                "price": "min_price",
                "discount": "max_discount",
                "rating": "avg_rating"
            }.get(sort_by, "price_difference"),
            sort_order=order.upper()
        ))

        result = db.execute(query, {"limit": page_size, "offset": (page - 1) * page_size})

        deals = []
        for row in result:
            row_dict = dict(row._mapping)
            platform_prices = {}
            if row_dict.get("platform_prices"):
                for pp in row_dict["platform_prices"].split(","):
                    if ":" in pp:
                        platform, price = pp.split(":")
                        platform_prices[platform] = float(price)
            row_dict["platform_prices"] = platform_prices
            row_dict["platforms"] = row_dict.get("platforms", "").split(",") if row_dict.get("platforms") else []
            deals.append(row_dict)

        return deals
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ======================================================
# ANALYTICS ENDPOINTS
# ======================================================

@app.get("/analytics/brands", response_model=List[BrandAnalyticsOut])
def brand_analytics(db: Session = Depends(get_db)):
    return db.query(TVBrandMaster).all()


@app.get("/analytics/platforms", response_model=List[PlatformAnalyticsOut])
def platform_analytics(db: Session = Depends(get_db)):
    return db.query(TVPlatformMaster).all()


@app.get("/analytics/products")
def product_statistics(db: Session = Depends(get_db)):
    try:
        result = db.execute(
            text("""
                SELECT
                    model_id, full_name, brand, total_platforms,
                    avg_price, min_price, max_price, avg_discount,
                    avg_rating, in_stock_count
                FROM product_statistics
                ORDER BY avg_price ASC
            """)
        )
        return [dict(row._mapping) for row in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ======================================================
# ✅ NEW BEST STATISTICS ENDPOINT (DASHBOARD READY)
# ======================================================

@app.get("/analytics/statistics")
def get_best_statistics(db: Session = Depends(get_db)):
    try:
        # -------------------- OVERALL KPIs --------------------
        overall = db.execute(text("""
            SELECT 
                COUNT(*) as total_tvs,
                ROUND(AVG(sale_price), 2) as avg_sale_price,
                ROUND(AVG(discount), 2) as avg_discount,
                ROUND(AVG(rating), 2) as avg_rating,
                MIN(sale_price) as min_sale_price,
                MAX(sale_price) as max_sale_price
            FROM tv_platform_latest_master
            WHERE sale_price > 0 AND original_cost > 0
        """)).fetchone()

        overall_stats = {
            "total_tvs": int(overall.total_tvs or 0),
            "avg_sale_price": float(overall.avg_sale_price or 0),
            "avg_discount": float(overall.avg_discount or 0),
            "avg_rating": float(overall.avg_rating or 0),
            "min_sale_price": float(overall.min_sale_price or 0),
            "max_sale_price": float(overall.max_sale_price or 0),
        }

        # -------------------- BEST VALUE TVs --------------------
        best_value = db.execute(text("""
            SELECT 
                model_id,
                MIN(full_name) as full_name,
                MIN(brand) as brand,
                MIN(image_url) as image_url,
                MIN(platform) as platform,
                MIN(sale_price) as sale_price,
                MAX(discount) as discount,
                ROUND(AVG(rating), 2) as rating,
                ROUND((MAX(discount)*0.6 + (AVG(rating)*10)*0.4), 2) as value_score
            FROM tv_platform_latest_master
            WHERE sale_price > 0 AND original_cost > 0
            GROUP BY model_id
            ORDER BY value_score DESC
            LIMIT 10
        """)).fetchall()

        top_best_value_tvs = [dict(row._mapping) for row in best_value]

        # -------------------- BRAND STATS --------------------
        brand_stats = db.execute(text("""
            SELECT
                brand,
                COUNT(DISTINCT model_id) as total_models,
                ROUND(AVG(sale_price), 2) as avg_price,
                ROUND(AVG(discount), 2) as avg_discount,
                ROUND(AVG(rating), 2) as avg_rating
            FROM tv_platform_latest_master
            WHERE sale_price > 0 AND original_cost > 0
            GROUP BY brand
            ORDER BY avg_rating DESC
            LIMIT 20
        """)).fetchall()

        brand_stats = [dict(row._mapping) for row in brand_stats]

        # -------------------- PLATFORM STATS --------------------
        platform_stats = db.execute(text("""
            SELECT
                platform,
                SUM(unique_models) as total_models,
                SUM(total_listings) as total_listings,
                SUM(in_stock_count) as total_in_stock,
                ROUND(SUM(in_stock_count) / NULLIF(SUM(total_listings), 0), 2) as stock_ratio
            FROM tv_platform_master
            GROUP BY platform
            ORDER BY stock_ratio DESC
        """)).fetchall()

        platform_stats = [dict(row._mapping) for row in platform_stats]

        # -------------------- PRICE SEGMENTS --------------------
        segment_stats = db.execute(text("""
            SELECT 
                CASE
                    WHEN sale_price BETWEEN 1 AND 25000 THEN 'Budget'
                    WHEN sale_price BETWEEN 25001 AND 50000 THEN 'Mid-Range'
                    WHEN sale_price BETWEEN 50001 AND 100000 THEN 'Premium'
                    ELSE 'Luxury'
                END as segment,
                COUNT(*) as total_tvs,
                ROUND(AVG(discount), 2) as avg_discount,
                ROUND(AVG(rating), 2) as avg_rating
            FROM tv_platform_latest_master
            WHERE sale_price > 0 AND original_cost > 0
            GROUP BY segment
            ORDER BY total_tvs DESC
        """)).fetchall()

        segment_stats = [dict(row._mapping) for row in segment_stats]

        return {
            "overall": overall_stats,
            "top_best_value_tvs": top_best_value_tvs,
            "brand_stats": brand_stats,
            "platform_stats": platform_stats,
            "segment_stats": segment_stats
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ======================================================
# PLATFORMS ENDPOINTS
# ======================================================

@app.get("/platforms/list", response_model=List[str])
def get_platforms(db: Session = Depends(get_db)):
    platforms = (
        db.query(TVPlatformLatest.platform)
        .distinct()
        .order_by(TVPlatformLatest.platform)
        .all()
    )
    return [p[0] for p in platforms]


@app.get("/platforms/{platform}/brands", response_model=List[str])
def get_brands_by_platform(platform: str, db: Session = Depends(get_db)):
    brands = (
        db.query(TVPlatformLatest.brand)
        .filter(TVPlatformLatest.platform == platform)
        .distinct()
        .order_by(TVPlatformLatest.brand)
        .all()
    )

    if not brands:
        raise HTTPException(status_code=404, detail="Platform not found or no brands")

    return [b[0] for b in brands]


@app.get("/platforms/{platform}/brands/{brand}/models", response_model=List[TVProductOut])
def get_models_by_platform_brand(
    platform: str,
    brand: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db)
):
    base_query = (
        db.query(TVPlatformLatest)
        .filter(
            TVPlatformLatest.platform == platform,
            TVPlatformLatest.brand == brand,
            TVPlatformLatest.sale_price > 0
        )
    )

    total = base_query.count()
    if total == 0:
        raise HTTPException(status_code=404, detail="No models found")

    return (
        base_query
        .order_by(TVPlatformLatest.sale_price.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )


# ======================================================
# FILTERS ENDPOINTS
# ======================================================

@app.get("/filters/brands")
def get_all_brands(db: Session = Depends(get_db)):
    result = db.execute(text("""
        SELECT DISTINCT brand, COUNT(*) as count
        FROM tv_platform_latest_master
        WHERE brand IS NOT NULL AND brand != ''
        GROUP BY brand
        ORDER BY count DESC
    """))
    return [{"brand": row.brand, "count": row.count} for row in result]


@app.get("/filters/price-range")
def get_price_range(db: Session = Depends(get_db)):
    result = db.execute(text("""
        SELECT MIN(sale_price) as min_price, MAX(sale_price) as max_price
        FROM tv_platform_latest_master
        WHERE sale_price > 0
    """))
    row = result.fetchone()
    return {"min_price": row.min_price or 0, "max_price": row.max_price or 500000}


# ======================================================
# PRICE HISTORY CHART ENDPOINTS
# ======================================================

@app.get("/products/{model_id}/charts/price-history")
def get_price_history_chart(
    model_id: str,
    days: int = Query(30, ge=7, le=365),
    db: Session = Depends(get_db)
):
    """Generate price history charts - PriceHistory.in style"""
    try:
        from charts import (
            create_price_history_matplotlib,
            create_price_comparison_seaborn,
            create_platform_heatmap,
            create_all_platforms_combined,
            create_empty_chart
        )

        end_date = date.today()
        start_date = end_date - timedelta(days=days)

        result = db.execute(text("""
            SELECT 
                platform,
                DATE(scraped_at) as price_date,
                MIN(sale_price) as min_price,
                MIN(full_name) as full_name,
                MIN(brand) as brand
            FROM tv_platform_latest_master
            WHERE model_id = :model_id
                AND sale_price > 0
                AND DATE(scraped_at) >= :start_date
                AND DATE(scraped_at) <= :end_date
            GROUP BY platform, DATE(scraped_at)
            ORDER BY price_date
        """), {
            "model_id": model_id,
            "start_date": start_date,
            "end_date": end_date
        })

        rows = result.fetchall()

        if not rows:
            empty_chart = create_empty_chart(f"No price history for last {days} days")
            return {
                "model_id": model_id,
                "product_name": "Unknown",
                "charts": {
                    "line_chart": empty_chart,
                    "comparison_chart": empty_chart,
                    "heatmap_chart": empty_chart,
                    "combined_chart": empty_chart
                }
            }

        data = [dict(row._mapping) for row in rows]
        product_name = data[0].get('full_name', model_id)

        return {
            "model_id": model_id,
            "product_name": product_name,
            "data_points": len(data),
            "charts": {
                "line_chart": create_price_history_matplotlib(data, model_id, product_name),
                "comparison_chart": create_price_comparison_seaborn(data, model_id, product_name),
                "heatmap_chart": create_platform_heatmap(data, model_id, product_name),
                "combined_chart": create_all_platforms_combined(data, model_id, product_name)
            }
        }

    except ImportError as e:
        raise HTTPException(status_code=500, detail=f"Missing module: {str(e)}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/products/{model_id}/charts/best-price")
def get_best_price_chart(
    model_id: str,
    days: int = Query(30, ge=7, le=90),
    db: Session = Depends(get_db)
):
    """Generate best price tracker chart using Matplotlib"""
    try:
        from charts import create_best_price_tracker_matplotlib, create_empty_chart

        end_date = date.today()
        start_date = end_date - timedelta(days=days)

        result = db.execute(text("""
            SELECT 
                platform,
                DATE(scraped_at) as price_date,
                MIN(sale_price) as min_price,
                MIN(full_name) as full_name
            FROM tv_platform_latest_master
            WHERE model_id = :model_id
                AND sale_price > 0
                AND DATE(scraped_at) >= :start_date
                AND DATE(scraped_at) <= :end_date
            GROUP BY platform, DATE(scraped_at)
            ORDER BY price_date, min_price
        """), {
            "model_id": model_id,
            "start_date": start_date,
            "end_date": end_date
        })

        rows = result.fetchall()
        print(f"[DEBUG] Best price - Found {len(rows)} rows for model_id: {model_id}")

        if not rows:
            empty_chart = create_empty_chart(f"No price history data available for the last {days} days")
            return {
                "model_id": model_id,
                "product_name": "No data found",
                "message": f"No price history in last {days} days",
                "chart": empty_chart
            }

        date_prices = {}
        product_name = None

        for row in rows:
            price_date = row.price_date
            if price_date not in date_prices:
                date_prices[price_date] = {}
            date_prices[price_date][row.platform] = float(row.min_price)
            if not product_name:
                product_name = row.full_name

        best_price_data = []
        for price_date in sorted(date_prices.keys()):
            prices = date_prices[price_date]
            best_platform = min(prices, key=prices.get)
            best_price = prices[best_platform]

            best_price_data.append({
                "date": price_date,
                "best_platform": best_platform,
                "best_price": best_price,
                "all_prices": prices
            })

        chart = create_best_price_tracker_matplotlib(
            best_price_data,
            model_id,
            product_name or model_id
        )

        return {
            "model_id": model_id,
            "product_name": product_name or model_id,
            "data_points": len(best_price_data),
            "chart": chart
        }

    except ImportError as e:
        print(f"[ERROR] Import Error: {e}")
        raise HTTPException(status_code=500, detail=f"Missing module: {str(e)}")
    except Exception as e:
        print(f"[ERROR] Best price chart failed: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ======================================================
# DEBUG ENDPOINT
# ======================================================

@app.get("/debug/check-data/{model_id}")
def debug_check_data(model_id: str, db: Session = Depends(get_db)):
    """Debug endpoint to check if data exists for a model"""
    try:
        total_result = db.execute(text("""
            SELECT COUNT(*) as total 
            FROM tv_platform_latest_master 
            WHERE model_id = :model_id
        """), {"model_id": model_id})
        total = total_result.fetchone().total

        dates_result = db.execute(text("""
            SELECT DISTINCT DATE(scraped_at) as scrape_date
            FROM tv_platform_latest_master 
            WHERE model_id = :model_id
            ORDER BY scrape_date DESC
            LIMIT 10
        """), {"model_id": model_id})
        dates = [str(row.scrape_date) for row in dates_result]

        platforms_result = db.execute(text("""
            SELECT DISTINCT platform
            FROM tv_platform_latest_master 
            WHERE model_id = :model_id
        """), {"model_id": model_id})
        platforms = [row.platform for row in platforms_result]

        sample_result = db.execute(text("""
            SELECT platform, sale_price, scraped_at, full_name
            FROM tv_platform_latest_master 
            WHERE model_id = :model_id
            LIMIT 5
        """), {"model_id": model_id})
        samples = [dict(row._mapping) for row in sample_result]

        return {
            "model_id": model_id,
            "total_records": total,
            "unique_dates": dates,
            "platforms": platforms,
            "sample_data": samples
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ======================================================
# ✅ BEST STATISTICS ENDPOINT (DASHBOARD READY)
# ======================================================

@app.get("/analytics/statistics")
def get_best_statistics(db: Session = Depends(get_db)):
    try:
        # -------------------- OVERALL KPIs --------------------
        overall = db.execute(text("""
            SELECT 
                COUNT(*) as total_tvs,
                ROUND(AVG(sale_price), 2) as avg_sale_price,
                ROUND(AVG(discount), 2) as avg_discount,
                ROUND(AVG(rating), 2) as avg_rating,
                MIN(sale_price) as min_sale_price,
                MAX(sale_price) as max_sale_price
            FROM tv_platform_latest_master
            WHERE sale_price > 0 AND original_cost > 0
        """)).fetchone()

        overall_stats = {
            "total_tvs": int(overall.total_tvs or 0),
            "avg_sale_price": float(overall.avg_sale_price or 0),
            "avg_discount": float(overall.avg_discount or 0),
            "avg_rating": float(overall.avg_rating or 0),
            "min_sale_price": float(overall.min_sale_price or 0),
            "max_sale_price": float(overall.max_sale_price or 0),
        }

        # -------------------- BEST VALUE TVs --------------------
        best_value = db.execute(text("""
            SELECT 
                model_id,
                MIN(full_name) as full_name,
                MIN(brand) as brand,
                MIN(image_url) as image_url,
                MIN(platform) as platform,
                MIN(sale_price) as sale_price,
                MAX(discount) as discount,
                ROUND(AVG(rating), 2) as rating,
                ROUND((MAX(discount)*0.6 + (AVG(rating)*10)*0.4), 2) as value_score
            FROM tv_platform_latest_master
            WHERE sale_price > 0 AND original_cost > 0
            GROUP BY model_id
            ORDER BY value_score DESC
            LIMIT 10
        """)).fetchall()

        top_best_value_tvs = [dict(row._mapping) for row in best_value]

        # -------------------- BRAND STATS --------------------
        brand_stats = db.execute(text("""
            SELECT
                brand,
                COUNT(DISTINCT model_id) as total_models,
                ROUND(AVG(sale_price), 2) as avg_price,
                ROUND(AVG(discount), 2) as avg_discount,
                ROUND(AVG(rating), 2) as avg_rating
            FROM tv_platform_latest_master
            WHERE sale_price > 0 AND original_cost > 0
            GROUP BY brand
            ORDER BY avg_rating DESC
            LIMIT 20
        """)).fetchall()

        brand_stats = [dict(row._mapping) for row in brand_stats]

        # -------------------- PLATFORM STATS --------------------
        platform_stats = db.execute(text("""
            SELECT
                platform,
                SUM(unique_models) as total_models,
                SUM(total_listings) as total_listings,
                SUM(in_stock_count) as total_in_stock,
                ROUND(SUM(in_stock_count) / NULLIF(SUM(total_listings), 0), 2) as stock_ratio
            FROM tv_platform_master
            GROUP BY platform
            ORDER BY stock_ratio DESC
        """)).fetchall()

        platform_stats = [dict(row._mapping) for row in platform_stats]

        # -------------------- PRICE SEGMENTS --------------------
        segment_stats = db.execute(text("""
            SELECT 
                CASE
                    WHEN sale_price BETWEEN 1 AND 25000 THEN 'Budget'
                    WHEN sale_price BETWEEN 25001 AND 50000 THEN 'Mid-Range'
                    WHEN sale_price BETWEEN 50001 AND 100000 THEN 'Premium'
                    ELSE 'Luxury'
                END as segment,
                COUNT(*) as total_tvs,
                ROUND(AVG(discount), 2) as avg_discount,
                ROUND(AVG(rating), 2) as avg_rating
            FROM tv_platform_latest_master
            WHERE sale_price > 0 AND original_cost > 0
            GROUP BY segment
            ORDER BY total_tvs DESC
        """)).fetchall()

        segment_stats = [dict(row._mapping) for row in segment_stats]

        return {
            "overall": overall_stats,
            "top_best_value_tvs": top_best_value_tvs,
            "brand_stats": brand_stats,
            "platform_stats": platform_stats,
            "segment_stats": segment_stats
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




# ======================================================
# PRICE HISTORY DATA ENDPOINT (JSON for React Charts)
# ======================================================

@app.get("/products/{model_id}/price-history-data")
def get_price_history_data(
    model_id: str,
    days: int = Query(30, ge=7, le=365),
    db: Session = Depends(get_db)
):
    """Return price history data from tvs_unified table"""
    try:
        # First, get the date range from the actual data (not today's date)
        date_range_result = db.execute(text("""
            SELECT 
                MIN(DATE(scraped_at)) as min_date,
                MAX(DATE(scraped_at)) as max_date
            FROM tvs_unified
            WHERE model_id = :model_id AND sale_price > 0
        """), {"model_id": model_id}).fetchone()
        
        if not date_range_result or not date_range_result.max_date:
            # No data found
            product_info = db.execute(text("""
                SELECT full_name, brand, image_url 
                FROM tv_platform_latest_master 
                WHERE model_id = :model_id 
                LIMIT 1
            """), {"model_id": model_id}).fetchone()
            
            return {
                "model_id": model_id,
                "product_name": product_info.full_name if product_info else None,
                "brand": product_info.brand if product_info else None,
                "image_url": product_info.image_url if product_info else None,
                "platforms_data": {},
                "best_price_data": [],
                "stats": None,
                "best_price_stats": None,
                "platforms": [],
                "message": "No price history found"
            }
        
        # Use the latest date in database as end_date
        end_date = date_range_result.max_date
        start_date = end_date - timedelta(days=days)
        
        # Query all price history data
        result = db.execute(text("""
            SELECT 
                platform,
                DATE(scraped_at) as price_date,
                MIN(sale_price) as price,
                MIN(full_name) as full_name,
                MIN(brand) as brand,
                MIN(image_url) as image_url
            FROM tvs_unified
            WHERE model_id = :model_id
                AND sale_price > 0
                AND DATE(scraped_at) >= :start_date
                AND DATE(scraped_at) <= :end_date
            GROUP BY platform, DATE(scraped_at)
            ORDER BY price_date ASC
        """), {
            "model_id": model_id, 
            "start_date": start_date,
            "end_date": end_date
        })
        
        rows = result.fetchall()
        
        if not rows:
            return {
                "model_id": model_id,
                "product_name": None,
                "platforms_data": {},
                "best_price_data": [],
                "stats": None,
                "best_price_stats": None,
                "platforms": [],
                "message": f"No price history found for last {days} days"
            }
        
        # Group by platform
        platforms_data = {}
        product_name = None
        brand = None
        image_url = None
        all_prices = []
        
        for row in rows:
            if not product_name:
                product_name = row.full_name
                brand = row.brand
                image_url = row.image_url
            
            platform = row.platform
            price = float(row.price)
            date_str = str(row.price_date)
            all_prices.append({"price": price, "date": date_str, "platform": platform})
            
            if platform not in platforms_data:
                platforms_data[platform] = {
                    "data": [],
                    "stats": {"highest": 0, "lowest": float('inf'), "current": 0}
                }
            
            platforms_data[platform]["data"].append({
                "date": date_str,
                "price": price
            })
            
            # Update platform stats
            if price > platforms_data[platform]["stats"]["highest"]:
                platforms_data[platform]["stats"]["highest"] = price
            if price < platforms_data[platform]["stats"]["lowest"]:
                platforms_data[platform]["stats"]["lowest"] = price
            platforms_data[platform]["stats"]["current"] = price
        
        # Calculate best price data (lowest across all platforms for each date)
        dates_prices = {}
        for item in all_prices:
            date_str = item["date"]
            if date_str not in dates_prices:
                dates_prices[date_str] = []
            dates_prices[date_str].append({"price": item["price"], "platform": item["platform"]})
        
        best_price_data = []
        for date_str in sorted(dates_prices.keys()):
            prices = dates_prices[date_str]
            best = min(prices, key=lambda x: x["price"])
            best_price_data.append({
                "date": date_str,
                "price": best["price"],
                "platform": best["platform"]
            })
        
        # Overall stats
        all_price_values = [p["price"] for p in all_prices]
        overall_stats = {
            "highest": max(all_price_values) if all_price_values else 0,
            "lowest": min(all_price_values) if all_price_values else 0,
            "average": round(sum(all_price_values) / len(all_price_values)) if all_price_values else 0,
            "current": all_price_values[-1] if all_price_values else 0
        }
        
        # Best price stats
        best_prices = [p["price"] for p in best_price_data]
        best_price_stats = {
            "highest": max(best_prices) if best_prices else 0,
            "lowest": min(best_prices) if best_prices else 0,
            "current": best_prices[-1] if best_prices else 0,
            "current_platform": best_price_data[-1]["platform"] if best_price_data else None
        }
        
        # Get platform count from tv_platform_latest_master for accurate count
        platform_count_result = db.execute(text("""
            SELECT COUNT(DISTINCT platform) as count
            FROM tv_platform_latest_master
            WHERE model_id = :model_id AND sale_price > 0
        """), {"model_id": model_id}).fetchone()
        
        return {
            "model_id": model_id,
            "product_name": product_name,
            "brand": brand,
            "image_url": image_url,
            "platforms_data": platforms_data,
            "best_price_data": best_price_data,
            "stats": overall_stats,
            "best_price_stats": best_price_stats,
            "platforms": list(platforms_data.keys()),
            "total_platforms_available": platform_count_result.count if platform_count_result else len(platforms_data),
            "date_range": {
                "start": str(start_date),
                "end": str(end_date)
            }
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
        
        
# ======================================================
# DEBUG ENDPOINTS
# ======================================================

@app.get("/debug/price-history/{model_id}")
def debug_price_history(model_id: str, db: Session = Depends(get_db)):
    """Debug endpoint to check price history data"""
    try:
        unified_data = db.execute(text("""
            SELECT 
                platform,
                DATE(scraped_at) as price_date,
                sale_price,
                scraped_at
            FROM tvs_unified
            WHERE model_id = :model_id
            ORDER BY scraped_at DESC
        """), {"model_id": model_id}).fetchall()
        
        latest_data = db.execute(text("""
            SELECT 
                platform,
                sale_price,
                scraped_at
            FROM tv_platform_latest_master
            WHERE model_id = :model_id
        """), {"model_id": model_id}).fetchall()
        
        unified_platforms = list(set([row.platform for row in unified_data]))
        latest_platforms = list(set([row.platform for row in latest_data]))
        
        return {
            "model_id": model_id,
            "tvs_unified": {
                "total_records": len(unified_data),
                "platforms": unified_platforms,
                "data": [
                    {
                        "platform": row.platform,
                        "price_date": str(row.price_date),
                        "sale_price": float(row.sale_price),
                        "scraped_at": str(row.scraped_at)
                    } for row in unified_data[:20]
                ]
            },
            "tv_platform_latest_master": {
                "total_records": len(latest_data),
                "platforms": latest_platforms,
                "data": [
                    {
                        "platform": row.platform,
                        "sale_price": float(row.sale_price),
                        "scraped_at": str(row.scraped_at)
                    } for row in latest_data
                ]
            }
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


@app.get("/debug/tvs-unified/{model_id}")
def debug_tvs_unified(model_id: str, db: Session = Depends(get_db)):
    """Debug endpoint to check tvs_unified data"""
    try:
        total = db.execute(text("""
            SELECT COUNT(*) as total FROM tvs_unified WHERE model_id = :model_id
        """), {"model_id": model_id}).fetchone()
        
        dates = db.execute(text("""
            SELECT 
                MIN(DATE(scraped_at)) as earliest,
                MAX(DATE(scraped_at)) as latest
            FROM tvs_unified WHERE model_id = :model_id
        """), {"model_id": model_id}).fetchone()
        
        platforms = db.execute(text("""
            SELECT DISTINCT platform, COUNT(*) as count
            FROM tvs_unified WHERE model_id = :model_id
            GROUP BY platform
        """), {"model_id": model_id}).fetchall()
        
        samples = db.execute(text("""
            SELECT platform, sale_price, scraped_at
            FROM tvs_unified WHERE model_id = :model_id
            ORDER BY scraped_at DESC LIMIT 10
        """), {"model_id": model_id}).fetchall()
        
        return {
            "model_id": model_id,
            "total_records": total.total if total else 0,
            "date_range": {
                "earliest": str(dates.earliest) if dates and dates.earliest else None,
                "latest": str(dates.latest) if dates and dates.latest else None
            },
            "platforms": [{"platform": p.platform, "count": p.count} for p in platforms],
            "sample_data": [
                {"platform": s.platform, "sale_price": float(s.sale_price), "scraped_at": str(s.scraped_at)} 
                for s in samples
            ]
        }
    except Exception as e:
        return {"error": str(e)}        

# ======================================================
# ADMIN ENDPOINTS
# ======================================================

@app.get("/admin/stats")
async def admin_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Admin-only statistics"""
    total_users = db.query(User).count()
    active_sessions = db.query(RefreshSession).filter(
        RefreshSession.is_revoked == False
    ).count()

    return {
        "total_users": total_users,
        "active_sessions": active_sessions,
        "admin": current_user.name
    }


# ======================================================
# RUN SERVER
# ======================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
