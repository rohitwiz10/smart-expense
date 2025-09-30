from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from typing import List, Optional
import os
from dotenv import load_dotenv
import uuid
from datetime import datetime, timezone
import httpx
from dateutil.relativedelta import relativedelta

load_dotenv()

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB setup
MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME', 'expense-manager')
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY')

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# Collections
expenses_collection = db.expenses
categories_collection = db.categories
budgets_collection = db.budgets

# Pydantic Models
class Category(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    color: str = "#3b82f6"
    icon: str = "💰"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    class Config:
        populate_by_name = True

class Expense(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    amount: float
    category_id: str
    description: str
    date: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    class Config:
        populate_by_name = True

class Budget(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    category_id: str
    amount: float
    recurring: bool = True  # Budgets are recurring by default
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    class Config:
        populate_by_name = True

# Health Check
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "expense-manager"}

# ==================== CATEGORIES ENDPOINTS ====================

@app.get("/api/categories", response_model=List[Category])
async def get_categories():
    categories = await categories_collection.find().to_list(length=None)
    return [Category(**cat) for cat in categories]

@app.post("/api/categories", response_model=Category)
async def create_category(category: Category):
    category_dict = category.dict()
    await categories_collection.insert_one(category_dict)
    return category

@app.put("/api/categories/{category_id}", response_model=Category)
async def update_category(category_id: str, category: Category):
    category_dict = category.dict()
    result = await categories_collection.update_one(
        {"id": category_id},
        {"$set": category_dict}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@app.delete("/api/categories/{category_id}")
async def delete_category(category_id: str):
    # Check if category has expenses
    expense_count = await expenses_collection.count_documents({"category_id": category_id})
    if expense_count > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete category with {expense_count} expenses"
        )
    
    result = await categories_collection.delete_one({"id": category_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Also delete associated budgets
    await budgets_collection.delete_many({"category_id": category_id})
    return {"message": "Category deleted successfully"}

# ==================== EXPENSES ENDPOINTS ====================

@app.get("/api/expenses", response_model=List[Expense])
async def get_expenses():
    expenses = await expenses_collection.find().sort("date", -1).to_list(length=None)
    return [Expense(**exp) for exp in expenses]

@app.post("/api/expenses", response_model=Expense)
async def create_expense(expense: Expense):
    # Verify category exists
    category = await categories_collection.find_one({"id": expense.category_id})
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    expense_dict = expense.dict()
    await expenses_collection.insert_one(expense_dict)
    return expense

@app.put("/api/expenses/{expense_id}", response_model=Expense)
async def update_expense(expense_id: str, expense: Expense):
    # Verify category exists
    category = await categories_collection.find_one({"id": expense.category_id})
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    expense_dict = expense.dict()
    result = await expenses_collection.update_one(
        {"id": expense_id},
        {"$set": expense_dict}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense

@app.delete("/api/expenses/{expense_id}")
async def delete_expense(expense_id: str):
    result = await expenses_collection.delete_one({"id": expense_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"message": "Expense deleted successfully"}

# ==================== BUDGETS ENDPOINTS ====================

@app.get("/api/budgets", response_model=List[Budget])
async def get_budgets():
    budgets = await budgets_collection.find().to_list(length=None)
    return [Budget(**budget) for budget in budgets]

@app.post("/api/budgets", response_model=Budget)
async def create_budget(budget: Budget):
    # Verify category exists
    category = await categories_collection.find_one({"id": budget.category_id})
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check if budget already exists for this category (only one recurring budget per category)
    existing = await budgets_collection.find_one({"category_id": budget.category_id})
    if existing:
        raise HTTPException(
            status_code=400, 
            detail="Budget already exists for this category. Update the existing one instead."
        )
    
    budget_dict = budget.dict()
    await budgets_collection.insert_one(budget_dict)
    return budget

@app.put("/api/budgets/{budget_id}", response_model=Budget)
async def update_budget(budget_id: str, budget: Budget):
    # Verify category exists
    category = await categories_collection.find_one({"id": budget.category_id})
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    budget_dict = budget.dict()
    result = await budgets_collection.update_one(
        {"id": budget_id},
        {"$set": budget_dict}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Budget not found")
    return budget

@app.delete("/api/budgets/{budget_id}")
async def delete_budget(budget_id: str):
    result = await budgets_collection.delete_one({"id": budget_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Budget not found")
    return {"message": "Budget deleted successfully"}

# ==================== DASHBOARD ENDPOINT ====================

@app.get("/api/dashboard")
async def get_dashboard():
    # Get current month
    now = datetime.now(timezone.utc)
    current_month = now.strftime("%Y-%m")
    
    # Get all data
    expenses = await expenses_collection.find().to_list(length=None)
    categories = await categories_collection.find().to_list(length=None)
    budgets = await budgets_collection.find().to_list(length=None)
    
    # Create category map
    category_map = {cat["id"]: cat for cat in categories}
    
    # Current month expenses
    current_month_expenses = [
        exp for exp in expenses 
        if exp["date"].startswith(current_month)
    ]
    
    current_month_total = sum(exp["amount"] for exp in current_month_expenses)
    
    # Current month budget (sum of all recurring budgets)
    current_month_budget = sum(b["amount"] for b in budgets if b.get("recurring", True))
    
    # Recent 5 transactions
    sorted_expenses = sorted(expenses, key=lambda x: x["date"], reverse=True)[:5]
    recent_transactions = []
    for exp in sorted_expenses:
        cat = category_map.get(exp["category_id"], {})
        recent_transactions.append({
            "id": exp["id"],
            "amount": exp["amount"],
            "description": exp["description"],
            "date": exp["date"],
            "category_name": cat.get("name", "Unknown"),
            "category_color": cat.get("color", "#3b82f6"),
            "category_icon": cat.get("icon", "💰")
        })
    
    # Budget utilization by category for current month
    budget_status = []
    for budget in budgets:
        if budget.get("recurring", True):
            cat_id = budget["category_id"]
            actual = sum(
                exp["amount"] for exp in current_month_expenses
                if exp["category_id"] == cat_id
            )
            
            if cat_id in category_map:
                budget_status.append({
                    "category": category_map[cat_id]["name"],
                    "category_icon": category_map[cat_id].get("icon", "💰"),
                    "category_color": category_map[cat_id].get("color", "#3b82f6"),
                    "budget": budget["amount"],
                    "spent": actual,
                    "remaining": budget["amount"] - actual,
                    "percentage": (actual / budget["amount"] * 100) if budget["amount"] > 0 else 0
                })
    
    return {
        "current_month": current_month,
        "current_month_expenses": current_month_total,
        "current_month_budget": current_month_budget,
        "remaining_budget": current_month_budget - current_month_total,
        "budget_utilization": (current_month_total / current_month_budget * 100) if current_month_budget > 0 else 0,
        "recent_transactions": recent_transactions,
        "budget_status": budget_status,
        "transaction_count": len(current_month_expenses)
    }

# ==================== ANALYTICS ENDPOINTS ====================

@app.get("/api/analytics/summary")
async def get_analytics_summary():
    # Get all data
    expenses = await expenses_collection.find().to_list(length=None)
    categories = await categories_collection.find().to_list(length=None)
    budgets = await budgets_collection.find().to_list(length=None)
    
    if not expenses:
        return {
            "category_spending": [],
            "monthly_trends": [],
            "budget_comparison": [],
            "average_monthly_spending": 0,
            "highest_spending_category": None,
            "total_categories": len(categories),
            "total_transactions": 0
        }
    
    # Create category map
    category_map = {cat["id"]: cat for cat in categories}
    
    # Spending by category
    spending_by_category = {}
    for expense in expenses:
        cat_id = expense["category_id"]
        if cat_id in spending_by_category:
            spending_by_category[cat_id] += expense["amount"]
        else:
            spending_by_category[cat_id] = expense["amount"]
    
    # Format spending by category with names
    category_spending = []
    for cat_id, amount in spending_by_category.items():
        if cat_id in category_map:
            category_spending.append({
                "category": category_map[cat_id]["name"],
                "amount": amount,
                "color": category_map[cat_id].get("color", "#3b82f6")
            })
    
    # Find highest spending category
    highest_spending_category = None
    if category_spending:
        highest = max(category_spending, key=lambda x: x["amount"])
        highest_spending_category = {
            "name": highest["category"],
            "amount": highest["amount"]
        }
    
    # Monthly trends (last 6 months)
    monthly_spending = {}
    for expense in expenses:
        month = expense["date"][:7]  # YYYY-MM
        if month in monthly_spending:
            monthly_spending[month] += expense["amount"]
        else:
            monthly_spending[month] = expense["amount"]
    
    trends = sorted(
        [{"month": month, "amount": amount} for month, amount in monthly_spending.items()],
        key=lambda x: x["month"]
    )[-6:]
    
    # Calculate average monthly spending
    average_monthly_spending = sum(t["amount"] for t in trends) / len(trends) if trends else 0
    
    # Budget vs Actuals for current month
    now = datetime.now(timezone.utc)
    current_month = now.strftime("%Y-%m")
    
    budget_comparison = []
    for budget in budgets:
        if budget.get("recurring", True):
            cat_id = budget["category_id"]
            
            # Calculate actual spending for this category in current month
            actual = sum(
                exp["amount"] for exp in expenses 
                if exp["category_id"] == cat_id and exp["date"].startswith(current_month)
            )
            
            if cat_id in category_map:
                budget_comparison.append({
                    "category": category_map[cat_id]["name"],
                    "budget": budget["amount"],
                    "actual": actual,
                    "color": category_map[cat_id].get("color", "#3b82f6")
                })
    
    return {
        "category_spending": category_spending,
        "monthly_trends": trends,
        "budget_comparison": budget_comparison,
        "average_monthly_spending": average_monthly_spending,
        "highest_spending_category": highest_spending_category,
        "total_categories": len(categories),
        "total_transactions": len(expenses)
    }

# ==================== AI INSIGHTS ENDPOINT ====================

@app.get("/api/insights")
async def get_ai_insights():
    try:
        # Get all data
        expenses = await expenses_collection.find().to_list(length=None)
        categories = await categories_collection.find().to_list(length=None)
        budgets = await budgets_collection.find().to_list(length=None)
        
        if not expenses:
            return {
                "insights": "No expenses found. Start adding expenses to get AI-powered insights!",
                "summary": {}
            }
        
        # Create category map
        category_map = {cat["id"]: cat["name"] for cat in categories}
        
        # Prepare data summary for AI
        total_expenses = sum(exp["amount"] for exp in expenses)
        
        spending_by_category = {}
        for expense in expenses:
            cat_name = category_map.get(expense["category_id"], "Unknown")
            if cat_name in spending_by_category:
                spending_by_category[cat_name] += expense["amount"]
            else:
                spending_by_category[cat_name] = expense["amount"]
        
        # Current month data
        now = datetime.now(timezone.utc)
        current_month = now.strftime("%Y-%m")
        current_month_expenses = [
            exp for exp in expenses if exp["date"].startswith(current_month)
        ]
        current_month_total = sum(exp["amount"] for exp in current_month_expenses)
        
        # Budget data
        total_budget = sum(b["amount"] for b in budgets if b.get("recurring", True))
        budget_info = []
        for budget in budgets:
            if budget.get("recurring", True):
                cat_name = category_map.get(budget["category_id"], "Unknown")
                actual = sum(
                    exp["amount"] for exp in current_month_expenses 
                    if exp["category_id"] == budget["category_id"]
                )
                budget_info.append({
                    "category": cat_name,
                    "budget": budget["amount"],
                    "actual": actual
                })
        
        # Create prompt for AI
        prompt = f"""Analyze this expense data (amounts in Indian Rupees ₹) and provide clear, actionable insights:

Current Month ({current_month}):
- Expenses: ₹{current_month_total:.2f}
- Budget: ₹{total_budget:.2f}
- Transactions: {len(current_month_expenses)}

Total Expenses (All Time): ₹{total_expenses:.2f}
Total Transactions: {len(expenses)}

Spending by Category:
{chr(10).join([f'- {cat}: ₹{amt:.2f}' for cat, amt in spending_by_category.items()])}

Recurring Monthly Budgets:
{chr(10).join([f"- {b['category']}: Budget ₹{b['budget']:.2f}, Current Month Spent ₹{b['actual']:.2f}" for b in budget_info]) if budget_info else 'No budgets set'}

Provide:
1. Key spending patterns and insights
2. Budget adherence analysis for current month
3. Specific recommendations for reducing expenses
4. Areas where spending can be optimized
5. Financial health assessment

Keep the response concise, actionable, and focused on the current month."""
        
        # Call OpenRouter API
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "x-ai/grok-4-fast:free",
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=500, 
                    detail=f"AI service error: {response.text}"
                )
            
            result = response.json()
            insights_text = result["choices"][0]["message"]["content"]
        
        return {
            "insights": insights_text,
            "summary": {
                "total_expenses": total_expenses,
                "current_month_expenses": current_month_total,
                "current_month_budget": total_budget,
                "num_transactions": len(expenses),
                "categories": len(spending_by_category),
                "budgets_set": len(budget_info)
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating insights: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
