export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const TOKEN_KEY = 'sop_access_token';
export const USER_KEY = 'sop_user';

export const ROLES = {
  ADMIN: 'admin',
  SALES_REP: 'sales_rep',
} as const;

export const SOP_STATUS = {
  DRAFT: 'draft',
  OPEN: 'open',
  CLOSED: 'closed',
  ARCHIVED: 'archived',
} as const;

export const SUBMISSION_STATUS = {
  PENDING: 'pending',
  SUBMITTED: 'submitted',
  APPROVED: 'approved',
  REJECTED: 'rejected',
} as const;

export const SUBMISSION_METHOD = {
  PORTAL: 'portal',
  EXCEL: 'excel',
} as const;

export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  DASHBOARD: '/dashboard',

  // Customers
  CUSTOMERS: '/customers',
  CUSTOMER_DETAIL: '/customers/:id',
  CUSTOMER_IMPORT: '/customers/import',

  // Products
  PRODUCTS: '/products',
  PRODUCT_DETAIL: '/products/:id',
  PRODUCT_IMPORT: '/products/import',

  // Sales History
  SALES_HISTORY: '/sales-history',

  // S&OP
  SOP_CYCLES: '/sop/cycles',
  SOP_CYCLE_DETAIL: '/sop/cycles/:id',
  FORECAST_ENTRY: '/sop/forecast/:cycleId',
  FORECAST_IMPORT: '/sop/import/:cycleId',

  // Reports
  REPORTS: '/reports',

  // Admin
  ADMIN_USERS: '/admin/users',
  ADMIN_SETTINGS: '/admin/settings',
} as const;

export const PAGINATION = {
  DEFAULT_PAGE: 1,
  DEFAULT_LIMIT: 50,
  MAX_LIMIT: 100,
} as const;

export const DATE_FORMAT = {
  DISPLAY: 'MMM dd, yyyy',
  MONTH_YEAR: 'MMM yyyy',
  API: 'yyyy-MM-dd',
} as const;

export const US_STATES = [
  'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
  'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
  'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
  'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
  'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY',
];

export const PRODUCT_GROUPS = ['G1', 'G2', 'G3', 'G4', 'G5'];
export const MANUFACTURING_LOCATIONS = ['Miami', 'New York', 'Los Angeles', 'Other'];
export const UNITS_OF_MEASURE = ['CS', 'LB', 'KG', 'EA'];

export const MANDATORY_FORECAST_MONTHS = 12;
export const TOTAL_FORECAST_MONTHS = 16;
export const SALES_HISTORY_MONTHS = 24;
