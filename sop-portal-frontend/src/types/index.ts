// User Types
export interface User {
  _id: string;
  username: string;
  email: string;
  fullName: string;
  role: 'admin' | 'sales_rep';
  isActive: boolean;
  lastLogin?: string;
  createdAt: string;
  updatedAt: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface LoginResponse {
  accessToken: string;
  tokenType: string;
  user: User;
}

// Customer Types
export interface Customer {
  _id: string;
  customerId: string;
  customerName: string;
  sopCustomerName?: string;
  trimCustomerId?: string;
  salesRepId: string;
  salesRepName: string;
  location: {
    city?: string;
    state?: string;
    address1?: string;
    address2?: string;
    zip?: string;
  };
  corporateGroup?: string;
  isActive: boolean;
  metadata?: {
    totalSalesYTD?: number;
    lastOrderDate?: string;
  };
  createdAt: string;
  updatedAt: string;
}

export interface CustomerFormData {
  customerId: string;
  customerName: string;
  sopCustomerName?: string;
  salesRepId: string;
  city?: string;
  state?: string;
  address1?: string;
  address2?: string;
  zip?: string;
  corporateGroup?: string;
}

// Product Types
export interface ProductGroup {
  code: string;
  subgroup?: string;
  desc?: string;
}

export interface ProductManufacturing {
  location: string;
  line?: string;
}

export interface ProductPricing {
  avgPrice: number;
  costPrice?: number;
  currency?: string;
}

export interface Product {
  _id: string;
  itemCode: string;
  itemDescription: string;
  group: ProductGroup;
  manufacturing: ProductManufacturing;
  weight?: number;
  uom: string;
  isActive: boolean;
  pricing: ProductPricing;
  createdAt: string;
  updatedAt: string;
}

export interface ProductFormData {
  itemCode: string;
  itemDescription: string;
  group: ProductGroup;
  manufacturing: ProductManufacturing;
  weight?: number;
  uom: string;
  pricing?: ProductPricing;
}

// Sales History Types
export interface SalesHistory {
  _id: string;
  customerId: string;
  productId: string;
  salesRepId: string;
  customerName: string;
  productCode: string;
  productDescription: string;
  salesRepName: string;
  yearMonth: string;
  year: number;
  month: number;
  quantity: number;
  unitPrice: number;
  totalSales: number;
  cogs?: number;
  grossProfit?: number;
  grossProfitPercent?: number;
  invoiceNumber?: string;
  deliveryDate?: string;
  customerPO?: string;
  workingDaysInMonth?: number;
  createdAt: string;
  updatedAt: string;
}

// S&OP Cycle Types
export interface SOPCycle {
  _id: string;
  cycleName: string;
  year: number;
  month: number;
  dates: {
    startDate: string;
    closeDate: string;
    planningStartMonth: string;
    planningEndMonth: string;
  };
  status: 'draft' | 'open' | 'closed' | 'archived';
  createdBy: {
    userId: string;
    userName: string;
  };
  stats?: {
    totalReps: number;
    submittedReps: number;
    pendingReps: number;
    completionPercent: number;
    totalForecasts: number;
    totalAmount: number;
  };
  createdAt: string;
  updatedAt: string;
}

export interface SOPCycleFormData {
  cycleName: string;
  year: number;
  month: number;
  startDate: string;
  closeDate: string;
  planningStartMonth: string;
}

// Forecast Types
export interface ForecastMonth {
  forecastMonth: string;
  monthNumber: number;
  quantity: number;
  unitPrice: number;
  totalAmount: number;
  isMandatory: boolean;
  notes?: string;
}

export interface SOPForecast {
  _id: string;
  cycleId: string;
  cycleName: string;
  salesRepId: string;
  salesRepName: string;
  customerId: string;
  customerName: string;
  productId: string;
  productCode: string;
  productDescription: string;
  forecasts: ForecastMonth[];
  submission: {
    isSubmitted: boolean;
    submittedAt?: string;
    submissionMethod?: 'portal' | 'excel';
    excelFilename?: string;
  };
  totals: {
    totalQuantity: number;
    totalAmount: number;
  };
  createdAt: string;
  updatedAt: string;
}

// Submission Types
export interface SOPSubmission {
  _id: string;
  cycleId: string;
  cycleName: string;
  salesRepId: string;
  salesRepName: string;
  submissionMethod?: 'portal' | 'excel';
  submittedAt?: string;
  excel?: {
    filename?: string;
    uploadedAt?: string;
  };
  stats: {
    totalRecords: number;
    mandatoryComplete: boolean;
    completionPercent: number;
    totalQuantity: number;
    totalAmount: number;
  };
  status: 'pending' | 'submitted' | 'approved' | 'rejected';
  notes?: string;
  createdAt: string;
  updatedAt: string;
}

// API Response Types
export interface PaginatedResponse<T> {
  total: number;
  page: number;
  limit: number;
  data: T[];
}

export interface ApiError {
  detail: string;
  errors?: Array<{
    field: string;
    message: string;
  }>;
}

// Dashboard Types
export interface AdminDashboard {
  stats: {
    totalCustomers: number;
    totalProducts: number;
    totalUsers: number;
    activeCycles: number;
  };
  currentCycle?: {
    id: string;
    cycleName: string;
    status: string;
    submissions: number;
    pending: number;
  };
  salesTrends: Array<{
    month: string;
    sales: number;
  }>;
  topCustomers: Array<{
    name: string;
    sales: number;
  }>;
  topProducts: Array<{
    name: string;
    sales: number;
  }>;
}

export interface SalesRepDashboard {
  myCustomers: {
    total: number;
    active: number;
  };
  currentCycle?: {
    id: string;
    cycleName: string;
    status: string;
    myStatus: string;
    submittedAt?: string;
  };
  recentSales: SalesHistory[];
  pendingForecasts: number;
}

// Filter/Query Types
export interface TableFilters {
  page?: number;
  limit?: number;
  search?: string;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
  [key: string]: string | number | boolean | undefined;
}
