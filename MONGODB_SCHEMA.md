# S&OP Portal - MongoDB Schema Design

## Database: MongoDB (instead of PostgreSQL)

MongoDB is excellent for MVP because:
- Flexible schema (easy to iterate)
- No migrations needed
- Fast development
- JSON native (perfect for React)
- Free cloud hosting (MongoDB Atlas)

---

## Collections (8 collections for MVP)

### 1. users
User authentication and roles

```javascript
{
  _id: ObjectId("..."),
  username: "john.doe",
  email: "john@example.com",
  passwordHash: "bcrypt_hash_here",
  fullName: "John Doe",
  role: "sales_rep", // "admin" or "sales_rep"
  isActive: true,
  createdAt: ISODate("2025-10-15T10:00:00Z"),
  updatedAt: ISODate("2025-10-15T10:00:00Z"),
  lastLogin: ISODate("2025-10-15T10:00:00Z")
}

// Indexes
db.users.createIndex({ email: 1 }, { unique: true })
db.users.createIndex({ username: 1 }, { unique: true })
db.users.createIndex({ role: 1 })
```

---

### 2. customers
Customer master data

```javascript
{
  _id: ObjectId("..."),
  customerId: "PATITO-000001", // External ID
  customerName: "Industria Los Patitos",
  sopCustomerName: "Los Patitos",
  trimCustomerId: "PATITO-000001",
  salesRepId: ObjectId("..."), // Reference to users._id
  salesRepName: "John Doe", // Denormalized for quick access
  location: {
    city: "Miami",
    state: "FL",
    address1: "123 Main St",
    address2: "Suite 100",
    zip: "33101"
  },
  corporateGroup: "Food Services",
  isActive: true,
  metadata: {
    totalSalesYTD: 125000.50,
    lastOrderDate: ISODate("2025-10-10T00:00:00Z")
  },
  createdAt: ISODate("2025-01-01T00:00:00Z"),
  updatedAt: ISODate("2025-10-15T00:00:00Z")
}

// Indexes
db.customers.createIndex({ customerId: 1 }, { unique: true })
db.customers.createIndex({ salesRepId: 1 })
db.customers.createIndex({ customerName: "text" }) // Text search
db.customers.createIndex({ isActive: 1 })
```

---

### 3. products
Product catalog

```javascript
{
  _id: ObjectId("..."),
  itemCode: "110001",
  description: "Peeled Garlic 12x1 LB Garland",
  group: {
    code: "G1",
    subgroup: "G1S7",
    desc: "Group 1-2",
    name: "12x1 lb P/G Domestic",
    name2: "Peeled Garlic Repack"
  },
  manufacturing: {
    location: "Miami",
    line: "Peeled Garlic Repack"
  },
  packSize: 12,
  weight: 12,
  uom: "CS",
  isActive: true,
  pricing: {
    avgPrice: 52.00,
    lastPrice: 52.00
  },
  createdAt: ISODate("2025-01-01T00:00:00Z"),
  updatedAt: ISODate("2025-10-15T00:00:00Z")
}

// Indexes
db.products.createIndex({ itemCode: 1 }, { unique: true })
db.products.createIndex({ "group.code": 1 })
db.products.createIndex({ "manufacturing.location": 1 })
db.products.createIndex({ description: "text" })
db.products.createIndex({ isActive: 1 })
```

---

### 4. productCustomerMatrix
Product activation per customer

```javascript
{
  _id: ObjectId("..."),
  productId: ObjectId("..."),
  customerId: ObjectId("..."),
  // Denormalized for performance
  productCode: "110001",
  customerName: "ABC Company",
  isActive: true,
  effectiveDate: ISODate("2025-01-01T00:00:00Z"),
  createdAt: ISODate("2025-01-01T00:00:00Z"),
  updatedAt: ISODate("2025-10-15T00:00:00Z")
}

// Indexes
db.productCustomerMatrix.createIndex({ productId: 1, customerId: 1 }, { unique: true })
db.productCustomerMatrix.createIndex({ customerId: 1 })
db.productCustomerMatrix.createIndex({ productId: 1 })
db.productCustomerMatrix.createIndex({ isActive: 1 })
```

---

### 5. salesHistory
Historical sales data (24 months)

```javascript
{
  _id: ObjectId("..."),
  customerId: ObjectId("..."),
  productId: ObjectId("..."),
  salesRepId: ObjectId("..."),

  // Denormalized for reporting
  customerName: "ABC Company",
  productCode: "110001",
  productDescription: "Peeled Garlic 12x1 LB",
  salesRepName: "John Doe",

  // Date (stored as first day of month)
  yearMonth: ISODate("2025-10-01T00:00:00Z"),
  year: 2025,
  month: 10,

  // Financial data
  quantity: 500,
  unitPrice: 52.00,
  totalSales: 26000.00,
  cogs: 18200.00,
  grossProfit: 7800.00,
  grossProfitPercent: 30.00,

  // Additional info
  invoiceNumber: "INV-12345",
  deliveryDate: ISODate("2025-10-15T00:00:00Z"),
  customerPO: "PO-67890",
  workingDaysInMonth: 21,

  createdAt: ISODate("2025-10-15T00:00:00Z"),
  updatedAt: ISODate("2025-10-15T00:00:00Z")
}

// Indexes
db.salesHistory.createIndex({ yearMonth: -1 }) // Descending for recent first
db.salesHistory.createIndex({ customerId: 1, yearMonth: -1 })
db.salesHistory.createIndex({ productId: 1, yearMonth: -1 })
db.salesHistory.createIndex({ salesRepId: 1, yearMonth: -1 })
db.salesHistory.createIndex({ year: 1, month: 1 })
```

---

### 6. sopCycles
S&OP planning cycles

```javascript
{
  _id: ObjectId("..."),
  cycleName: "Nov 2025",
  year: 2025,
  month: 11,

  dates: {
    startDate: ISODate("2025-10-15T00:00:00Z"),
    closeDate: ISODate("2025-10-30T00:00:00Z"),
    planningStartMonth: ISODate("2025-11-01T00:00:00Z"),
    planningEndMonth: ISODate("2027-02-28T00:00:00Z") // 16 months later
  },

  status: "open", // "draft", "open", "closed", "archived"

  createdBy: {
    userId: ObjectId("..."),
    userName: "Admin User"
  },

  stats: {
    totalReps: 10,
    submittedReps: 8,
    pendingReps: 2,
    completionPercent: 80.0,
    totalForecasts: 2500,
    totalAmount: 5000000.00
  },

  createdAt: ISODate("2025-10-01T00:00:00Z"),
  updatedAt: ISODate("2025-10-15T00:00:00Z")
}

// Indexes
db.sopCycles.createIndex({ year: 1, month: 1 }, { unique: true })
db.sopCycles.createIndex({ status: 1 })
db.sopCycles.createIndex({ "dates.startDate": 1, "dates.closeDate": 1 })
```

---

### 7. sopForecasts
Forecast data (16 months per cycle)

```javascript
{
  _id: ObjectId("..."),
  cycleId: ObjectId("..."),
  cycleName: "Nov 2025", // Denormalized

  salesRepId: ObjectId("..."),
  salesRepName: "John Doe", // Denormalized

  customerId: ObjectId("..."),
  customerName: "ABC Company", // Denormalized

  productId: ObjectId("..."),
  productCode: "110001", // Denormalized
  productDescription: "Peeled Garlic 12x1 LB", // Denormalized

  // Array of 16 months forecast
  forecasts: [
    {
      forecastMonth: ISODate("2025-11-01T00:00:00Z"),
      monthNumber: 1, // 1-16
      quantity: 500,
      unitPrice: 52.00,
      totalAmount: 26000.00,
      isMandatory: true, // First 12 are mandatory
      notes: "Holiday season increase"
    },
    {
      forecastMonth: ISODate("2025-12-01T00:00:00Z"),
      monthNumber: 2,
      quantity: 550,
      unitPrice: 52.00,
      totalAmount: 28600.00,
      isMandatory: true,
      notes: ""
    }
    // ... 14 more months
  ],

  submission: {
    isSubmitted: true,
    submittedAt: ISODate("2025-10-20T15:30:00Z"),
    submissionMethod: "portal", // "portal" or "excel"
    excelFilename: null
  },

  totals: {
    totalQuantity: 8000,
    totalAmount: 416000.00
  },

  createdAt: ISODate("2025-10-15T00:00:00Z"),
  updatedAt: ISODate("2025-10-20T15:30:00Z")
}

// Indexes
db.sopForecasts.createIndex({ cycleId: 1, salesRepId: 1, customerId: 1, productId: 1 }, { unique: true })
db.sopForecasts.createIndex({ cycleId: 1 })
db.sopForecasts.createIndex({ salesRepId: 1 })
db.sopForecasts.createIndex({ "submission.isSubmitted": 1 })
```

---

### 8. sopSubmissions
Track submission status per sales rep per cycle

```javascript
{
  _id: ObjectId("..."),
  cycleId: ObjectId("..."),
  cycleName: "Nov 2025", // Denormalized

  salesRepId: ObjectId("..."),
  salesRepName: "John Doe", // Denormalized

  submissionMethod: "portal", // "portal" or "excel"
  submittedAt: ISODate("2025-10-20T15:30:00Z"),

  excel: {
    filename: "forecast_john_doe_nov2025.xlsx",
    uploadedAt: ISODate("2025-10-20T15:30:00Z")
  },

  stats: {
    totalRecords: 250,
    mandatoryComplete: true,
    completionPercent: 100.0,
    totalQuantity: 50000,
    totalAmount: 2500000.00
  },

  status: "submitted", // "pending", "submitted", "approved", "rejected"
  notes: "",

  createdAt: ISODate("2025-10-15T00:00:00Z"),
  updatedAt: ISODate("2025-10-20T15:30:00Z")
}

// Indexes
db.sopSubmissions.createIndex({ cycleId: 1, salesRepId: 1 }, { unique: true })
db.sopSubmissions.createIndex({ cycleId: 1 })
db.sopSubmissions.createIndex({ salesRepId: 1 })
db.sopSubmissions.createIndex({ status: 1 })
```

---

## MongoDB Design Principles Used

### 1. Denormalization for Performance
- Store frequently accessed data together
- Example: Store `salesRepName` in customers to avoid joins
- Trade-off: Slightly more storage for much faster reads

### 2. Embedded Documents
- Store related data as nested objects
- Example: `location` object in customers
- Example: Array of `forecasts` in sopForecasts

### 3. Flexible Schema
- Can add fields without migrations
- Easy to evolve during MVP development

### 4. Strategic Indexes
- Index frequently queried fields
- Text indexes for search
- Compound indexes for complex queries

---

## Data Relationships (Reference Pattern)

```javascript
// One-to-Many: User → Customers
// Store userId in customer document
{
  customerId: "ABC-001",
  salesRepId: ObjectId("user123"),
  salesRepName: "John Doe" // Denormalized
}

// Many-to-Many: Products ↔ Customers
// Separate collection: productCustomerMatrix
{
  productId: ObjectId("prod123"),
  customerId: ObjectId("cust456"),
  isActive: true
}

// One-to-Many: Cycle → Forecasts
// Store cycleId in forecast document
{
  cycleId: ObjectId("cycle789"),
  cycleName: "Nov 2025", // Denormalized
  salesRepId: ObjectId("user123"),
  forecasts: [...] // Embedded array
}
```

---

## Aggregation Pipeline Examples

### Sales Summary by Customer
```javascript
db.salesHistory.aggregate([
  {
    $match: {
      yearMonth: { $gte: ISODate("2024-10-01") }
    }
  },
  {
    $group: {
      _id: "$customerId",
      customerName: { $first: "$customerName" },
      totalSales: { $sum: "$totalSales" },
      totalQuantity: { $sum: "$quantity" },
      avgPrice: { $avg: "$unitPrice" }
    }
  },
  {
    $sort: { totalSales: -1 }
  }
])
```

### Forecast Summary by Cycle
```javascript
db.sopForecasts.aggregate([
  {
    $match: { cycleId: ObjectId("cycle123") }
  },
  {
    $group: {
      _id: "$salesRepId",
      salesRepName: { $first: "$salesRepName" },
      totalQuantity: { $sum: "$totals.totalQuantity" },
      totalAmount: { $sum: "$totals.totalAmount" },
      forecastCount: { $sum: 1 }
    }
  }
])
```

---

## Collection Size Estimates (for planning)

Assuming:
- 1,000 customers
- 500 products
- 10 sales reps
- 12 S&OP cycles/year

**Approximate storage:**
- users: < 1 MB
- customers: ~5 MB
- products: ~3 MB
- productCustomerMatrix: ~10 MB
- salesHistory: ~500 MB/year (24 months)
- sopCycles: < 1 MB
- sopForecasts: ~200 MB/cycle (~2.4 GB/year)
- sopSubmissions: < 10 MB

**Total: ~3-5 GB/year** (easily handled by MongoDB)

---

## MongoDB Atlas Setup (Free Tier)

MongoDB Atlas offers a **FREE tier** perfect for MVP:
- 512 MB storage
- Shared cluster
- No credit card required
- Perfect for development and small production

**Upgrade later** when you need more:
- M10 tier: $0.08/hour (~$57/month)
- More storage and performance
- Automated backups

---

## Migration from PostgreSQL Design

The PostgreSQL schema translates easily to MongoDB:
- Each table → Collection
- Foreign keys → ObjectId references
- Complex queries → Aggregation pipelines
- Views → Aggregation pipeline queries

---

## MVP Collections (Start with these)

For the MVP, you can start with just **5 collections**:

1. **users** - Authentication
2. **customers** - Customer data
3. **products** - Product catalog
4. **sopCycles** - S&OP cycles
5. **sopForecasts** - Forecast data

Add later:
- salesHistory (when importing historical data)
- productCustomerMatrix (when needed)
- sopSubmissions (for detailed tracking)

---

## Next: Backend Setup

MongoDB works great with:
- **Node.js + Express** (JavaScript)
- **Python + FastAPI + Motor** (async MongoDB driver)
- **Node.js + Fastify** (faster than Express)

For Python/FastAPI (recommended):
```bash
pip install motor pymongo
```

For Node.js/Express (alternative):
```bash
npm install mongodb express
```

---

This schema is **production-ready** but flexible enough for rapid MVP development!
