#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Expense Manager
Tests all endpoints sequentially with realistic data
"""

import requests
import json
import uuid
from datetime import datetime, timedelta
import sys

# Backend URL from frontend/.env
BASE_URL = "https://budget-wizard-32.preview.emergentagent.com/api"

class ExpenseManagerTester:
    def __init__(self):
        self.session = requests.Session()
        self.created_categories = []
        self.created_expenses = []
        self.created_budgets = []
        self.test_results = {
            "health": False,
            "categories_crud": False,
            "expenses_crud": False,
            "budgets_crud": False,
            "dashboard": False,
            "analytics": False,
            "ai_insights": False
        }
        
    def log(self, message, level="INFO"):
        """Log test messages"""
        print(f"[{level}] {message}")
        
    def test_health_check(self):
        """Test 1: Health check endpoint"""
        self.log("=== Testing Health Check ===")
        try:
            response = self.session.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log("✅ Health check passed")
                    self.test_results["health"] = True
                    return True
                else:
                    self.log(f"❌ Health check failed - unexpected response: {data}", "ERROR")
            else:
                self.log(f"❌ Health check failed - status code: {response.status_code}", "ERROR")
        except Exception as e:
            self.log(f"❌ Health check failed - exception: {str(e)}", "ERROR")
        return False
        
    def test_categories_crud(self):
        """Test 2: Categories CRUD operations"""
        self.log("=== Testing Categories CRUD ===")
        
        # Test data - realistic categories
        test_categories = [
            {"name": "Food & Dining", "color": "#ff6b6b", "icon": "🍽️"},
            {"name": "Transportation", "color": "#4ecdc4", "icon": "🚗"},
            {"name": "Entertainment", "color": "#45b7d1", "icon": "🎬"},
            {"name": "Shopping", "color": "#f9ca24", "icon": "🛍️"}
        ]
        
        try:
            # 1. GET categories (should be empty initially)
            self.log("Testing GET /api/categories")
            response = self.session.get(f"{BASE_URL}/categories")
            if response.status_code != 200:
                self.log(f"❌ GET categories failed - status: {response.status_code}", "ERROR")
                return False
            initial_categories = response.json()
            self.log(f"Initial categories count: {len(initial_categories)}")
            
            # 2. POST categories (create test categories)
            self.log("Testing POST /api/categories")
            for cat_data in test_categories:
                response = self.session.post(f"{BASE_URL}/categories", json=cat_data)
                if response.status_code == 200:
                    created_cat = response.json()
                    self.created_categories.append(created_cat)
                    self.log(f"✅ Created category: {created_cat['name']} (ID: {created_cat['id']})")
                else:
                    self.log(f"❌ Failed to create category {cat_data['name']} - status: {response.status_code}", "ERROR")
                    return False
            
            # 3. GET categories again to verify creation
            self.log("Verifying categories were created")
            response = self.session.get(f"{BASE_URL}/categories")
            if response.status_code == 200:
                categories = response.json()
                if len(categories) >= len(test_categories):
                    self.log(f"✅ Categories created successfully - total: {len(categories)}")
                else:
                    self.log(f"❌ Category count mismatch - expected at least {len(test_categories)}, got {len(categories)}", "ERROR")
                    return False
            
            # 4. PUT category (update one)
            if self.created_categories:
                self.log("Testing PUT /api/categories/{id}")
                cat_to_update = self.created_categories[0]
                updated_data = cat_to_update.copy()
                updated_data["name"] = "Food & Restaurants (Updated)"
                updated_data["color"] = "#e74c3c"
                
                response = self.session.put(f"{BASE_URL}/categories/{cat_to_update['id']}", json=updated_data)
                if response.status_code == 200:
                    updated_cat = response.json()
                    self.log(f"✅ Updated category: {updated_cat['name']}")
                    # Update our local copy
                    self.created_categories[0] = updated_cat
                else:
                    self.log(f"❌ Failed to update category - status: {response.status_code}", "ERROR")
                    return False
            
            # 5. Try DELETE (should work for unused category)
            if len(self.created_categories) > 1:
                self.log("Testing DELETE /api/categories/{id} for unused category")
                cat_to_delete = self.created_categories[-1]  # Last category
                response = self.session.delete(f"{BASE_URL}/categories/{cat_to_delete['id']}")
                if response.status_code == 200:
                    self.log(f"✅ Deleted unused category: {cat_to_delete['name']}")
                    self.created_categories.remove(cat_to_delete)
                else:
                    self.log(f"❌ Failed to delete category - status: {response.status_code}", "ERROR")
                    return False
            
            self.test_results["categories_crud"] = True
            self.log("✅ Categories CRUD tests passed")
            return True
            
        except Exception as e:
            self.log(f"❌ Categories CRUD failed - exception: {str(e)}", "ERROR")
            return False
    
    def test_expenses_crud(self):
        """Test 3: Expenses CRUD operations"""
        self.log("=== Testing Expenses CRUD ===")
        
        if not self.created_categories:
            self.log("❌ No categories available for expense testing", "ERROR")
            return False
        
        # Test data - realistic expenses across different months
        base_date = datetime.now()
        test_expenses = [
            {
                "amount": 45.50,
                "category_id": self.created_categories[0]["id"],
                "description": "Lunch at Italian restaurant",
                "date": (base_date - timedelta(days=5)).strftime("%Y-%m-%d")
            },
            {
                "amount": 25.00,
                "category_id": self.created_categories[1]["id"] if len(self.created_categories) > 1 else self.created_categories[0]["id"],
                "description": "Gas station fill-up",
                "date": (base_date - timedelta(days=10)).strftime("%Y-%m-%d")
            },
            {
                "amount": 15.99,
                "category_id": self.created_categories[0]["id"],
                "description": "Coffee and pastry",
                "date": (base_date - timedelta(days=2)).strftime("%Y-%m-%d")
            },
            {
                "amount": 89.99,
                "category_id": self.created_categories[2]["id"] if len(self.created_categories) > 2 else self.created_categories[0]["id"],
                "description": "Movie tickets and snacks",
                "date": (base_date - timedelta(days=15)).strftime("%Y-%m-%d")
            },
            {
                "amount": 120.00,
                "category_id": self.created_categories[0]["id"],
                "description": "Grocery shopping",
                "date": (base_date - timedelta(days=30)).strftime("%Y-%m-%d")
            },
            {
                "amount": 67.50,
                "category_id": self.created_categories[1]["id"] if len(self.created_categories) > 1 else self.created_categories[0]["id"],
                "description": "Uber rides",
                "date": (base_date - timedelta(days=45)).strftime("%Y-%m-%d")
            }
        ]
        
        try:
            # 1. GET expenses (should be empty initially)
            self.log("Testing GET /api/expenses")
            response = self.session.get(f"{BASE_URL}/expenses")
            if response.status_code != 200:
                self.log(f"❌ GET expenses failed - status: {response.status_code}", "ERROR")
                return False
            initial_expenses = response.json()
            self.log(f"Initial expenses count: {len(initial_expenses)}")
            
            # 2. POST expenses (create test expenses)
            self.log("Testing POST /api/expenses")
            for exp_data in test_expenses:
                response = self.session.post(f"{BASE_URL}/expenses", json=exp_data)
                if response.status_code == 200:
                    created_exp = response.json()
                    self.created_expenses.append(created_exp)
                    self.log(f"✅ Created expense: ${created_exp['amount']} - {created_exp['description']}")
                else:
                    self.log(f"❌ Failed to create expense - status: {response.status_code}, response: {response.text}", "ERROR")
                    return False
            
            # 3. GET expenses again to verify creation
            self.log("Verifying expenses were created")
            response = self.session.get(f"{BASE_URL}/expenses")
            if response.status_code == 200:
                expenses = response.json()
                if len(expenses) >= len(test_expenses):
                    self.log(f"✅ Expenses created successfully - total: {len(expenses)}")
                else:
                    self.log(f"❌ Expense count mismatch - expected at least {len(test_expenses)}, got {len(expenses)}", "ERROR")
                    return False
            
            # 4. PUT expense (update one)
            if self.created_expenses:
                self.log("Testing PUT /api/expenses/{id}")
                exp_to_update = self.created_expenses[0]
                updated_data = exp_to_update.copy()
                updated_data["amount"] = 55.75
                updated_data["description"] = "Dinner at Italian restaurant (Updated)"
                
                response = self.session.put(f"{BASE_URL}/expenses/{exp_to_update['id']}", json=updated_data)
                if response.status_code == 200:
                    updated_exp = response.json()
                    self.log(f"✅ Updated expense: ${updated_exp['amount']} - {updated_exp['description']}")
                    self.created_expenses[0] = updated_exp
                else:
                    self.log(f"❌ Failed to update expense - status: {response.status_code}", "ERROR")
                    return False
            
            # 5. DELETE expense
            if self.created_expenses:
                self.log("Testing DELETE /api/expenses/{id}")
                exp_to_delete = self.created_expenses[-1]  # Last expense
                response = self.session.delete(f"{BASE_URL}/expenses/{exp_to_delete['id']}")
                if response.status_code == 200:
                    self.log(f"✅ Deleted expense: ${exp_to_delete['amount']} - {exp_to_delete['description']}")
                    self.created_expenses.remove(exp_to_delete)
                else:
                    self.log(f"❌ Failed to delete expense - status: {response.status_code}", "ERROR")
                    return False
            
            # 6. Test invalid category_id
            self.log("Testing expense creation with invalid category_id")
            invalid_expense = {
                "amount": 10.00,
                "category_id": str(uuid.uuid4()),  # Random UUID that doesn't exist
                "description": "Test invalid category",
                "date": datetime.now().strftime("%Y-%m-%d")
            }
            response = self.session.post(f"{BASE_URL}/expenses", json=invalid_expense)
            if response.status_code == 404:
                self.log("✅ Correctly rejected expense with invalid category_id")
            else:
                self.log(f"❌ Should have rejected invalid category_id - status: {response.status_code}", "ERROR")
                return False
            
            self.test_results["expenses_crud"] = True
            self.log("✅ Expenses CRUD tests passed")
            return True
            
        except Exception as e:
            self.log(f"❌ Expenses CRUD failed - exception: {str(e)}", "ERROR")
            return False
    
    def test_budgets_crud(self):
        """Test 4: Recurring Budgets CRUD operations (Updated Model)"""
        self.log("=== Testing Recurring Budgets CRUD ===")
        
        if not self.created_categories:
            self.log("❌ No categories available for budget testing", "ERROR")
            return False
        
        # Test data - recurring budgets (no month field, recurring=true by default)
        test_budgets = [
            {
                "category_id": self.created_categories[0]["id"],
                "amount": 500.00
                # No month field - should be recurring by default
            },
            {
                "category_id": self.created_categories[1]["id"] if len(self.created_categories) > 1 else self.created_categories[0]["id"],
                "amount": 200.00
            }
        ]
        
        try:
            # 1. GET budgets (should be empty initially)
            self.log("Testing GET /api/budgets")
            response = self.session.get(f"{BASE_URL}/budgets")
            if response.status_code != 200:
                self.log(f"❌ GET budgets failed - status: {response.status_code}", "ERROR")
                return False
            initial_budgets = response.json()
            self.log(f"Initial budgets count: {len(initial_budgets)}")
            
            # 2. POST budgets (create recurring budgets)
            self.log("Testing POST /api/budgets (recurring budgets)")
            for budget_data in test_budgets:
                response = self.session.post(f"{BASE_URL}/budgets", json=budget_data)
                if response.status_code == 200:
                    created_budget = response.json()
                    self.created_budgets.append(created_budget)
                    # Verify it's recurring by default
                    if created_budget.get("recurring", False):
                        self.log(f"✅ Created recurring budget: ₹{created_budget['amount']} (recurring: {created_budget['recurring']})")
                    else:
                        self.log(f"❌ Budget should be recurring by default", "ERROR")
                        return False
                else:
                    self.log(f"❌ Failed to create budget - status: {response.status_code}, response: {response.text}", "ERROR")
                    return False
            
            # 3. GET budgets again to verify creation
            self.log("Verifying recurring budgets were created")
            response = self.session.get(f"{BASE_URL}/budgets")
            if response.status_code == 200:
                budgets = response.json()
                if len(budgets) >= len(test_budgets):
                    self.log(f"✅ Recurring budgets created successfully - total: {len(budgets)}")
                    # Verify all are recurring
                    for budget in budgets:
                        if not budget.get("recurring", False):
                            self.log(f"❌ Budget {budget['id']} is not marked as recurring", "ERROR")
                            return False
                else:
                    self.log(f"❌ Budget count mismatch - expected at least {len(test_budgets)}, got {len(budgets)}", "ERROR")
                    return False
            
            # 4. PUT budget (update one)
            if self.created_budgets:
                self.log("Testing PUT /api/budgets/{id}")
                budget_to_update = self.created_budgets[0]
                updated_data = budget_to_update.copy()
                updated_data["amount"] = 550.00
                
                response = self.session.put(f"{BASE_URL}/budgets/{budget_to_update['id']}", json=updated_data)
                if response.status_code == 200:
                    updated_budget = response.json()
                    self.log(f"✅ Updated recurring budget: ₹{updated_budget['amount']} (recurring: {updated_budget.get('recurring', False)})")
                    self.created_budgets[0] = updated_budget
                else:
                    self.log(f"❌ Failed to update budget - status: {response.status_code}", "ERROR")
                    return False
            
            # 5. Test duplicate budget creation for same category (should fail)
            self.log("Testing duplicate budget creation for same category (should fail)")
            if self.created_budgets:
                duplicate_budget = {
                    "category_id": self.created_budgets[0]["category_id"],
                    "amount": 300.00
                    # No month field - should fail because one recurring budget per category
                }
                response = self.session.post(f"{BASE_URL}/budgets", json=duplicate_budget)
                if response.status_code == 400:
                    self.log("✅ Correctly rejected duplicate budget for same category")
                else:
                    self.log(f"❌ Should have rejected duplicate budget for same category - status: {response.status_code}", "ERROR")
                    return False
            
            # 6. Test invalid category_id
            self.log("Testing recurring budget creation with invalid category_id")
            invalid_budget = {
                "category_id": str(uuid.uuid4()),
                "amount": 100.00
                # No month field for recurring budget
            }
            response = self.session.post(f"{BASE_URL}/budgets", json=invalid_budget)
            if response.status_code == 404:
                self.log("✅ Correctly rejected budget with invalid category_id")
            else:
                self.log(f"❌ Should have rejected invalid category_id - status: {response.status_code}", "ERROR")
                return False
            
            self.test_results["budgets_crud"] = True
            self.log("✅ Recurring Budgets CRUD tests passed")
            return True
            
        except Exception as e:
            self.log(f"❌ Budgets CRUD failed - exception: {str(e)}", "ERROR")
            return False
    
    def test_dashboard(self):
        """Test 5: Dashboard endpoint for home page"""
        self.log("=== Testing Dashboard Endpoint ===")
        
        try:
            response = self.session.get(f"{BASE_URL}/dashboard")
            if response.status_code == 200:
                data = response.json()
                
                # Verify expected structure
                required_fields = [
                    "current_month", "current_month_expenses", "current_month_budget", 
                    "remaining_budget", "budget_utilization", "recent_transactions", 
                    "budget_status", "transaction_count"
                ]
                for field in required_fields:
                    if field not in data:
                        self.log(f"❌ Dashboard missing field: {field}", "ERROR")
                        return False
                
                self.log("✅ Dashboard structure valid")
                self.log(f"   - Current month: {data['current_month']}")
                self.log(f"   - Current month expenses: ₹{data['current_month_expenses']:.2f}")
                self.log(f"   - Current month budget: ₹{data['current_month_budget']:.2f}")
                self.log(f"   - Remaining budget: ₹{data['remaining_budget']:.2f}")
                self.log(f"   - Budget utilization: {data['budget_utilization']:.1f}%")
                self.log(f"   - Recent transactions: {len(data['recent_transactions'])}")
                self.log(f"   - Budget status categories: {len(data['budget_status'])}")
                self.log(f"   - Transaction count: {data['transaction_count']}")
                
                # Verify recent transactions structure
                if data['recent_transactions']:
                    transaction = data['recent_transactions'][0]
                    required_tx_fields = ["id", "amount", "description", "date", "category_name", "category_color", "category_icon"]
                    for field in required_tx_fields:
                        if field not in transaction:
                            self.log(f"❌ Recent transaction missing field: {field}", "ERROR")
                            return False
                    self.log("✅ Recent transactions structure valid")
                
                # Verify budget status structure
                if data['budget_status']:
                    budget_status = data['budget_status'][0]
                    required_budget_fields = ["category", "category_icon", "category_color", "budget", "spent", "remaining", "percentage"]
                    for field in required_budget_fields:
                        if field not in budget_status:
                            self.log(f"❌ Budget status missing field: {field}", "ERROR")
                            return False
                    self.log("✅ Budget status structure valid")
                
                # Verify data consistency
                if data['current_month_expenses'] >= 0 and data['current_month_budget'] >= 0:
                    expected_remaining = data['current_month_budget'] - data['current_month_expenses']
                    if abs(data['remaining_budget'] - expected_remaining) < 0.01:  # Allow for floating point precision
                        self.log("✅ Dashboard calculations are consistent")
                    else:
                        self.log(f"❌ Dashboard calculation mismatch - expected remaining: {expected_remaining}, got: {data['remaining_budget']}", "ERROR")
                        return False
                else:
                    self.log("❌ Dashboard data values are invalid", "ERROR")
                    return False
                
                self.test_results["dashboard"] = True
                self.log("✅ Dashboard tests passed")
                return True
            else:
                self.log(f"❌ Dashboard failed - status: {response.status_code}, response: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Dashboard failed - exception: {str(e)}", "ERROR")
            return False
    
    def test_analytics(self):
        """Test 6: Updated Analytics summary endpoint"""
        self.log("=== Testing Updated Analytics Summary ===")
        
        try:
            response = self.session.get(f"{BASE_URL}/analytics/summary")
            if response.status_code == 200:
                data = response.json()
                
                # Verify expected structure (updated fields)
                required_fields = [
                    "category_spending", "monthly_trends", "budget_comparison", 
                    "average_monthly_spending", "highest_spending_category", 
                    "total_categories", "total_transactions"
                ]
                for field in required_fields:
                    if field not in data:
                        self.log(f"❌ Analytics missing field: {field}", "ERROR")
                        return False
                
                self.log("✅ Updated Analytics summary structure valid")
                self.log(f"   - Average monthly spending: ₹{data['average_monthly_spending']:.2f}")
                self.log(f"   - Total categories: {data['total_categories']}")
                self.log(f"   - Total transactions: {data['total_transactions']}")
                self.log(f"   - Categories with spending: {len(data['category_spending'])}")
                self.log(f"   - Monthly trends: {len(data['monthly_trends'])} months")
                self.log(f"   - Budget comparisons (current month): {len(data['budget_comparison'])}")
                
                # Verify highest spending category structure
                if data['highest_spending_category']:
                    highest = data['highest_spending_category']
                    if "name" in highest and "amount" in highest:
                        self.log(f"   - Highest spending category: {highest['name']} (₹{highest['amount']:.2f})")
                        self.log("✅ Highest spending category structure valid")
                    else:
                        self.log("❌ Highest spending category missing required fields", "ERROR")
                        return False
                else:
                    self.log("   - No highest spending category (no data)")
                
                # Verify budget comparison is for current month only
                current_month = datetime.now().strftime("%Y-%m")
                self.log(f"   - Budget comparison should be for current month: {current_month}")
                
                # Verify data makes sense
                if (data['average_monthly_spending'] >= 0 and 
                    data['total_categories'] >= 0 and 
                    data['total_transactions'] >= 0):
                    self.log("✅ Updated Analytics data values are reasonable")
                else:
                    self.log("❌ Updated Analytics data values are invalid", "ERROR")
                    return False
                
                self.test_results["analytics"] = True
                self.log("✅ Updated Analytics tests passed")
                return True
            else:
                self.log(f"❌ Analytics failed - status: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Analytics failed - exception: {str(e)}", "ERROR")
            return False
    
    def test_ai_insights(self):
        """Test 7: Updated AI Insights endpoint with Rupees currency"""
        self.log("=== Testing Updated AI Insights ===")
        
        try:
            response = self.session.get(f"{BASE_URL}/insights")
            if response.status_code == 200:
                data = response.json()
                
                # Verify expected structure
                if "insights" not in data or "summary" not in data:
                    self.log("❌ AI insights missing required fields", "ERROR")
                    return False
                
                insights_text = data["insights"]
                summary = data["summary"]
                
                # Verify insights text is not empty
                if not insights_text or len(insights_text.strip()) == 0:
                    self.log("❌ AI insights text is empty", "ERROR")
                    return False
                
                # Verify summary structure (updated fields)
                expected_summary_fields = [
                    "total_expenses", "current_month_expenses", "current_month_budget",
                    "num_transactions", "categories", "budgets_set"
                ]
                for field in expected_summary_fields:
                    if field not in summary:
                        self.log(f"❌ AI insights summary missing field: {field}", "ERROR")
                        return False
                
                self.log("✅ Updated AI insights structure valid")
                self.log(f"   - Insights length: {len(insights_text)} characters")
                self.log(f"   - Total expenses: ₹{summary['total_expenses']:.2f}")
                self.log(f"   - Current month expenses: ₹{summary['current_month_expenses']:.2f}")
                self.log(f"   - Current month budget: ₹{summary['current_month_budget']:.2f}")
                self.log(f"   - Transactions: {summary['num_transactions']}")
                self.log(f"   - Categories: {summary['categories']}")
                self.log(f"   - Budgets set: {summary['budgets_set']}")
                
                # Check if insights contain Rupees currency symbol
                if "₹" in insights_text:
                    self.log("✅ AI insights contain Rupees currency (₹)")
                else:
                    self.log("⚠️ AI insights may not contain Rupees currency symbol", "WARNING")
                
                # Check if insights contain reasonable content
                if any(keyword in insights_text.lower() for keyword in ["spending", "budget", "expense", "category", "recommendation", "current month"]):
                    self.log("✅ AI insights contain relevant content")
                else:
                    self.log("⚠️ AI insights may not contain expected content", "WARNING")
                
                # Verify current month data is included
                current_month = datetime.now().strftime("%Y-%m")
                if current_month in insights_text or "current month" in insights_text.lower():
                    self.log("✅ AI insights include current month context")
                else:
                    self.log("⚠️ AI insights may not include current month context", "WARNING")
                
                self.test_results["ai_insights"] = True
                self.log("✅ Updated AI Insights tests passed")
                return True
            else:
                self.log(f"❌ AI Insights failed - status: {response.status_code}, response: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ AI Insights failed - exception: {str(e)}", "ERROR")
            return False
    
    def run_all_tests(self):
        """Run all tests sequentially"""
        self.log("🚀 Starting Expense Manager Backend API Tests")
        self.log(f"Base URL: {BASE_URL}")
        
        tests = [
            ("Health Check", self.test_health_check),
            ("Categories CRUD", self.test_categories_crud),
            ("Expenses CRUD", self.test_expenses_crud),
            ("Recurring Budgets CRUD", self.test_budgets_crud),
            ("Dashboard Endpoint", self.test_dashboard),
            ("Updated Analytics Summary", self.test_analytics),
            ("Updated AI Insights", self.test_ai_insights)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            self.log(f"\n{'='*50}")
            if test_func():
                passed += 1
            else:
                self.log(f"❌ {test_name} FAILED", "ERROR")
        
        # Final summary
        self.log(f"\n{'='*50}")
        self.log("🏁 TEST SUMMARY")
        self.log(f"{'='*50}")
        
        for test_name, result in self.test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            self.log(f"{test_name.replace('_', ' ').title()}: {status}")
        
        self.log(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            self.log("🎉 ALL TESTS PASSED! Backend API is working correctly.")
            return True
        else:
            self.log(f"⚠️ {total - passed} tests failed. Please check the errors above.")
            return False

def main():
    """Main test execution"""
    tester = ExpenseManagerTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()