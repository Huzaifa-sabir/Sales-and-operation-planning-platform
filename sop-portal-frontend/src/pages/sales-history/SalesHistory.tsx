import { useState, useEffect } from 'react';
import {
  Table,
  Card,
  Select,
  Space,
  Typography,
  Row,
  Col,
  Statistic,
  Tag,
  Button,
  Spin,
  message,
} from 'antd';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import type { ColumnsType } from 'antd/es/table';
import {
  DollarOutlined,
  RiseOutlined,
  DownloadOutlined,
} from '@ant-design/icons';
import type { SalesHistory as SalesHistoryType } from '@/types';
import { salesHistoryAPI } from '@/api/salesHistory';
import { customersAPI } from '@/api/customers';
import { productsAPI } from '@/api/products';
import dayjs from 'dayjs';

const { Title, Text } = Typography;


// Aggregate by month for chart
const getMonthlyTotals = (data: SalesHistoryType[]) => {
  const monthly = data.reduce((acc, item) => {
    const key = dayjs(item.yearMonth).format('MMM YY');
    if (!acc[key]) {
      acc[key] = { month: key, totalSales: 0, quantity: 0, grossProfit: 0 };
    }
    acc[key].totalSales += item.totalSales;
    acc[key].quantity += item.quantity;
    acc[key].grossProfit += (item.grossProfit || 0);
    return acc;
  }, {} as Record<string, any>);

  return Object.values(monthly);
};

export default function SalesHistory() {
  const [salesData, setSalesData] = useState<SalesHistoryType[]>([]);
  const [loading, setLoading] = useState(false);
  const [customers, setCustomers] = useState<Array<{label: string, value: string}>>([]);
  const [products, setProducts] = useState<Array<{label: string, value: string}>>([]);
  const [loadingCustomers, setLoadingCustomers] = useState(false);
  const [loadingProducts, setLoadingProducts] = useState(false);
  const [selectedCustomer, setSelectedCustomer] = useState<string | undefined>();
  const [selectedProduct, setSelectedProduct] = useState<string | undefined>();
  const [pagination, setPagination] = useState({
    page: 1,
    pageSize: 200, // Fetch more records initially
    total: 0,
    totalPages: 0,
  });
  
  const [tablePagination, setTablePagination] = useState({
    current: 1,
    pageSize: 20,
  });

  const fetchCustomers = async () => {
    try {
      setLoadingCustomers(true);
      const result = await customersAPI.getAll({ page: 1, limit: 1000, isActive: true });
      const customerOptions = (result.customers || []).map(c => ({
        label: `${c.customerName} (${c.customerId})`,
        value: c.customerId
      }));
      setCustomers(customerOptions);
    } catch (error) {
      console.error('Failed to fetch customers:', error);
    } finally {
      setLoadingCustomers(false);
    }
  };

  const fetchProducts = async () => {
    try {
      setLoadingProducts(true);
      // Fetch in batches since backend limit is 100 per page
      let allProducts: any[] = [];
      let page = 1;
      let hasMore = true;
      
      while (hasMore) {
        const result = await productsAPI.getAll({ page, limit: 100, isActive: true });
        allProducts = [...allProducts, ...(result.products || [])];
        hasMore = result.hasNext || false;
        page++;
        if (page > 100) break; // Safety limit
      }
      
      const productOptions = allProducts.map(p => ({
        label: `${p.itemCode} - ${p.itemDescription}`,
        value: p.itemCode
      }));
      setProducts(productOptions);
    } catch (error) {
      console.error('Failed to fetch products:', error);
      message.error('Failed to load products');
    } finally {
      setLoadingProducts(false);
    }
  };

  const fetchSalesHistory = async () => {
    try {
      setLoading(true);
      const response = await salesHistoryAPI.list({
        skip: (pagination.page - 1) * pagination.pageSize,
        limit: pagination.pageSize,
        customerId: selectedCustomer,
        productId: selectedProduct,
      });

      // Backend returns 'records' not 'data'
      const records = (response as any).records || response.data || [];
      setSalesData(records);
      setPagination(prev => ({
        ...prev,
        total: response.total || 0,
        totalPages: response.totalPages || Math.ceil((response.total || 0) / prev.pageSize),
      }));
    } catch (error) {
      console.error('Failed to fetch sales history:', error);
      message.error('Failed to load sales history');
    } finally {
      setLoading(false);
    }
  };

  // Fetch customers and products on mount
  useEffect(() => {
    fetchCustomers();
    fetchProducts();
  }, []);

  // Fetch sales history from backend when filters or pagination changes
  useEffect(() => {
    fetchSalesHistory();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedCustomer, selectedProduct, pagination.page, pagination.pageSize]);

  // Data is already filtered by backend, so use as is
  const filteredData = salesData;

  // Calculate statistics from all loaded data (we'll need to fetch all for accurate stats)
  const stats = {
    totalSales: filteredData.reduce((sum, item) => sum + (item.totalSales || 0), 0),
    totalQuantity: filteredData.reduce((sum, item) => sum + (item.quantity || 0), 0),
    avgPrice: filteredData.length > 0 ? filteredData.reduce((sum, item) => sum + (item.unitPrice || 0), 0) / filteredData.length : 0,
    grossProfit: filteredData.reduce((sum, item) => sum + (item.grossProfit || 0), 0),
  };

  // Use all filtered data, sorted by date (newest first)
  const sortedData = [...filteredData].sort((a, b) => {
    const dateA = new Date(a.yearMonth || `${a.year}-${String(a.month).padStart(2, '0')}`).getTime();
    const dateB = new Date(b.yearMonth || `${b.year}-${String(b.month).padStart(2, '0')}`).getTime();
    return dateB - dateA;
  });

  const chartData = getMonthlyTotals(filteredData);

  const columns: ColumnsType<SalesHistoryType> = [
    {
      title: 'Month',
      dataIndex: 'yearMonth',
      key: 'yearMonth',
      width: 120,
      render: (date) => <strong>{dayjs(date).format('MMM YYYY')}</strong>,
      sorter: (a, b) => new Date(a.yearMonth).getTime() - new Date(b.yearMonth).getTime(),
    },
    {
      title: 'Customer',
      dataIndex: 'customerName',
      key: 'customerName',
      width: 200,
    },
    {
      title: 'Product',
      key: 'product',
      width: 250,
      render: (_, record) => (
        <div>
          <Text strong>{record.productCode}</Text>
          <br />
          <Text type="secondary" style={{ fontSize: 12 }}>
            {record.productDescription}
          </Text>
        </div>
      ),
    },
    {
      title: 'Quantity',
      dataIndex: 'quantity',
      key: 'quantity',
      width: 100,
      align: 'right',
      render: (qty) => qty.toLocaleString(),
    },
    {
      title: 'Unit Price',
      dataIndex: 'unitPrice',
      key: 'unitPrice',
      width: 120,
      align: 'right',
      render: (price) => `$${price.toFixed(2)}`,
    },
    {
      title: 'Total Sales',
      dataIndex: 'totalSales',
      key: 'totalSales',
      width: 130,
      align: 'right',
      render: (sales) => <strong>${sales.toLocaleString(undefined, { maximumFractionDigits: 0 })}</strong>,
      sorter: (a, b) => a.totalSales - b.totalSales,
    },
    {
      title: 'Gross Profit',
      dataIndex: 'grossProfit',
      key: 'grossProfit',
      width: 130,
      align: 'right',
      render: (profit) => (
        <Tag color="green">${profit.toLocaleString(undefined, { maximumFractionDigits: 0 })}</Tag>
      ),
    },
    {
      title: 'GP %',
      dataIndex: 'grossProfitPercent',
      key: 'grossProfitPercent',
      width: 80,
      align: 'right',
      render: (percent) => `${percent.toFixed(1)}%`,
    },
  ];

  return (
    <Spin spinning={loading}>
      <div>
        <Title level={3}>Sales History (Last 24 Months)</Title>

        {/* Statistics Cards */}
        <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Total Sales"
              value={stats.totalSales}
              precision={0}
              prefix={<DollarOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Total Quantity"
              value={stats.totalQuantity}
              suffix="units"
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Avg Unit Price"
              value={stats.avgPrice}
              precision={2}
              prefix="$"
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Gross Profit"
              value={stats.grossProfit}
              precision={0}
              prefix={<RiseOutlined />}
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Charts */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col xs={24} lg={12}>
          <Card title="Sales Trend (24 Months)" bordered={false}>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip formatter={(value: number) => `$${value.toLocaleString()}`} />
                <Legend />
                <Line type="monotone" dataKey="totalSales" stroke="#8884d8" strokeWidth={2} name="Total Sales" />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="Quantity Trend (24 Months)" bordered={false}>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="quantity" fill="#82ca9d" name="Quantity" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      {/* Filters and Table */}
      <Card>
        <Space direction="vertical" style={{ width: '100%' }} size="middle">
          <Row gutter={16} align="middle">
            <Col flex="auto">
              <Space wrap>
                <Select
                  placeholder="Filter by Customer"
                  style={{ width: 300 }}
                  allowClear
                  showSearch
                  loading={loadingCustomers}
                  value={selectedCustomer}
                  onChange={setSelectedCustomer}
                  filterOption={(input, option) =>
                    (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
                  }
                  options={customers}
                />
                <Select
                  placeholder="Filter by Product"
                  style={{ width: 350 }}
                  allowClear
                  showSearch
                  loading={loadingProducts}
                  value={selectedProduct}
                  onChange={setSelectedProduct}
                  filterOption={(input, option) =>
                    (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
                  }
                  options={products}
                />
              </Space>
            </Col>
            <Col>
              <Button
                icon={<DownloadOutlined />}
                size="large"
                onClick={async () => {
                  try {
                    const blob = await salesHistoryAPI.exportExcel({
                      customerId: selectedCustomer,
                      productId: selectedProduct,
                      limit: 1000,
                    });
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `sales_history_${Date.now()}.xlsx`;
                    document.body.appendChild(a);
                    a.click();
                    a.remove();
                    window.URL.revokeObjectURL(url);
                  } catch (e) {
                    message.error('Failed to export Excel');
                  }
                }}
              >
                Export Excel
              </Button>
            </Col>
          </Row>

          <Table
            columns={columns}
            dataSource={sortedData}
            rowKey={(record) => record.id || record._id || `${record.customerId}-${record.productId}-${record.year}-${record.month}`}
            scroll={{ x: 1200 }}
            loading={loading}
            pagination={{
              current: tablePagination.current,
              pageSize: tablePagination.pageSize,
              total: sortedData.length, // Total records in current fetch
              showTotal: (total, range) => {
                const totalFromServer = pagination.total;
                if (totalFromServer > total) {
                  return `Showing ${range[0]}-${range[1]} of ${total} loaded (${totalFromServer} total)`;
                }
                return `Showing ${range[0]}-${range[1]} of ${total} records`;
              },
              showSizeChanger: true,
              pageSizeOptions: ['20', '50', '100', '200'],
              onChange: (page, pageSize) => {
                setTablePagination({ current: page, pageSize });
              },
              onShowSizeChange: (current, size) => {
                setTablePagination({ current: 1, pageSize: size });
              },
            }}
          />
        </Space>
      </Card>
    </div>
    </Spin>
  );
}
