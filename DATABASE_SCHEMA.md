# S&OP Portal - Database Schema Design

## Database: PostgreSQL

---

## Core Tables

### 1. users
User authentication and role management

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('admin', 'sales_rep')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
```

---

### 2. customers
Customer master data

```sql
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    customer_id VARCHAR(100) UNIQUE NOT NULL, -- e.g., "PATITO-000001"
    customer_name VARCHAR(255) NOT NULL,
    sop_customer_name VARCHAR(255), -- S&OP specific name
    trim_customer_id VARCHAR(100),
    sales_rep_id INTEGER REFERENCES users(id),
    city VARCHAR(100),
    state VARCHAR(50),
    address_1 VARCHAR(255),
    address_2 VARCHAR(255),
    zip VARCHAR(20),
    corporate_group VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (sales_rep_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_customers_sales_rep ON customers(sales_rep_id);
CREATE INDEX idx_customers_active ON customers(is_active);
CREATE INDEX idx_customers_name ON customers(customer_name);
```

---

### 3. products
Product/Item master data

```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    item_code VARCHAR(50) UNIQUE NOT NULL, -- e.g., "110001"
    description TEXT NOT NULL,
    group_code VARCHAR(50), -- e.g., "G1"
    group_subgroup VARCHAR(50), -- e.g., "G1S7"
    group_desc VARCHAR(255), -- e.g., "Group 1-2"
    group_name VARCHAR(255),
    group_name2 VARCHAR(255),
    manufacturing_location VARCHAR(100), -- e.g., "Miami"
    production_line VARCHAR(100), -- e.g., "Peeled Garlic Line"
    pack_size DECIMAL(10, 2),
    weight DECIMAL(10, 2),
    uom VARCHAR(20) DEFAULT 'CS', -- Unit of measure
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_products_item_code ON products(item_code);
CREATE INDEX idx_products_group ON products(group_code);
CREATE INDEX idx_products_location ON products(manufacturing_location);
CREATE INDEX idx_products_active ON products(is_active);
```

---

### 4. product_customer_matrix
Product activation matrix (which products are available for which customers)

```sql
CREATE TABLE product_customer_matrix (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    effective_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    UNIQUE(product_id, customer_id)
);

CREATE INDEX idx_matrix_product ON product_customer_matrix(product_id);
CREATE INDEX idx_matrix_customer ON product_customer_matrix(customer_id);
CREATE INDEX idx_matrix_active ON product_customer_matrix(is_active);
```

---

### 5. sales_history
Historical sales data (24 months)

```sql
CREATE TABLE sales_history (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    sales_rep_id INTEGER,
    year_month DATE NOT NULL, -- First day of month (e.g., "2025-01-01")
    quantity DECIMAL(15, 2) NOT NULL DEFAULT 0,
    unit_price DECIMAL(15, 4),
    total_sales DECIMAL(15, 2),
    cogs DECIMAL(15, 2), -- Cost of goods sold
    gross_profit DECIMAL(15, 2),
    gross_profit_percent DECIMAL(5, 2),
    invoice_number VARCHAR(100),
    delivery_date DATE,
    customer_po VARCHAR(100),
    working_days_in_month INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (sales_rep_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_sales_year_month ON sales_history(year_month);
CREATE INDEX idx_sales_customer ON sales_history(customer_id);
CREATE INDEX idx_sales_product ON sales_history(product_id);
CREATE INDEX idx_sales_rep ON sales_history(sales_rep_id);
CREATE INDEX idx_sales_customer_product_month ON sales_history(customer_id, product_id, year_month);
```

---

### 6. sop_cycles
S&OP planning cycle management

```sql
CREATE TABLE sop_cycles (
    id SERIAL PRIMARY KEY,
    cycle_name VARCHAR(100) NOT NULL, -- e.g., "Nov 2025"
    year INTEGER NOT NULL,
    month INTEGER NOT NULL CHECK (month BETWEEN 1 AND 12),
    start_date DATE NOT NULL, -- When cycle opens for data entry
    close_date DATE NOT NULL, -- When cycle closes
    planning_start_month DATE NOT NULL, -- First month of 16-month planning
    status VARCHAR(50) DEFAULT 'draft' CHECK (status IN ('draft', 'open', 'closed', 'archived')),
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(year, month)
);

CREATE INDEX idx_sop_cycles_status ON sop_cycles(status);
CREATE INDEX idx_sop_cycles_dates ON sop_cycles(start_date, close_date);
```

---

### 7. sop_forecasts
Monthly forecast data from sales reps (16 months per cycle)

```sql
CREATE TABLE sop_forecasts (
    id SERIAL PRIMARY KEY,
    sop_cycle_id INTEGER NOT NULL,
    sales_rep_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    forecast_month DATE NOT NULL, -- Month being forecasted
    forecast_month_number INTEGER NOT NULL CHECK (forecast_month_number BETWEEN 1 AND 16),
    quantity DECIMAL(15, 2), -- Forecasted quantity (cases)
    unit_price DECIMAL(15, 4), -- Forecasted price
    total_amount DECIMAL(15, 2), -- Calculated: quantity * unit_price
    is_mandatory BOOLEAN DEFAULT TRUE, -- First 12 months are mandatory
    notes TEXT,
    submission_date TIMESTAMP,
    is_submitted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (sop_cycle_id) REFERENCES sop_cycles(id) ON DELETE CASCADE,
    FOREIGN KEY (sales_rep_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    UNIQUE(sop_cycle_id, sales_rep_id, customer_id, product_id, forecast_month)
);

CREATE INDEX idx_forecast_cycle ON sop_forecasts(sop_cycle_id);
CREATE INDEX idx_forecast_rep ON sop_forecasts(sales_rep_id);
CREATE INDEX idx_forecast_customer ON sop_forecasts(customer_id);
CREATE INDEX idx_forecast_product ON sop_forecasts(product_id);
CREATE INDEX idx_forecast_month ON sop_forecasts(forecast_month);
CREATE INDEX idx_forecast_submitted ON sop_forecasts(is_submitted);
```

---

### 8. sop_submissions
Track submission status by sales rep per cycle

```sql
CREATE TABLE sop_submissions (
    id SERIAL PRIMARY KEY,
    sop_cycle_id INTEGER NOT NULL,
    sales_rep_id INTEGER NOT NULL,
    submission_method VARCHAR(50) CHECK (submission_method IN ('excel', 'portal')),
    submitted_at TIMESTAMP,
    excel_filename VARCHAR(255),
    total_records INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'submitted', 'approved', 'rejected')),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (sop_cycle_id) REFERENCES sop_cycles(id) ON DELETE CASCADE,
    FOREIGN KEY (sales_rep_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(sop_cycle_id, sales_rep_id)
);

CREATE INDEX idx_submissions_cycle ON sop_submissions(sop_cycle_id);
CREATE INDEX idx_submissions_rep ON sop_submissions(sales_rep_id);
CREATE INDEX idx_submissions_status ON sop_submissions(status);
```

---

### 9. audit_logs
System audit trail

```sql
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    action VARCHAR(100) NOT NULL, -- e.g., "CREATE", "UPDATE", "DELETE", "LOGIN"
    entity_type VARCHAR(100), -- e.g., "customer", "product", "forecast"
    entity_id INTEGER,
    old_values JSONB,
    new_values JSONB,
    ip_address VARCHAR(50),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_action ON audit_logs(action);
CREATE INDEX idx_audit_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_created ON audit_logs(created_at);
```

---

### 10. import_logs
Track Excel import operations

```sql
CREATE TABLE import_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    import_type VARCHAR(100) NOT NULL, -- e.g., "customers", "products", "sales_history", "forecast"
    filename VARCHAR(255),
    file_size INTEGER,
    total_rows INTEGER,
    successful_rows INTEGER,
    failed_rows INTEGER,
    error_details JSONB,
    status VARCHAR(50) DEFAULT 'processing' CHECK (status IN ('processing', 'completed', 'failed')),
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_import_user ON import_logs(user_id);
CREATE INDEX idx_import_type ON import_logs(import_type);
CREATE INDEX idx_import_status ON import_logs(status);
```

---

### 11. system_settings
Application configuration

```sql
CREATE TABLE system_settings (
    id SERIAL PRIMARY KEY,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT,
    setting_type VARCHAR(50) DEFAULT 'string', -- string, integer, boolean, json
    description TEXT,
    is_editable BOOLEAN DEFAULT TRUE,
    updated_by INTEGER REFERENCES users(id),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Default settings
INSERT INTO system_settings (setting_key, setting_value, setting_type, description, is_editable) VALUES
('default_planning_months', '16', 'integer', 'Number of months for S&OP planning', TRUE),
('mandatory_planning_months', '12', 'integer', 'Number of mandatory planning months', TRUE),
('sales_history_months', '24', 'integer', 'Number of months to display in sales history', TRUE),
('enable_email_notifications', 'true', 'boolean', 'Enable email notifications for S&OP cycles', TRUE),
('company_name', 'Your Company Name', 'string', 'Company name for reports', TRUE);
```

---

## Views for Reporting

### Sales History Summary (Last 24 Months)
```sql
CREATE VIEW vw_sales_summary AS
SELECT
    sh.customer_id,
    c.customer_name,
    sh.product_id,
    p.item_code,
    p.description,
    sh.sales_rep_id,
    u.full_name as sales_rep_name,
    sh.year_month,
    SUM(sh.quantity) as total_quantity,
    AVG(sh.unit_price) as avg_price,
    SUM(sh.total_sales) as total_sales,
    SUM(sh.gross_profit) as total_gross_profit
FROM sales_history sh
JOIN customers c ON sh.customer_id = c.id
JOIN products p ON sh.product_id = p.id
LEFT JOIN users u ON sh.sales_rep_id = u.id
WHERE sh.year_month >= CURRENT_DATE - INTERVAL '24 months'
GROUP BY sh.customer_id, c.customer_name, sh.product_id, p.item_code,
         p.description, sh.sales_rep_id, u.full_name, sh.year_month;
```

### S&OP Forecast Summary by Sales Rep
```sql
CREATE VIEW vw_sop_forecast_summary AS
SELECT
    sc.id as cycle_id,
    sc.cycle_name,
    sf.sales_rep_id,
    u.full_name as sales_rep_name,
    sf.customer_id,
    c.customer_name,
    sf.forecast_month,
    sf.forecast_month_number,
    COUNT(sf.id) as total_items,
    SUM(sf.quantity) as total_quantity,
    SUM(sf.total_amount) as total_amount,
    COUNT(CASE WHEN sf.is_submitted THEN 1 END) as submitted_items
FROM sop_forecasts sf
JOIN sop_cycles sc ON sf.sop_cycle_id = sc.id
JOIN users u ON sf.sales_rep_id = u.id
JOIN customers c ON sf.customer_id = c.id
GROUP BY sc.id, sc.cycle_name, sf.sales_rep_id, u.full_name,
         sf.customer_id, c.customer_name, sf.forecast_month, sf.forecast_month_number;
```

---

## Data Relationships

1. **Users** → Sales Representatives (one-to-many with customers)
2. **Customers** → Products (many-to-many through matrix)
3. **Sales History** → Tracks past performance
4. **S&OP Cycles** → Planning periods
5. **S&OP Forecasts** → Future predictions per cycle
6. **S&OP Submissions** → Status tracking per rep

---

## Key Features Enabled by Schema

1. **Multi-tenant by Sales Rep**: Each rep sees only their customers
2. **Historical Trending**: 24 months of sales data with calculations
3. **Flexible Planning**: 16-month forecasts with mandatory/optional distinction
4. **Audit Trail**: Complete history of changes
5. **Import Tracking**: Monitor Excel uploads and errors
6. **Product Activation**: Control which products are available per customer
7. **Cycle Management**: Open/close S&OP cycles with date controls

---

## Database Size Estimation

Assuming:
- 1,000 customers
- 500 products
- 10 sales reps
- 12 S&OP cycles per year

**Approximate storage:**
- Sales History: ~10-20 GB/year
- Forecasts: ~5-10 GB/year
- Total: ~50-100 GB for 3 years of data

PostgreSQL handles this easily with proper indexing.
