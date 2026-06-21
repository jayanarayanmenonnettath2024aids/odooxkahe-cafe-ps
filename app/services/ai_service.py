import math
from datetime import datetime, timedelta, timezone
from sqlalchemy import func, select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from collections import Counter

from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.inventory import InventoryItem
from app.models.feedback import Feedback
from app.models.table import Table

class AIService:
    @staticmethod
    async def get_demand_forecast(session: AsyncSession):
        # Deterministic logic: Calculate averages based on OrderItem history
        # Since this is a demo, we will use a static but realistic formula
        query = select(Product.name, func.sum(OrderItem.quantity).label("total_sold")).join(
            OrderItem, OrderItem.product_id == Product.id
        ).group_by(Product.name).order_by(desc("total_sold")).limit(4)
        
        result = await session.execute(query)
        rows = result.fetchall()
        
        forecast = []
        for name, total_sold in rows:
            weekly_avg = int(total_sold / 7) if total_sold > 7 else int(total_sold)
            # Add some slight variation for "tomorrow" forecast
            forecast_tomorrow = weekly_avg + int(weekly_avg * 0.15)
            
            forecast.append({
                "product": name,
                "today_sales": int(total_sold / 2),
                "weekly_average": weekly_avg,
                "forecast_tomorrow": forecast_tomorrow,
                "confidence": 85 + (total_sold % 15)  # deterministic confidence between 85 and 99
            })
            
        return forecast

    @staticmethod
    async def get_inventory_alerts(session: AsyncSession):
        # Forecast based on mock consumption rate
        query = select(InventoryItem)
        result = await session.execute(query)
        items = result.scalars().all()
        
        alerts = []
        for item in items:
            # Deterministic pseudo-usage
            current_stock = float(item.current_stock)
            avg_daily = current_stock / 4.0 if current_stock > 0 else 1.0
            if item.name == "Coffee Beans":
                avg_daily = 5.0
            elif item.name == "Milk":
                avg_daily = 4.0
            elif item.name == "Chocolate Syrup":
                avg_daily = 2.0
                
            days_remaining = current_stock / avg_daily if avg_daily > 0 else 99
            
            alert_level = "HEALTHY"
            if days_remaining <= 2:
                alert_level = "CRITICAL"
            elif days_remaining <= 5:
                alert_level = "WARNING"
                
            alerts.append({
                "item": item.name,
                "stock": float(current_stock),
                "daily_usage": float(avg_daily),
                "days_remaining": round(days_remaining, 1),
                "alert": alert_level
            })
            
        # Sort so critical comes first
        alerts.sort(key=lambda x: x["days_remaining"])
        return alerts

    @staticmethod
    async def get_menu_recommendations(session: AsyncSession):
        # Deterministic recommendations based on simple static associations for demo
        recommendations = {
            "selected_product": "Burger",
            "recommended_products": [
                "French Fries",
                "Cold Coffee",
                "Brownie"
            ]
        }
        return recommendations

    @staticmethod
    async def get_feedback_analysis(session: AsyncSession):
        query = select(Feedback)
        result = await session.execute(query)
        feedbacks = result.scalars().all()
        
        total = len(feedbacks)
        if total == 0:
            return {"positive": 0, "neutral": 0, "negative": 0, "top_positive": [], "top_negative": []}
            
        positive = len([f for f in feedbacks if f.rating >= 4])
        negative = len([f for f in feedbacks if f.rating <= 2])
        neutral = total - positive - negative
        
        return {
            "positive": int((positive / total) * 100),
            "neutral": int((neutral / total) * 100),
            "negative": int((negative / total) * 100),
            "top_positive": ["Coffee", "Fast Service", "Ambience"],
            "top_negative": ["Waiting Time"]
        }

    @staticmethod
    async def get_table_recommendation(guests: int, session: AsyncSession):
        # Find the smallest valid table
        query = select(Table).where(Table.seat_count >= guests).order_by(Table.seat_count)
        result = await session.execute(query)
        table = result.scalars().first()
        
        if table:
            efficiency = int((guests / table.seat_count) * 100)
            return {
                "party_size": guests,
                "recommended_table": f"Table {table.table_number}",
                "efficiency": efficiency
            }
        return {
            "party_size": guests,
            "recommended_table": "No suitable table available",
            "efficiency": 0
        }

    @staticmethod
    async def get_peak_hours(session: AsyncSession):
        # Returns static deterministic peak hours
        return [
            {"name": "Lunch Rush", "time": "12 PM - 2 PM", "expected_customers": 45},
            {"name": "Dinner Rush", "time": "7 PM - 9 PM", "expected_customers": 65}
        ]
