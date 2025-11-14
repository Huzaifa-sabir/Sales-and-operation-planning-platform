import { useEffect, useMemo, useState } from 'react';
import { Card, Typography, Table, InputNumber, Button, Space, message, Upload, Tag, Select, Alert } from 'antd';
import { UploadOutlined, SaveOutlined, CheckOutlined, DownloadOutlined, ReloadOutlined, PlusOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import { cyclesAPI } from '@/api/cycles';
import { forecastsAPI, type Forecast, type MonthlyForecast } from '@/api/forecasts';
import { productsAPI } from '@/api/products';
import { customersAPI } from '@/api/customers';
import type { Customer, Product } from '@/types';

const { Title, Text } = Typography;

// Helper to convert month string (YYYY-MM) to backend format
const convertMonthToBackendFormat = (monthStr: string, quantity: number = 0): MonthlyForecast => {
  const d = dayjs(monthStr + '-01');
  return {
    year: d.year(),
    month: d.month() + 1, // dayjs months are 0-based
    monthLabel: monthStr,
    quantity,
  };
};

// Helper to convert backend format to month string for display
const getMonthFromBackend = (mf: MonthlyForecast): string => {
  return mf.monthLabel || `${mf.year}-${String(mf.month).padStart(2, '0')}`;
};

export default function ForecastEntry() {
  const [activeCycle, setActiveCycle] = useState<any | null>(null);
  const [selectedCustomerId, setSelectedCustomerId] = useState<string | null>(null);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [rows, setRows] = useState<Forecast[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingProducts, setLoadingProducts] = useState(false);
  const [loadingCustomers, setLoadingCustomers] = useState(false);

  useEffect(() => {
    loadCycle();
    loadCustomers();
  }, []);

  useEffect(() => {
    if (selectedCustomerId && activeCycle) {
      loadProductsForCustomer();
      loadForecastsForCustomer();
    } else {
      // Clear products and rows when no customer selected
      setProducts([]);
      setRows([]);
    }
  }, [selectedCustomerId, activeCycle]);

  const loadCycle = async () => {
    try {
      setLoading(true);
      const cycle = await cyclesAPI.getCurrent();
      setActiveCycle(cycle);
      if (!cycle) {
        setSelectedCustomerId(null);
        setRows([]);
      }
    } catch (e) {
      console.error('Failed to load cycle:', e);
      message.error('Failed to load cycle');
    } finally {
      setLoading(false);
    }
  };

  const loadCustomers = async () => {
    try {
      setLoadingCustomers(true);
      // Fetch all customers by looping through pages
      let allCustomers: Customer[] = [];
      let page = 1;
      let hasMore = true;
      const pageSize = 1000; // Fetch 1000 per page
      
      while (hasMore) {
        const result = await customersAPI.getAll({ page, limit: pageSize, isActive: true });
        if (result.customers && result.customers.length > 0) {
          allCustomers = [...allCustomers, ...result.customers];
          // Check if there are more pages
          hasMore = result.hasNext === true && result.customers.length === pageSize;
          page++;
        } else {
          hasMore = false;
        }
        // Safety limit to prevent infinite loops
        if (page > 100) {
          console.warn('Customer loading stopped at page 100 (safety limit)');
          break;
        }
      }
      
      console.log(`Loaded ${allCustomers.length} customers`);
      setCustomers(allCustomers);
    } catch (e) {
      console.error('Failed to load customers:', e);
      message.error('Failed to load customers');
    } finally {
      setLoadingCustomers(false);
    }
  };

  const loadProductsForCustomer = async () => {
    // Guard: Don't load products without a customer selected
    if (!selectedCustomerId) {
      setProducts([]);
      return;
    }
    
    try {
      setLoadingProducts(true);
      console.log(`Loading products for customer: ${selectedCustomerId}`);
      
      // Fetch all products for this customer by looping through pages
      let allProducts: Product[] = [];
      let page = 1;
      let hasMore = true;
      
      while (hasMore) {
        const result = await productsAPI.getByCustomer(selectedCustomerId, { page, limit: 1000, isActive: true });
        console.log(`Page ${page}: Received ${result.products?.length || 0} products, hasNext: ${result.hasNext}`);
        
        if (result.products && result.products.length > 0) {
          allProducts = [...allProducts, ...result.products];
          hasMore = result.hasNext === true && result.products.length === 1000;
          page++;
        } else {
          hasMore = false;
        }
        
        // Safety limit
        if (page > 100) {
          console.warn('Product loading stopped at page 100 (safety limit)');
          break;
        }
      }
      
      console.log(`Total products loaded for customer ${selectedCustomerId}: ${allProducts.length}`);
      console.log(`Product codes: ${allProducts.map(p => p.itemCode).join(', ')}`);
      setProducts(allProducts);
    } catch (e) {
      console.error('Failed to load products:', e);
      message.error('Failed to load products for this customer');
      setProducts([]);
    } finally {
      setLoadingProducts(false);
    }
  };

  const loadForecastsForCustomer = async () => {
    if (!selectedCustomerId || !activeCycle) return;
    try {
      const list = await forecastsAPI.list({ 
        page: 1, 
        pageSize: 1000, 
        cycleId: activeCycle._id,
        customerId: selectedCustomerId 
      });
      setRows(list.forecasts || []);
    } catch (e) {
      console.error('Failed to load forecasts:', e);
      message.error('Failed to load forecasts');
    }
  };

  const months = useMemo(() => {
    const pp = activeCycle?.planningPeriod;
    if (!pp?.months || !Array.isArray(pp.months)) return [] as string[];
    return pp.months.map((m: any) => {
      if (typeof m === 'string') return m;
      if (m.monthLabel) return m.monthLabel;
      if (m.year && m.month) return `${m.year}-${String(m.month).padStart(2, '0')}`;
      return String(m);
    }) as string[];
  }, [activeCycle]);

  const updateCell = (productId: string, month: string, value: number) => {
    setRows(prev => {
      const copy = [...prev];
      let row = copy.find(r => r.productId === productId);
      
      if (!row) {
        // Create new row if doesn't exist
        row = {
          _id: '',
          cycleId: activeCycle._id,
          customerId: selectedCustomerId!,
          productId,
          salesRepId: '',
          status: 'DRAFT' as const,
          monthlyForecasts: [],
          useCustomerPrice: true,
          totalQuantity: 0,
          totalRevenue: 0,
          version: 1,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        };
        copy.push(row);
      }
      
      const mf = [...(row.monthlyForecasts || [])];
      const idx = mf.findIndex(m => getMonthFromBackend(m) === month);
      const next = convertMonthToBackendFormat(month, Math.max(0, Number(value || 0)));
      if (idx >= 0) mf[idx] = next; else mf.push(next);
      row.monthlyForecasts = mf;
      row.totalQuantity = mf.reduce((s, m) => s + (m.quantity || 0), 0);
      
      return copy;
    });
  };

  const convertForecastsForAPI = (forecasts: MonthlyForecast[]): MonthlyForecast[] => {
    return forecasts.map(mf => {
      if (mf.monthLabel && typeof mf.year === 'number' && typeof mf.month === 'number') {
        return mf;
      }
      const monthStr = 'monthLabel' in mf ? mf.monthLabel : (mf as any).month;
      return convertMonthToBackendFormat(monthStr, mf.quantity || 0);
    });
  };

  const createForecastsForAllProducts = async () => {
    if (!selectedCustomerId || !activeCycle || products.length === 0) return;
    
    try {
      setLoading(true);
      const baseMonths: MonthlyForecast[] = months.map((m) => convertMonthToBackendFormat(m, 0));
      
      const forecastsData = products.map(product => ({
        productId: product.itemCode,
        monthlyForecasts: baseMonths,
        useCustomerPrice: true,
      }));

      const result = await forecastsAPI.bulkCreate(activeCycle._id, selectedCustomerId, forecastsData);
      message.success(`Created ${result.created} forecasts for all products`);
      await loadForecastsForCustomer();
    } catch (e: any) {
      message.error(e?.response?.data?.detail || 'Failed to create forecasts');
    } finally {
      setLoading(false);
    }
  };

  const saveAll = async () => {
    if (!selectedCustomerId || !activeCycle) return;
    
    try {
      setLoading(true);
      const forecastsData = rows.map(row => ({
        productId: row.productId,
        monthlyForecasts: convertForecastsForAPI(row.monthlyForecasts || []),
        useCustomerPrice: row.useCustomerPrice,
        overridePrice: row.overridePrice,
        notes: row.notes,
      }));

      const result = await forecastsAPI.bulkCreate(activeCycle._id, selectedCustomerId, forecastsData);
      message.success(`Saved ${result.created + result.updated} forecasts`);
      await loadForecastsForCustomer();
    } catch (e: any) {
      message.error(e?.response?.data?.detail || 'Failed to save forecasts');
    } finally {
      setLoading(false);
    }
  };

  const submitAll = async () => {
    if (!selectedCustomerId || !activeCycle) return;
    
    try {
      setLoading(true);
      // First save all
      await saveAll();
      
      // Then submit all drafts
      const drafts = rows.filter(r => r.status === 'DRAFT' && r._id);
      for (const row of drafts) {
        try {
          await forecastsAPI.submit(row._id);
        } catch (e: any) {
          console.error(`Failed to submit forecast ${row._id}:`, e);
        }
      }
      
      message.success(`Submitted ${drafts.length} forecasts`);
      await loadForecastsForCustomer();
    } catch (e: any) {
      message.error(e?.response?.data?.detail || 'Failed to submit forecasts');
    } finally {
      setLoading(false);
    }
  };

  const downloadTemplate = async () => {
    if (!activeCycle) return;
    const blob = await forecastsAPI.template(activeCycle._id);
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `forecast_template_${activeCycle.cycleName.replace(/\s+/g, '_')}.xlsx`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const exportAll = async () => {
    if (!activeCycle) return;
    const blob = await forecastsAPI.exportAll(activeCycle._id);
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `forecasts_${activeCycle.cycleName.replace(/\s+/g, '_')}_${dayjs().format('YYYYMMDD')}.xlsx`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Build table data: one row per product
  const tableData = useMemo(() => {
    return products.map(product => {
      const forecast = rows.find(r => r.productId === product.itemCode);
      return {
        key: product.itemCode,
        productId: product.itemCode,
        productDescription: product.itemDescription,
        forecast: forecast || null,
      };
    });
  }, [products, rows]);

  const columns: any[] = [
    {
      title: 'Product Code',
      dataIndex: 'productId',
      fixed: 'left',
      width: 120,
    },
    {
      title: 'Product Description',
      dataIndex: 'productDescription',
      fixed: 'left',
      width: 250,
    },
    ...months.map((m) => ({
      title: dayjs(m + '-01').format('MMM YY'),
      dataIndex: m,
      width: 110,
      render: (_: any, record: any) => {
        const forecast = record.forecast;
        const qty = forecast?.monthlyForecasts?.find((x: MonthlyForecast) => getMonthFromBackend(x) === m)?.quantity || 0;
        const disabled = !activeCycle || activeCycle.status !== 'open' || (forecast && forecast.status !== 'DRAFT');
        return (
          <InputNumber
            min={0}
            value={qty}
            disabled={disabled}
            onChange={(val) => updateCell(record.productId, m, Number(val || 0))}
            style={{ width: '100%' }}
          />
        );
      }
    })),
    {
      title: 'Total Qty',
      key: 'totalQuantity',
      width: 120,
      render: (_: any, record: any) => record.forecast?.totalQuantity || 0,
    },
    {
      title: 'Status',
      dataIndex: 'status',
      width: 110,
      render: (_: any, record: any) => {
        const status = record.forecast?.status || 'NONE';
        return <Tag color={status === 'SUBMITTED' ? 'blue' : status === 'APPROVED' ? 'green' : status === 'REJECTED' ? 'red' : 'default'}>{status}</Tag>;
      }
    }
  ];

  // Deadline calculation
  const deadlineAlert = useMemo(() => {
    if (!activeCycle) return null;
    
    const endDateRaw = activeCycle.dates?.endDate || activeCycle.dates?.closeDate || activeCycle.endDate;
    if (!endDateRaw) return <Alert type="warning" showIcon message="Cycle end date not found" />;
    
    let end = dayjs(endDateRaw);
    if (!end.isValid()) {
      if (typeof endDateRaw === 'string') {
        end = dayjs(endDateRaw, 'YYYY-MM-DDTHH:mm:ss', true);
        if (!end.isValid()) {
          end = dayjs(endDateRaw, 'YYYY-MM-DD', true);
        }
      }
    }
    
    if (!end.isValid()) {
      return <Alert type="error" showIcon message={`Invalid end date: ${String(endDateRaw)}`} />;
    }
    
    const now = dayjs().startOf('day');
    const endOfDay = end.startOf('day');
    const daysRemaining = endOfDay.diff(now, 'day');
    
    if (String(activeCycle.status).toLowerCase() !== 'open') {
      return <Alert type="info" showIcon message={`Cycle is ${String(activeCycle.status).toUpperCase()}. Editing disabled.`} />;
    }
    
    if (daysRemaining < 0) {
      return <Alert type="error" showIcon message={`Cycle deadline has passed (${endOfDay.format('MMM DD, YYYY')}). Please contact administrator.`} />;
    }
    
    if (daysRemaining === 0) {
      return <Alert type="warning" showIcon message={`Cycle closes TODAY (${endOfDay.format('MMM DD, YYYY')}). Please submit your forecasts immediately.`} />;
    }
    
    return <Alert type={daysRemaining <= 3 ? 'warning' : 'info'} showIcon message={`Cycle closes in ${daysRemaining} day${daysRemaining !== 1 ? 's' : ''} (${endOfDay.format('MMM DD, YYYY')})`} />;
  }, [activeCycle]);

  const selectedCustomer = customers.find(c => c.customerId === selectedCustomerId);

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <div>
          <Title level={3}>Forecast Entry</Title>
          <Text type="secondary">
            {activeCycle ? `${activeCycle.cycleName} · ${dayjs(activeCycle.dates?.startDate).format('MMM DD')} - ${dayjs(activeCycle.dates?.endDate || activeCycle.dates?.closeDate).format('MMM DD, YYYY')}` : 'No open cycle'}
          </Text>
          {activeCycle && (
            <div style={{ marginTop: 8 }}>
              {deadlineAlert}
            </div>
          )}
        </div>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={loadCycle} disabled={loading}>Refresh</Button>
          <Button icon={<DownloadOutlined />} onClick={downloadTemplate} disabled={!activeCycle}>Download Template</Button>
          <Upload
            beforeUpload={() => false}
            maxCount={1}
            accept=".xlsx,.xls"
            customRequest={async ({ file, onSuccess, onError }: any) => {
              try {
                const f = file as File;
                await forecastsAPI.bulkUpload(activeCycle._id, f);
                message.success('Uploaded');
                await loadForecastsForCustomer();
                onSuccess && onSuccess({}, new XMLHttpRequest());
              } catch (e: any) {
                onError && onError(e);
                message.error(e?.response?.data?.detail || 'Upload failed');
              }
            }}
          >
            <Button icon={<UploadOutlined />} disabled={!activeCycle}>Bulk Upload</Button>
          </Upload>
          <Button onClick={exportAll} disabled={!activeCycle}>Export</Button>
        </Space>
      </div>

      <Card>
        <div style={{ marginBottom: 16 }}>
          <Space size="large" align="center">
            <div>
              <Text strong>Select Customer:</Text>
              <Select
                style={{ width: 300, marginLeft: 8 }}
                placeholder="Select a customer"
                showSearch
                value={selectedCustomerId}
                onChange={setSelectedCustomerId}
                loading={loadingCustomers}
                optionFilterProp="children"
                filterOption={(input, option) =>
                  (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
                }
                options={customers.map(c => ({
                  value: c.customerId,
                  label: `${c.customerName} (${c.customerId})`
                }))}
              />
            </div>
            {selectedCustomerId && (
              <>
                <Button 
                  type="primary" 
                  icon={<PlusOutlined />} 
                  onClick={createForecastsForAllProducts}
                  disabled={!activeCycle || activeCycle.status !== 'open' || products.length === 0}
                  loading={loading}
                >
                  Create Forecasts for All Products
                </Button>
                <Button 
                  icon={<SaveOutlined />} 
                  onClick={saveAll}
                  disabled={!activeCycle || activeCycle.status !== 'open' || rows.length === 0}
                  loading={loading}
                >
                  Save All
                </Button>
                <Button 
                  type="primary" 
                  icon={<CheckOutlined />} 
                  onClick={submitAll}
                  disabled={!activeCycle || activeCycle.status !== 'open' || rows.filter(r => r.status === 'DRAFT').length === 0}
                  loading={loading}
                >
                  Submit All
                </Button>
              </>
            )}
          </Space>
        </div>

        {selectedCustomerId && (
          <>
            {selectedCustomer && (
              <div style={{ marginBottom: 16 }}>
                <Text strong>Customer: </Text>
                <Text>{selectedCustomer.customerName}</Text>
                <Text type="secondary" style={{ marginLeft: 16 }}>
                  {products.length} active product{products.length !== 1 ? 's' : ''}
                </Text>
              </div>
            )}
            
            {loadingProducts ? (
              <div style={{ textAlign: 'center', padding: 40 }}>
                <Text>Loading products...</Text>
              </div>
            ) : products.length === 0 ? (
              <Alert type="info" message="No active products found for this customer. Please contact administrator to activate products." />
            ) : (
              <Table
                columns={columns}
                dataSource={tableData}
                scroll={{ x: 'max-content' }}
                pagination={false}
                loading={loading}
                size="small"
              />
            )}
          </>
        )}

        {!selectedCustomerId && (
          <Alert type="info" message="Please select a customer to view and enter forecasts" />
        )}
      </Card>
    </div>
  );
}
