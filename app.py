"""
app.py
Streamlit web application for the AI Business Intelligence Agent

HOW TO USE:
1. Make sure you've run database_setup.py and sample_data.py
2. Save this file as 'app.py' in your project folder
3. Run: streamlit run app.py
4. Open your browser and start asking business questions!
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from ai_agent import BusinessAIAgent
import sqlite3
from datetime import datetime, timedelta
import json

# Page configuration
st.set_page_config(
    page_title="📊 AI Business Intelligence Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .query-box {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def get_database_stats():
    """Get basic database statistics for the dashboard"""
    try:
        conn = sqlite3.connect('inventory_sales.db')
        
        stats = {}
        
        # Total products
        stats['total_products'] = pd.read_sql("SELECT COUNT(*) as count FROM products WHERE is_active = 1", conn)['count'][0]
        
        # Total customers
        stats['total_customers'] = pd.read_sql("SELECT COUNT(*) as count FROM customers", conn)['count'][0]
        
        # Total orders
        stats['total_orders'] = pd.read_sql("SELECT COUNT(*) as count FROM sales_orders", conn)['count'][0]
        
        # Total revenue
        stats['total_revenue'] = pd.read_sql("SELECT COALESCE(SUM(total_amount), 0) as revenue FROM sales_orders WHERE order_status != 'Cancelled'", conn)['revenue'][0]
        
        # Pending orders
        stats['pending_orders'] = pd.read_sql("SELECT COUNT(*) as count FROM sales_orders WHERE order_status = 'Pending'", conn)['count'][0]
        
        # Low stock products
        stats['low_stock'] = pd.read_sql("SELECT COUNT(*) as count FROM inventory WHERE quantity_on_hand <= reorder_level", conn)['low_stock'][0]
        
        conn.close()
        return stats
    except Exception as e:
        st.error(f"Error getting database stats: {e}")
        return {}

@st.cache_data
def get_sales_chart_data():
    """Get data for sales charts"""
    try:
        conn = sqlite3.connect('inventory_sales.db')
        
        # Monthly sales
        monthly_sales = pd.read_sql("""
            SELECT 
                strftime('%Y-%m', order_date) as month,
                SUM(total_amount) as revenue,
                COUNT(*) as orders
            FROM sales_orders 
            WHERE order_status != 'Cancelled'
            GROUP BY strftime('%Y-%m', order_date)
            ORDER BY month DESC
            LIMIT 12
        """, conn)
        
        # Top products by revenue
        top_products = pd.read_sql("""
            SELECT 
                p.product_name,
                SUM(soi.line_total) as revenue,
                SUM(soi.quantity) as quantity_sold
            FROM sales_order_items soi
            JOIN products p ON soi.product_id = p.product_id
            JOIN sales_orders so ON soi.order_id = so.order_id
            WHERE so.order_status != 'Cancelled'
            GROUP BY p.product_id, p.product_name
            ORDER BY revenue DESC
            LIMIT 10
        """, conn)
        
        # Sales by category
        category_sales = pd.read_sql("""
            SELECT 
                c.category_name,
                SUM(soi.line_total) as revenue
            FROM sales_order_items soi
            JOIN products p ON soi.product_id = p.product_id
            JOIN categories c ON p.category_id = c.category_id
            JOIN sales_orders so ON soi.order_id = so.order_id
            WHERE so.order_status != 'Cancelled'
            GROUP BY c.category_id, c.category_name
            ORDER BY revenue DESC
        """, conn)
        
        conn.close()
        return monthly_sales, top_products, category_sales
    except Exception as e:
        st.error(f"Error getting chart data: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

def initialize_agent():
    """Initialize the AI agent"""
    if 'agent' not in st.session_state:
        try:
            with st.spinner("🤖 Initializing AI Agent..."):
                st.session_state.agent = BusinessAIAgent()
            st.success("✅ AI Agent ready!")
        except Exception as e:
            st.error(f"❌ Failed to initialize AI Agent: {e}")
            return None
    return st.session_state.agent

def display_query_result(result):
    """Display the result of a query in a nice format"""
    if result['success']:
        # Success message
        st.markdown('<div class="success-box">✅ Query executed successfully!</div>', unsafe_allow_html=True)
        
        # Show SQL query in expandable section
        with st.expander("🔍 View Generated SQL Query"):
            st.code(result['sql_query'], language='sql')
        
        # Show analysis
        st.markdown("### 🧠 AI Analysis")
        st.markdown(result['analysis'])
        
        # Show data if available
        if result['results']:
            st.markdown(f"### 📊 Data ({result['record_count']} records)")
            
            # Convert to DataFrame for better display
            df = pd.DataFrame(result['results'])
            
            # Display as table
            st.dataframe(df, use_container_width=True)
            
            # If numerical data, try to create a simple chart
            if len(df.columns) >= 2:
                numeric_columns = df.select_dtypes(include=['int64', 'float64']).columns
                if len(numeric_columns) > 0:
                    try:
                        # Simple bar chart for small datasets
                        if len(df) <= 20 and len(numeric_columns) >= 1:
                            y_col = numeric_columns[0]
                            x_col = [col for col in df.columns if col != y_col][0]
                            
                            fig = px.bar(df.head(10), x=x_col, y=y_col, 
                                       title=f"{y_col} by {x_col}")
                            st.plotly_chart(fig, use_container_width=True)
                    except Exception as e:
                        pass  # Chart creation is optional
        
    else:
        # Error message
        st.markdown(f'<div class="error-box">❌ Query failed: {result["error"]}</div>', unsafe_allow_html=True)

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<h1 class="main-header">🤖 AI Business Intelligence Agent</h1>', unsafe_allow_html=True)
    st.markdown("Ask any business question about your inventory and sales data in natural language!")
    
    # Initialize AI Agent
    agent = initialize_agent()
    if not agent:
        st.stop()
    
    # Sidebar
    st.sidebar.markdown("## 📋 Quick Actions")
    
    # Database stats in sidebar
    with st.sidebar:
        st.markdown("### 📊 Database Overview")
        stats = get_database_stats()
        
        if stats:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Products", f"{stats.get('total_products', 0):,}")
                st.metric("Orders", f"{stats.get('total_orders', 0):,}")
                st.metric("Low Stock", f"{stats.get('low_stock', 0):,}")
            
            with col2:
                st.metric("Customers", f"{stats.get('total_customers', 0):,}")
                st.metric("Revenue", f"₦{stats.get('total_revenue', 0):,.2f}")
                st.metric("Pending", f"{stats.get('pending_orders', 0):,}")
    
    # Sample questions in sidebar
    st.sidebar.markdown("### 💡 Sample Questions")
    sample_questions = agent.get_sample_questions()
    
    for i, question in enumerate(sample_questions[:5]):
        if st.sidebar.button(f"📌 {question[:30]}...", key=f"sample_{i}"):
            st.session_state.current_question = question
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 💬 Ask Your Business Question")
        
        # Question input
        default_question = st.session_state.get('current_question', '')
        question = st.text_area(
            "Type your question here:",
            value=default_question,
            height=100,
            placeholder="e.g., What are our top 5 best-selling products this month?"
        )
        
        # Query button
        if st.button("🚀 Get Answer", type="primary"):
            if question.strip():
                with st.spinner("🤔 Thinking..."):
                    result = agent.answer_question(question)
                    display_query_result(result)
            else:
                st.warning("Please enter a question!")
        
        # Clear current question from session state after use
        if 'current_question' in st.session_state:
            del st.session_state.current_question
    
    with col2:
        st.markdown("### 🎯 Quick Insights")
        
        # Get chart data
        monthly_sales, top_products, category_sales = get_sales_chart_data()
        
        # Mini revenue trend chart
        if not monthly_sales.empty:
            fig_mini = px.line(monthly_sales, x='month', y='revenue', 
                             title='Revenue Trend (Last 12 Months)')
            fig_mini.update_layout(height=250)
            st.plotly_chart(fig_mini, use_container_width=True)
        
        # Top categories pie chart
        if not category_sales.empty:
            fig_pie = px.pie(category_sales, values='revenue', names='category_name',
                           title='Sales by Category')
            fig_pie.update_layout(height=300)
            st.plotly_chart(fig_pie, use_container_width=True)
    
    # Dashboard section
    st.markdown("---")
    st.markdown("## 📈 Business Dashboard")
    
    # Charts in tabs
    tab1, tab2, tab3 = st.tabs(["📊 Sales Overview", "🏆 Top Products", "📦 Inventory Status"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            if not monthly_sales.empty:
                fig_revenue = px.bar(monthly_sales, x='month', y='revenue',
                                   title='Monthly Revenue')
                st.plotly_chart(fig_revenue, use_container_width=True)
        
        with col2:
            if not monthly_sales.empty:
                fig_orders = px.line(monthly_sales, x='month', y='orders',
                                   title='Monthly Order Count')
                st.plotly_chart(fig_orders, use_container_width=True)
    
    with tab2:
        if not top_products.empty:
            fig_products = px.bar(top_products.head(10), 
                                x='revenue', y='product_name',
                                orientation='h',
                                title='Top 10 Products by Revenue')
            fig_products.update_layout(height=500)
            st.plotly_chart(fig_products, use_container_width=True)
            
            # Show data table
            st.markdown("### 📋 Top Products Data")
            st.dataframe(top_products, use_container_width=True)
    
    with tab3:
        try:
            # Inventory status
            conn = sqlite3.connect('inventory_sales.db')
            inventory_status = pd.read_sql("""
                SELECT 
                    p.product_name,
                    w.warehouse_name,
                    i.quantity_on_hand,
                    i.reorder_level,
                    CASE 
                        WHEN i.quantity_on_hand <= i.reorder_level THEN 'Low Stock'
                        WHEN i.quantity_on_hand <= i.reorder_level * 2 THEN 'Medium Stock'
                        ELSE 'Good Stock'
                    END as stock_status
                FROM inventory i
                JOIN products p ON i.product_id = p.product_id
                JOIN warehouses w ON i.warehouse_id = w.warehouse_id
                ORDER BY i.quantity_on_hand ASC
                LIMIT 20
            """, conn)
            conn.close()
            
            if not inventory_status.empty:
                # Color code by stock status
                fig_inventory = px.bar(inventory_status, 
                                     x='product_name', y='quantity_on_hand',
                                     color='stock_status',
                                     title='Current Inventory Levels (Bottom 20 Products)')
                fig_inventory.update_xaxes(tickangle=45)
                st.plotly_chart(fig_inventory, use_container_width=True)
                
                st.markdown("### 📋 Inventory Details")
                st.dataframe(inventory_status, use_container_width=True)
        except Exception as e:
            st.error(f"Error loading inventory data: {e}")
    
    # Footer
    st.markdown("---")
    st.markdown("### 🛠️ How It Works")
    st.markdown("""
    1. **Ask Questions**: Type your business question in natural language
    2. **AI Processing**: The AI converts your question to SQL and queries the database
    3. **Get Insights**: Receive detailed analysis and actionable recommendations
    4. **Visualize**: See your data in charts and tables
    """)
    
    # Technical info in expander
    with st.expander("🔧 Technical Details"):
        st.markdown("""
        **Technology Stack:**
        - **Database**: SQLite with normalized inventory & sales schema
        - **AI Model**: Llama 3 via Groq API for natural language processing
        - **Backend**: Python with LangChain for AI orchestration
        - **Frontend**: Streamlit for interactive web interface
        - **Visualization**: Plotly for charts and graphs
        
        **Database Tables:**
        - Products, Categories, Suppliers
        - Inventory, Warehouses
        - Customers, Sales Orders, Order Items
        - Inventory Movements
        """)

if __name__ == "__main__":
    main()