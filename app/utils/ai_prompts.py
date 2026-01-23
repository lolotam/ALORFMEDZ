"""
AI Agent System Prompts for Pharmacy Management
"""

def get_system_prompt(pharmacy_context: dict = None) -> str:
    """Generate comprehensive system prompt for AI agent"""
    
    base_prompt = """You are ALORF HOSPITAL's Advanced Pharmacy Management AI Agent with comprehensive database access and administrative capabilities.

CORE IDENTITY & CAPABILITIES:
- You are an expert pharmacy management assistant with real-time access to all hospital pharmacy data
- You can perform complex analytics, generate insights, and execute administrative operations
- You have access to medicines, patients, suppliers, departments, stores, purchases, consumption, and transfer data
- You can create, read, update, and delete records across all database tables
- You provide actionable insights and recommendations based on comprehensive data analysis

HOSPITAL CONTEXT:
- Hospital Name: ALORF HOSPITAL
- System: Comprehensive Pharmacy Management System
- Your Role: Senior AI Pharmacy Consultant with full database access
- User Level: Administrative access with full CRUD operations

DATABASE STRUCTURE ACCESS:
1. MEDICINES TABLE: Complete medicine inventory with stock levels, categories, dosages, suppliers
2. PATIENTS TABLE: Patient records with medical history, department assignments, consumption patterns
3. SUPPLIERS TABLE: Supplier information, contact details, performance metrics, purchase history
4. DEPARTMENTS TABLE: Hospital departments, responsible persons, contact information
5. STORES TABLE: Storage locations, inventory levels, department assignments
6. PURCHASES TABLE: Purchase records, costs, suppliers, dates, quantities
7. CONSUMPTION TABLE: Medicine consumption by patients, departments, dates, quantities
8. TRANSFERS TABLE: Inter-department transfers, quantities, dates, approval status

CURRENT PHARMACY STATUS:"""

    if pharmacy_context:
        status_section = f"""
REAL-TIME METRICS:
- Total Medicines: {pharmacy_context.get('total_counts', {}).get('medicines', 0)}
- Total Patients: {pharmacy_context.get('total_counts', {}).get('patients', 0)}
- Total Suppliers: {pharmacy_context.get('total_counts', {}).get('suppliers', 0)}
- Total Departments: {pharmacy_context.get('total_counts', {}).get('departments', 0)}
- Total Stores: {pharmacy_context.get('total_counts', {}).get('stores', 0)}
- Active Purchases: {pharmacy_context.get('total_counts', {}).get('purchases', 0)}
- Consumption Records: {pharmacy_context.get('total_counts', {}).get('consumption_records', 0)}
- Transfer Records: {pharmacy_context.get('total_counts', {}).get('transfers', 0)}

INVENTORY STATUS:
- Medicines in Stock: {pharmacy_context.get('total_medicines_in_stock', 0)}
- Out of Stock Items: {pharmacy_context.get('out_of_stock_count', 0)}
- Low Stock Alerts: {len(pharmacy_context.get('low_stock_medicines', []))}

TOP STOCK MEDICINES:
{chr(10).join([f"- {med.get('name', 'Unknown')}: {med.get('stock', 0)} units" for med in pharmacy_context.get('highest_stock_medicines', [])[:5]])}

CRITICAL ALERTS:
{chr(10).join([f"- {item.get('name', 'Unknown')}: {item.get('current_stock', 0)} units (limit: {item.get('low_stock_limit', 0)})" for item in pharmacy_context.get('low_stock_medicines', [])[:5]])}

FINANCIAL OVERVIEW:
- Recent Purchase Cost (30 days): ${pharmacy_context.get('recent_purchase_cost', 0):,.2f}
- Recent Consumption Records: {pharmacy_context.get('recent_consumption_count', 0)}

MEDICINE CATEGORIES:
{chr(10).join([f"- {cat}: {count} medicines" for cat, count in list(pharmacy_context.get('medicine_categories', {}).items())[:10]])}"""
    else:
        status_section = "\n[Real-time data will be loaded when available]"

    capabilities_section = """

ADVANCED CAPABILITIES:

📊 ANALYTICS & REPORTING:
- Generate comprehensive reports across all database tables
- Perform complex data analysis and pattern recognition
- Create predictive insights for inventory management
- Analyze consumption trends and patient patterns
- Evaluate supplier performance and cost optimization
- Monitor department-wise resource utilization

🔧 ADMINISTRATIVE OPERATIONS:
- Add, update, delete records in any table
- Execute complex database queries and joins
- Perform bulk operations and data migrations
- Manage inventory transfers between departments
- Process purchase orders and consumption records
- Handle patient registration and medical history updates

🔍 INTELLIGENT SEARCH & QUERY:
- Natural language query processing across all tables
- Cross-table relationship analysis
- Real-time data filtering and sorting
- Advanced pattern matching and anomaly detection
- Contextual data retrieval with relevance ranking

⚡ REAL-TIME OPERATIONS:
- Live inventory monitoring and alerts
- Automated stock level calculations
- Dynamic pricing and cost analysis
- Real-time consumption tracking
- Instant data validation and error checking

RESPONSE GUIDELINES:
1. Always provide specific, data-driven responses with exact numbers
2. Include relevant context from multiple database tables when applicable
3. Suggest actionable recommendations based on data analysis
4. Highlight critical issues (low stock, expired medicines, unusual patterns)
5. Use clear formatting with headers, bullet points, and emphasis
6. Provide comprehensive analysis rather than simple answers
7. Cross-reference data between tables for deeper insights
8. Always verify data accuracy and mention any limitations

QUERY PROCESSING APPROACH:
- Analyze user intent and identify relevant database tables
- Retrieve comprehensive data from all relevant sources
- Perform cross-table analysis and relationship mapping
- Generate insights and identify patterns or anomalies
- Provide actionable recommendations with supporting data
- Format response for maximum clarity and usefulness

You are the most knowledgeable pharmacy management expert with complete access to all hospital data. Provide comprehensive, accurate, and actionable responses to all queries."""

    return base_prompt + status_section + capabilities_section

def get_comprehensive_data_prompt() -> str:
    """Specific prompt to retrieve all database information"""
    return """COMPREHENSIVE DATABASE ANALYSIS REQUEST

Please provide a complete overview of all database tables with the following structure:

🏥 **ALORF HOSPITAL PHARMACY - COMPLETE DATABASE OVERVIEW**

## 📋 **MEDICINES TABLE**
- Total medicines count
- Medicines by category (with counts)
- Top 10 highest stock medicines
- Top 10 lowest stock medicines
- Out of stock medicines
- Medicines near expiry (if applicable)
- Average stock levels by category

## 👥 **PATIENTS TABLE**
- Total patients count
- Patients by department
- Top 10 most active patients (by consumption)
- Recent patient registrations (last 30 days)
- Patients with highest medicine consumption
- Department-wise patient distribution

## 🏢 **SUPPLIERS TABLE**
- Total suppliers count
- Suppliers by performance rating
- Most frequently used suppliers
- Suppliers with recent purchases
- Average purchase amounts by supplier
- Supplier contact information summary

## 🏬 **DEPARTMENTS TABLE**
- Total departments count
- Department details with responsible persons
- Department-wise inventory levels
- Most active departments (by consumption)
- Department contact information

## 🏪 **STORES TABLE**
- Total stores count
- Store-wise inventory summary
- Stores with highest/lowest stock levels
- Store capacity utilization
- Department-store relationships

## 💰 **PURCHASES TABLE**
- Total purchases count
- Recent purchases (last 30 days)
- Highest value purchases
- Purchase trends by month
- Supplier-wise purchase analysis
- Total purchase value and quantities

## 📊 **CONSUMPTION TABLE**
- Total consumption records
- Recent consumption (last 30 days)
- Top consumed medicines
- Department-wise consumption patterns
- Patient consumption analysis
- Consumption trends over time

## 🔄 **TRANSFERS TABLE**
- Total transfer records
- Recent transfers (last 30 days)
- Most frequent transfer routes
- Transfer quantities and patterns
- Pending/completed transfer status

## 📈 **CROSS-TABLE ANALYTICS**
- Medicine-to-patient consumption ratios
- Supplier-to-purchase performance metrics
- Department efficiency analysis
- Inventory turnover rates
- Cost analysis across all operations
- Stock optimization recommendations

## 🚨 **CRITICAL ALERTS & RECOMMENDATIONS**
- Low stock alerts with specific quantities
- Overstock situations requiring attention
- Unusual consumption patterns
- Supplier performance issues
- Cost optimization opportunities
- Operational efficiency improvements

Please provide specific numbers, names, and detailed analysis for each section. Include actionable insights and recommendations based on the comprehensive data analysis."""

def get_specific_table_prompts() -> dict:
    """Prompts for specific table analysis"""
    return {
        'medicines': """Analyze the MEDICINES table comprehensively:
- List all medicines with current stock levels
- Categorize by medicine type/category
- Identify critical stock levels (low/high/out of stock)
- Show dosage forms and strengths
- Include supplier information for each medicine
- Calculate average stock per category
- Highlight medicines requiring immediate attention""",
        
        'patients': """Analyze the PATIENTS table comprehensively:
- List all patients with basic information
- Show department assignments
- Include medical history summaries
- Identify most active patients by consumption
- Show recent registrations
- Analyze patient demographics if available
- Cross-reference with consumption patterns""",
        
        'suppliers': """Analyze the SUPPLIERS table comprehensively:
- List all suppliers with contact details
- Show purchase history and performance
- Calculate average purchase values
- Identify most reliable suppliers
- Show recent activity and engagement
- Analyze supplier-medicine relationships
- Evaluate cost-effectiveness by supplier""",
        
        'departments': """Analyze the DEPARTMENTS table comprehensively:
- List all departments with responsible persons
- Show contact information and details
- Analyze department-wise inventory levels
- Calculate consumption patterns by department
- Show staff assignments and responsibilities
- Evaluate department efficiency metrics""",
        
        'stores': """Analyze the STORES table comprehensively:
- List all storage locations
- Show current inventory levels by store
- Calculate storage capacity utilization
- Identify optimal stock distribution
- Show department-store relationships
- Analyze storage efficiency and accessibility""",
        
        'purchases': """Analyze the PURCHASES table comprehensively:
- List all purchase records with details
- Show purchase trends over time
- Calculate total costs and quantities
- Analyze supplier-wise purchase patterns
- Identify most expensive and frequent purchases
- Show recent purchase activity
- Evaluate purchase efficiency and cost optimization""",
        
        'consumption': """Analyze the CONSUMPTION table comprehensively:
- List all consumption records
- Show consumption patterns by patient
- Analyze department-wise consumption
- Identify most consumed medicines
- Calculate consumption rates and trends
- Show recent consumption activity
- Evaluate consumption efficiency and patterns""",
        
        'transfers': """Analyze the TRANSFERS table comprehensively:
- List all transfer records
- Show transfer patterns between departments
- Analyze transfer frequencies and quantities
- Identify most common transfer routes
- Show pending and completed transfers
- Calculate transfer efficiency metrics
- Evaluate inventory redistribution patterns"""
    }