StockFlow Technical Assessment - Inventory Management System
 Project Overview
This repository contains my solution for the StockFlow Backend Technical Assessment. The goal was to debug an existing product creation API, design a scalable database schema, and implement a low-stock alert system with predictive logic.

 Code Review & Debugging (Part 1)
Upon reviewing the initial implementation, I identified three critical issues that would compromise data integrity in a production environment:

The Commit Problem (Lack of Atomicity):

Issue: The original code used two separate db.session.commit() calls. If the system failed after saving the product but before saving the inventory, it would result in "orphaned" products with no stock records.

My Fix: I implemented a single transaction approach using db.session.flush() followed by a single db.session.commit(). This ensures an "all or nothing" execution.

Missing Input Validation:

Issue: The API directly accessed request.json without verifying if required fields (like SKU or Name) were present, which would cause the application to crash with a KeyError.

My Fix: I added manual validation to check for all required fields and return a user-friendly error message if data is missing.

SKU Uniqueness Enforcement:

Issue: Business rules require unique SKUs, but the code lacked a check for existing SKUs before insertion.

My Fix: I added a database query to check for SKU existence before proceeding with the creation of a new product.

 Database Design (Part 2)
I designed a normalized database schema to ensure scalability and support the "multiple warehouse" requirement.

Warehouses Table: Includes a company_id to allow multi-tenant management.

Inventory Table (Bridge Table): Links Products and Warehouses. It includes a low_stock_threshold column, allowing different alert levels for different products.

Bundles Logic: To support product bundles, I proposed a Bundle_Items table using a parent-child relationship (self-referencing table).

 Low-Stock Alerts API (Part 3)
I developed a comprehensive API endpoint to identify products running low on stock.

Data Integration: The query joins four tables (Inventory, Product, Warehouse, and Supplier) to provide all necessary reordering information in one call.

Predictive Logic: I implemented a "Days Until Stockout" calculation to help warehouse managers prioritize reorders: Days Remaining = Current Stock / Average Daily Sales

 Questions for the Product Team
To further improve the system, I have identified the following points for clarification:

Bundle Stock Calculation: If a single component of a bundle runs out of stock, should the entire bundle automatically be marked as "Out of Stock"?

Automated Notifications: Beyond the API, should the system trigger automated email or SMS alerts when the threshold is reached?
Tech Stack
Language: Python

Framework: Flask

ORM: Flask-SQLAlchemy

Database: MySQL 