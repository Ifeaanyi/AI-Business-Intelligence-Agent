"""
ai_agent.py - FIXED VERSION
AI Agent that converts natural language questions into SQL queries and provides business insights.

INSTRUCTIONS:
1. DELETE your current ai_agent.py file
2. SAVE THIS ENTIRE CODE as ai_agent.py
3. Run: streamlit run app.py
"""

import os
import sqlite3
import pandas as pd
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from typing import Dict, List, Tuple, Optional
import json
import re

# Load environment variables
load_dotenv()

class BusinessAIAgent:
    """
    AI Agent for answering business questions by querying the inventory & sales database
    """
    
    def __init__(self):
        """Initialize the AI agent"""
        self.db_path = "inventory_sales.db"
        self.llm = self._initialize_llm()
        self.db_schema = self._get_database_schema()
        
    def _initialize_llm(self) -> ChatGroq:
        """Initialize the Groq LLM"""
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        return ChatGroq(
            model="llama3-8b-8192",
            groq_api_key=groq_api_key,
            temperature=0.1,  # Low temperature for consistent SQL generation
            max_tokens=1500
        )
    
    def _get_database_schema(self) -> str:
        """Get database schema information for the AI to understand table structure"""
        schema_info = """
DATABASE SCHEMA INFORMATION:

TABLES AND RELATIONSHIPS:

1. categories
   - category_id (PRIMARY KEY)
   - category_name (e.g., Electronics, Clothing, etc.)
   - description

2. suppliers  
   - supplier_id (PRIMARY KEY)
   - supplier_name, contact_person, email, phone
   - address, city, country

3. products
   - product_id (PRIMARY KEY)
   - product_name, product_code
   - category_id (FOREIGN KEY -> categories)
   - supplier_id (FOREIGN KEY -> suppliers)  
   - unit_price, cost_price
   - weight, dimensions, is_active

4. warehouses
   - warehouse_id (PRIMARY KEY)
   - warehouse_name, location, capacity
   - manager_name, phone

5. inventory
   - product_id, warehouse_id (FOREIGN KEYS)
   - quantity_on_hand, quantity_reserved
   - reorder_level, max_stock_level

6. customers
   - customer_id (PRIMARY KEY)
   - customer_name, customer_type (Individual/Business)
   - email, phone, address, city, country
   - credit_limit

7. sales_orders
   - order_id (PRIMARY KEY)
   - order_number, customer_id, warehouse_id
   - order_date, required_date, shipped_date
   - order_status (Pending, Processing, Shipped, Delivered, Cancelled)
   - payment_status (Pending, Paid, Partial, Refunded)
   - subtotal, tax_amount, shipping_cost, total_amount

8. sales_order_items
   - order_id (FOREIGN KEY -> sales_orders)
   - product_id (FOREIGN KEY -> products)
   - quantity, unit_price, discount_percentage, line_total

9. inventory_movements
   - product_id, warehouse_id
   - movement_type (IN, OUT, TRANSFER, ADJUSTMENT)
   - quantity, movement_date, reference_type

COMMON BUSINESS QUERIES:
- Revenue analysis: Use sales_orders and sales_order_items
- Inventory levels: Use inventory table
- Product performance: Join products with sales_order_items
- Customer analysis: Use customers and sales_orders
- Warehouse operations: Use warehouses, inventory, sales_orders
"""
        return schema_info
    
    def _connect_db(self) -> sqlite3.Connection:
        """Connect to the database"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _get_predefined_query(self, question: str) -> str:
        """Get predefined query for common business questions"""
        question_lower = question.lower()
        
        # Common queries for reliability
        if "best seller" in question_lower and ("month" in question_lower or "monthly" in question_lower):
            return """
            SELECT 
                strftime('%Y-%m', so.order_date) AS month,
                p.product_name,
                SUM(soi.quantity) AS total_quantity,
                SUM(soi.line_total) AS total_revenue,
                COUNT(DISTINCT so.order_id) AS order_count
            FROM sales_orders so
            JOIN sales_order_items soi ON so.order_id = soi.order_id
            JOIN products p ON soi.product_id = p.product_id
            WHERE so.order_status != 'Cancelled'
            GROUP BY strftime('%Y-%m', so.order_date), p.product_id, p.product_name
            ORDER BY month DESC, total_revenue DESC
            """
        
        elif "top" in question_lower and "product" in question_lower and "revenue" in question_lower:
            return """
            SELECT 
                p.product_name,
                SUM(soi.line_total) AS total_revenue,
                SUM(soi.quantity) AS total_quantity,
                COUNT(DISTINCT so.order_id) AS order_count
            FROM sales_order_items soi
            JOIN products p ON soi.product_id = p.product_id
            JOIN sales_orders so ON soi.order_id = so.order_id
            WHERE so.order_status != 'Cancelled'
            GROUP BY p.product_id, p.product_name
            ORDER BY total_revenue DESC
            LIMIT 10
            """
        
        elif "sales by month" in question_lower or "monthly sales" in question_lower:
            return """
            SELECT 
                strftime('%Y-%m', order_date) AS month,
                COUNT(*) AS order_count,
                SUM(total_amount) AS total_revenue,
                AVG(total_amount) AS avg_order_value
            FROM sales_orders
            WHERE order_status != 'Cancelled'
            GROUP BY strftime('%Y-%m', order_date)
            ORDER BY month DESC
            LIMIT 12
            """
        
        elif "low stock" in question_lower or "reorder" in question_lower:
            return """
            SELECT 
                p.product_name,
                w.warehouse_name,
                i.quantity_on_hand,
                i.reorder_level,
                i.max_stock_level
            FROM inventory i
            JOIN products p ON i.product_id = p.product_id
            JOIN warehouses w ON i.warehouse_id = w.warehouse_id
            WHERE i.quantity_on_hand <= i.reorder_level
            ORDER BY i.quantity_on_hand ASC
            """
        
        return None
    
    def _generate_sql_query(self, question: str) -> str:
        """Generate SQL query from natural language question"""
        
        # First try predefined queries for common questions
        predefined = self._get_predefined_query(question)
        if predefined:
            return predefined.strip()
        
        prompt = f"""
You are a SQL expert for a business inventory and sales database. 
Convert the following business question into a SQL query.

{self.db_schema}

CRITICAL RULES:
1. Return ONLY the SQL query - NO explanations, NO comments, NO extra text
2. Generate ONLY valid SQLite SQL queries
3. Use proper JOINs when accessing related tables
4. Include appropriate WHERE clauses for filtering
5. Use aggregate functions (SUM, COUNT, AVG) when needed
6. Format dates properly for SQLite using strftime()
7. Always include column aliases for clarity
8. Limit results to reasonable numbers (use LIMIT if needed)
9. Start directly with SELECT, not with "Here is" or any explanation

QUESTION: {question}

SQL:
"""
        
        try:
            response = self.llm.invoke(prompt)
            sql_query = response.content.strip()
            
            # More aggressive cleanup of the response
            sql_query = re.sub(r'```sql\n?', '', sql_query)
            sql_query = re.sub(r'```\n?', '', sql_query)
            
            # Remove common prefixes that the AI might add
            prefixes_to_remove = [
                "Here is the SQL query:",
                "Here's the SQL query:",
                "SQL Query:",
                "The SQL query is:",
                "Query:",
                "SQL:",
                "Here is",
                "Here's"
            ]
            
            for prefix in prefixes_to_remove:
                if sql_query.lower().startswith(prefix.lower()):
                    sql_query = sql_query[len(prefix):].strip()
            
            # Remove any remaining explanation text before SELECT
            lines = sql_query.split('\n')
            sql_lines = []
            found_select = False
            
            for line in lines:
                line = line.strip()
                if line.upper().startswith('SELECT') or found_select:
                    found_select = True
                    sql_lines.append(line)
                elif not found_select and any(keyword in line.upper() for keyword in ['WITH', 'CREATE', 'INSERT', 'UPDATE', 'DELETE']):
                    found_select = True
                    sql_lines.append(line)
            
            if sql_lines:
                sql_query = '\n'.join(sql_lines)
            
            # Final cleanup
            sql_query = sql_query.strip()
            
            # Validate that it starts with a SQL command
            if not any(sql_query.upper().startswith(cmd) for cmd in ['SELECT', 'WITH', 'CREATE', 'INSERT', 'UPDATE', 'DELETE']):
                raise Exception("Generated query doesn't start with a valid SQL command")
            
            return sql_query
            
        except Exception as e:
            raise Exception(f"Error generating SQL query: {e}")
    
    def _execute_query(self, sql_query: str) -> Tuple[List[Dict], List[str]]:
        """Execute SQL query and return results"""
        try:
            conn = self._connect_db()
            cursor = conn.cursor()
            
            cursor.execute(sql_query)
            rows = cursor.fetchall()
            
            # Get column names
            columns = [description[0] for description in cursor.description] if cursor.description else []
            
            # Convert to list of dictionaries
            results = [dict(row) for row in rows]
            
            conn.close()
            return results, columns
            
        except sqlite3.Error as e:
            raise Exception(f"Database error: {e}")
        except Exception as e:
            raise Exception(f"Query execution error: {e}")
    
    def _interpret_results(self, question: str, results: List[Dict], columns: List[str]) -> str:
        """Generate natural language interpretation of query results"""
        
        if not results:
            return "No data found for your query."
        
        # Convert results to a readable format
        results_text = ""
        if len(results) <= 10:
            # Show all results if small dataset
            for i, row in enumerate(results, 1):
                results_text += f"\n{i}. " + " | ".join([f"{col}: {row[col]}" for col in columns])
        else:
            # Show summary for large datasets
            results_text = f"\nFound {len(results)} records. Here are the first 5:\n"
            for i, row in enumerate(results[:5], 1):
                results_text += f"{i}. " + " | ".join([f"{col}: {row[col]}" for col in columns]) + "\n"
        
        prompt = f"""
You are a business analyst. Interpret the following query results and provide insights.

ORIGINAL QUESTION: {question}

QUERY RESULTS ({len(results)} records):
{results_text}

INSTRUCTIONS:
1. Provide a clear, concise summary of the findings
2. Highlight key insights and trends
3. Use business language, not technical jargon
4. Include specific numbers and percentages where relevant
5. Suggest actionable recommendations if appropriate
6. Keep response under 200 words

BUSINESS ANALYSIS:
"""
        
        try:
            response = self.llm.invoke(prompt)
            return response.content.strip()
        except Exception as e:
            return f"Results found but interpretation failed: {e}\n\nRaw results: {results[:3]}..."
    
    def answer_question(self, question: str) -> Dict[str, any]:
        """
        Main method to answer business questions
        
        Returns:
            Dict containing query, results, analysis, and metadata
        """
        try:
            print(f"🤔 Processing question: {question}")
            
            # Step 1: Generate SQL query
            print("🔍 Generating SQL query...")
            sql_query = self._generate_sql_query(question)
            print(f"📝 Generated query: {sql_query[:100]}...")
            
            # Step 2: Execute query
            print("⚡ Executing query...")
            results, columns = self._execute_query(sql_query)
            print(f"📊 Found {len(results)} records")
            
            # Step 3: Interpret results
            print("🧠 Analyzing results...")
            analysis = self._interpret_results(question, results, columns)
            
            return {
                "success": True,
                "question": question,
                "sql_query": sql_query,
                "results": results,
                "columns": columns,
                "analysis": analysis,
                "record_count": len(results)
            }
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return {
                "success": False,
                "question": question,
                "error": str(e),
                "sql_query": None,
                "results": [],
                "columns": [],
                "analysis": f"Sorry, I couldn't process your question: {e}",
                "record_count": 0
            }
    
    def get_sample_questions(self) -> List[str]:
        """Return list of sample business questions for testing"""
        return [
            "What are the top 5 best-selling products by revenue?",
            "Show me total sales by month for this year",
            "Which customers have the highest total order value?",
            "What products are low in stock across all warehouses?",
            "How much revenue did we generate last month?",
            "Which product categories are most profitable?",
            "Show me pending orders that need attention",
            "What's our inventory turnover rate?",
            "Which warehouse has the highest sales volume?",
            "Show me customers with overdue payments"
        ]

def test_ai_agent():
    """Test function to try the AI agent with sample questions"""
    print("🤖 Testing Business AI Agent")
    print("=" * 50)
    
    # Initialize agent
    try:
        agent = BusinessAIAgent()
        print("✅ AI Agent initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize AI Agent: {e}")
        return
    
    # Test with sample questions
    sample_questions = [
        "What are our top 5 products by total sales revenue?",
        "How many orders do we have in each status?",
        "Which warehouse has the most inventory?"
    ]
    
    for i, question in enumerate(sample_questions, 1):
        print(f"\n🔸 Test {i}: {question}")
        print("-" * 40)
        
        result = agent.answer_question(question)
        
        if result["success"]:
            print(f"✅ Query executed successfully!")
            print(f"📊 Found {result['record_count']} records")
            print(f"🧠 Analysis: {result['analysis'][:200]}...")
        else:
            print(f"❌ Query failed: {result['error']}")
        
        print()

if __name__ == "__main__":
    # Test the agent when run directly
    test_ai_agent()