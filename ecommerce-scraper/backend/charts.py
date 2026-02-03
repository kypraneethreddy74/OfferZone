"""
Price History Charts - Clean Style like PriceHistory.in
"""

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import pandas as pd
import numpy as np
from io import BytesIO
import base64
from datetime import datetime, date, timedelta
from typing import List, Dict

# Set clean style
plt.rcParams['figure.figsize'] = (14, 6)
plt.rcParams['font.size'] = 10
plt.rcParams['axes.facecolor'] = 'white'
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.alpha'] = 0.3

# Platform colors
PLATFORM_COLORS = {
    'Amazon': '#FF9900',
    'amazon': '#FF9900',
    'Flipkart': '#2874F0',
    'flipkart': '#2874F0',
    'CROMA': '#00B0B9',
    'Croma': '#00B0B9',
    'Reliance': '#E31837',
    'reliance': '#E31837',
    'Vijay': '#8B5CF6',
    'vijay': '#8B5CF6',
    'Tatacliq': '#E91E63',
    'tatacliq': '#E91E63'
}


def get_platform_color(platform: str) -> str:
    """Get color for a platform"""
    return PLATFORM_COLORS.get(platform, '#2874F0')


def fig_to_base64(fig) -> str:
    """Convert matplotlib figure to base64 string"""
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close(fig)
    return f"data:image/png;base64,{image_base64}"


def create_empty_chart(message: str) -> str:
    """Create a placeholder chart with a message"""
    fig, ax = plt.subplots(figsize=(14, 6))
    
    ax.set_facecolor('#f8f9fa')
    ax.text(0.5, 0.5, message, ha='center', va='center', 
            fontsize=16, color='#666', transform=ax.transAxes)
    ax.text(0.5, 0.65, '📊', ha='center', va='center', 
            fontsize=48, transform=ax.transAxes)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    return fig_to_base64(fig)


def create_price_history_matplotlib(
    data: List[Dict],
    model_id: str,
    product_name: str
) -> str:
    """
    Create price history chart like PriceHistory.in style
    - Area fill under price line
    - Red dashed line for highest price
    - Green dashed line for lowest price
    """
    if not data:
        return create_empty_chart("No price history data available")
    
    df = pd.DataFrame(data)
    df['price_date'] = pd.to_datetime(df['price_date'])
    
    # Create separate charts for each platform
    platforms = df['platform'].unique()
    
    if len(platforms) == 1:
        # Single platform - create the exact style shown
        return create_single_platform_chart(df, platforms[0], product_name)
    else:
        # Multiple platforms - create combined view
        return create_multi_platform_chart(df, product_name)


def create_single_platform_chart(df: pd.DataFrame, platform: str, product_name: str) -> str:
    """Create single platform price history chart - PriceHistory.in style"""
    
    fig, ax = plt.subplots(figsize=(14, 6))
    
    # Sort by date
    df = df.sort_values('price_date')
    
    dates = df['price_date']
    prices = df['min_price']
    
    # Calculate statistics
    highest_price = prices.max()
    lowest_price = prices.min()
    avg_price = prices.mean()
    
    # Main price line with area fill
    ax.fill_between(dates, prices, alpha=0.4, color='#87CEEB', step='post')
    ax.step(dates, prices, where='post', linewidth=2, color='#1E90FF', label=f'{platform} Price')
    
    # Highest price line (red dashed)
    ax.axhline(y=highest_price, color='#FF6B6B', linestyle='--', 
               linewidth=1.5, label=f'Highest: ₹{highest_price:,.0f}')
    
    # Lowest price line (green dashed)
    ax.axhline(y=lowest_price, color='#4CAF50', linestyle='--', 
               linewidth=1.5, label=f'Lowest: ₹{lowest_price:,.0f}')
    
    # Average price line (orange dashed) - optional
    ax.axhline(y=avg_price, color='#FFA500', linestyle=':', 
               linewidth=1, alpha=0.7, label=f'Average: ₹{avg_price:,.0f}')
    
    # Title
    ax.set_title(f'{platform} Price History', fontsize=14, fontweight='bold', loc='left')
    
    # Y-axis formatting with Rupee symbol
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'₹{x:,.0f}'))
    
    # X-axis date formatting
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b %Y'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.xticks(rotation=45, ha='right')
    
    # Grid
    ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
    ax.set_axisbelow(True)
    
    # Legend
    ax.legend(loc='upper right', framealpha=0.9, fontsize=9)
    
    # Set Y-axis limits with padding
    y_min = lowest_price * 0.9
    y_max = highest_price * 1.1
    ax.set_ylim(y_min, y_max)
    
    plt.tight_layout()
    
    return fig_to_base64(fig)


def create_multi_platform_chart(df: pd.DataFrame, product_name: str) -> str:
    """Create multi-platform price history chart"""
    
    platforms = df['platform'].unique()
    n_platforms = len(platforms)
    
    # Create subplots for each platform
    fig, axes = plt.subplots(n_platforms, 1, figsize=(14, 5 * n_platforms), sharex=True)
    
    if n_platforms == 1:
        axes = [axes]
    
    for idx, platform in enumerate(platforms):
        ax = axes[idx]
        platform_df = df[df['platform'] == platform].sort_values('price_date')
        
        dates = platform_df['price_date']
        prices = platform_df['min_price']
        
        # Statistics
        highest_price = prices.max()
        lowest_price = prices.min()
        avg_price = prices.mean()
        
        color = get_platform_color(platform)
        
        # Area fill and step line
        ax.fill_between(dates, prices, alpha=0.3, color=color, step='post')
        ax.step(dates, prices, where='post', linewidth=2, color=color)
        
        # Reference lines
        ax.axhline(y=highest_price, color='#FF6B6B', linestyle='--', linewidth=1.5)
        ax.axhline(y=lowest_price, color='#4CAF50', linestyle='--', linewidth=1.5)
        
        # Title and formatting
        ax.set_title(f'{platform} Price History', fontsize=12, fontweight='bold', loc='left')
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'₹{x:,.0f}'))
        ax.grid(True, alpha=0.3)
        
        # Add price annotations
        ax.text(0.02, 0.95, f'Highest: ₹{highest_price:,.0f}', transform=ax.transAxes,
                fontsize=9, color='#FF6B6B', verticalalignment='top')
        ax.text(0.02, 0.05, f'Lowest: ₹{lowest_price:,.0f}', transform=ax.transAxes,
                fontsize=9, color='#4CAF50', verticalalignment='bottom')
        
        # Y limits
        ax.set_ylim(lowest_price * 0.9, highest_price * 1.1)
    
    # X-axis formatting on last subplot
    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter('%d %b %Y'))
    plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    
    return fig_to_base64(fig)


def create_price_comparison_seaborn(
    data: List[Dict],
    model_id: str,
    product_name: str
) -> str:
    """Create platform price comparison chart"""
    if not data:
        return create_empty_chart("No data available for comparison")
    
    df = pd.DataFrame(data)
    platforms = df['platform'].unique()
    
    fig, ax = plt.subplots(figsize=(14, 6))
    
    # Get current/latest prices for each platform
    latest_prices = df.groupby('platform')['min_price'].last().sort_values()
    
    colors = [get_platform_color(p) for p in latest_prices.index]
    
    bars = ax.barh(latest_prices.index, latest_prices.values, color=colors, edgecolor='white', height=0.6)
    
    # Add value labels
    for bar, price in zip(bars, latest_prices.values):
        ax.text(bar.get_width() + 1000, bar.get_y() + bar.get_height()/2,
                f'₹{price:,.0f}', va='center', fontsize=11, fontweight='bold')
    
    # Best price highlight
    best_platform = latest_prices.idxmin()
    best_price = latest_prices.min()
    
    ax.set_title(f'Price Comparison Across Platforms\nBest Price: ₹{best_price:,.0f} on {best_platform}',
                 fontsize=12, fontweight='bold', loc='left')
    ax.set_xlabel('Price (₹)', fontsize=10)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'₹{x:,.0f}'))
    
    # Add savings annotation
    if len(latest_prices) > 1:
        max_price = latest_prices.max()
        savings = max_price - best_price
        savings_pct = (savings / max_price) * 100
        ax.text(0.98, 0.02, f'💰 Save up to ₹{savings:,.0f} ({savings_pct:.1f}%)',
                transform=ax.transAxes, ha='right', va='bottom',
                fontsize=10, color='#4CAF50', fontweight='bold')
    
    ax.grid(True, axis='x', alpha=0.3)
    plt.tight_layout()
    
    return fig_to_base64(fig)


def create_platform_heatmap(
    data: List[Dict],
    model_id: str,
    product_name: str
) -> str:
    """Create price heatmap across platforms and dates"""
    if not data:
        return create_empty_chart("No data available for heatmap")
    
    df = pd.DataFrame(data)
    df['price_date'] = pd.to_datetime(df['price_date'])
    df['date_str'] = df['price_date'].dt.strftime('%d %b')
    
    try:
        pivot_df = df.pivot_table(
            values='min_price',
            index='platform',
            columns='date_str',
            aggfunc='min'
        )
    except Exception:
        return create_empty_chart("Not enough data for heatmap")
    
    if pivot_df.empty or pivot_df.shape[1] < 2:
        return create_empty_chart("Not enough date range for heatmap")
    
    fig, ax = plt.subplots(figsize=(16, max(4, len(pivot_df) * 1.2)))
    
    # Custom colormap - green (low) to red (high)
    cmap = sns.diverging_palette(130, 10, as_cmap=True)
    
    sns.heatmap(
        pivot_df,
        annot=True,
        fmt=',.0f',
        cmap='RdYlGn_r',
        ax=ax,
        cbar_kws={'label': 'Price (₹)', 'shrink': 0.8},
        linewidths=1,
        linecolor='white',
        annot_kws={'size': 8, 'weight': 'bold'}
    )
    
    ax.set_title('Price Heatmap: Lower prices in Green, Higher in Red',
                 fontsize=12, fontweight='bold', pad=15)
    ax.set_xlabel('Date', fontsize=10)
    ax.set_ylabel('Platform', fontsize=10)
    plt.xticks(rotation=45, ha='right', fontsize=9)
    plt.yticks(fontsize=10)
    
    plt.tight_layout()
    
    return fig_to_base64(fig)


def create_best_price_tracker_matplotlib(
    data: List[Dict],
    model_id: str,
    product_name: str
) -> str:
    """Create best price tracker chart - shows which platform had best price each day"""
    if not data:
        return create_empty_chart("No best price data available")
    
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    fig, axes = plt.subplots(2, 1, figsize=(14, 10), gridspec_kw={'height_ratios': [2, 1]})
    
    # ===== Chart 1: Best Price Over Time =====
    ax1 = axes[0]
    
    dates = df['date']
    best_prices = df['best_price']
    
    # Statistics
    highest = best_prices.max()
    lowest = best_prices.min()
    current = best_prices.iloc[-1]
    
    # Area fill with step
    ax1.fill_between(dates, best_prices, alpha=0.4, color='#87CEEB', step='post')
    ax1.step(dates, best_prices, where='post', linewidth=2.5, color='#1E90FF')
    
    # Reference lines
    ax1.axhline(y=highest, color='#FF6B6B', linestyle='--', linewidth=1.5,
                label=f'Highest: ₹{highest:,.0f}')
    ax1.axhline(y=lowest, color='#4CAF50', linestyle='--', linewidth=1.5,
                label=f'Lowest: ₹{lowest:,.0f}')
    
    # Mark best platform on each point
    for _, row in df.iterrows():
        ax1.scatter(row['date'], row['best_price'], s=80,
                   color=get_platform_color(row['best_platform']),
                   zorder=5, edgecolors='white', linewidths=1.5)
    
    ax1.set_title('Best Price Tracker (Lowest Price Across All Platforms)',
                  fontsize=14, fontweight='bold', loc='left')
    ax1.set_ylabel('Best Price (₹)', fontsize=11)
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'₹{x:,.0f}'))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
    ax1.legend(loc='upper right', fontsize=9)
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(lowest * 0.9, highest * 1.1)
    
    # Current price annotation
    ax1.annotate(f'Current: ₹{current:,.0f}',
                xy=(dates.iloc[-1], current),
                xytext=(10, 10), textcoords='offset points',
                fontsize=10, fontweight='bold', color='#1E90FF',
                arrowprops=dict(arrowstyle='->', color='#1E90FF'))
    
    # ===== Chart 2: Platform Wins =====
    ax2 = axes[1]
    
    win_counts = df['best_platform'].value_counts()
    colors = [get_platform_color(p) for p in win_counts.index]
    
    bars = ax2.bar(win_counts.index, win_counts.values, color=colors,
                   edgecolor='white', linewidth=2)
    
    for bar, count in zip(bars, win_counts.values):
        percentage = (count / len(df)) * 100
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                f'{count} days\n({percentage:.0f}%)',
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    ax2.set_title('Days with Best Price by Platform', fontsize=12, fontweight='bold')
    ax2.set_xlabel('Platform', fontsize=10)
    ax2.set_ylabel('Number of Days', fontsize=10)
    ax2.set_ylim(0, max(win_counts.values) * 1.4)
    ax2.grid(True, axis='y', alpha=0.3)
    
    plt.tight_layout()
    
    return fig_to_base64(fig)


def create_all_platforms_combined(
    data: List[Dict],
    model_id: str,
    product_name: str
) -> str:
    """Create a combined chart showing all platforms on same axes"""
    if not data:
        return create_empty_chart("No price history data available")
    
    df = pd.DataFrame(data)
    df['price_date'] = pd.to_datetime(df['price_date'])
    
    fig, ax = plt.subplots(figsize=(14, 7))
    
    platforms = df['platform'].unique()
    
    for platform in platforms:
        platform_df = df[df['platform'] == platform].sort_values('price_date')
        color = get_platform_color(platform)
        
        # Step plot for each platform
        ax.step(platform_df['price_date'], platform_df['min_price'],
               where='post', linewidth=2, color=color, label=platform)
        ax.fill_between(platform_df['price_date'], platform_df['min_price'],
                       alpha=0.15, color=color, step='post')
    
    # Overall stats
    overall_high = df['min_price'].max()
    overall_low = df['min_price'].min()
    
    ax.axhline(y=overall_high, color='#FF6B6B', linestyle='--', linewidth=1,
               alpha=0.7, label=f'Highest: ₹{overall_high:,.0f}')
    ax.axhline(y=overall_low, color='#4CAF50', linestyle='--', linewidth=1,
               alpha=0.7, label=f'Lowest: ₹{overall_low:,.0f}')
    
    title = product_name[:60] + "..." if len(product_name) > 60 else product_name
    ax.set_title(f'Price History: {title}', fontsize=14, fontweight='bold', loc='left')
    ax.set_xlabel('Date', fontsize=11)
    ax.set_ylabel('Price (₹)', fontsize=11)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'₹{x:,.0f}'))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b %Y'))
    plt.xticks(rotation=45, ha='right')
    ax.legend(loc='upper right', fontsize=9, ncol=2)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(overall_low * 0.9, overall_high * 1.1)
    
    plt.tight_layout()
    
    return fig_to_base64(fig)