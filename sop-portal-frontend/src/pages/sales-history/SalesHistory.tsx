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
  const [selectedCustomer, setSelectedCustomer] = useState<string | undefined>();
  const [selectedProduct, setSelectedProduct] = useState<string | undefined>();
  const [pagination, setPagination] = useState({
    page: 1,
    pageSize: 100,
    total: 0,
  });

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
      setSalesData((response as any).records || response.data || []);
      setPagination(prev => ({
        ...prev,
        total: response.total || 0,
      }));
    } catch (error) {
      console.error('Failed to fetch sales history:', error);
      message.error('Failed to load sales history');
    } finally {
      setLoading(false);
    }
  };

  // Fetch sales history from backend
  useEffect(() => {
    fetchSalesHistory();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedCustomer, selectedProduct, pagination.page]);

  // Data is already filtered by backend, so use as is
  const filteredData = salesData;

  // Calculate statistics
  const stats = {
    totalSales: filteredData.reduce((sum, item) => sum + item.totalSales, 0),
    totalQuantity: filteredData.reduce((sum, item) => sum + item.quantity, 0),
    avgPrice: filteredData.length > 0 ? filteredData.reduce((sum, item) => sum + item.unitPrice, 0) / filteredData.length : 0,
    grossProfit: filteredData.reduce((sum, item) => sum + (item.grossProfit || 0), 0),
  };

  // Get last 6 months for detailed view
  const last6Months = filteredData
    .sort((a, b) => new Date(b.yearMonth).getTime() - new Date(a.yearMonth).getTime())
    .slice(0, 18);

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
                  style={{ width: 200 }}
                  allowClear
                  value={selectedCustomer}
                  onChange={setSelectedCustomer}
                  options={[
                    { label: 'Industria Los Patitos', value: 'Industria Los Patitos' },
                    { label: 'Canadawide', value: 'Canadawide' },
                    { label: 'A&A Organic', value: 'A&A Organic' },
                  ]}
                />
                <Select
                  placeholder="Filter by Product"
                  style={{ width: 200 }}
                  allowClear
                  value={selectedProduct}
                  onChange={setSelectedProduct}
                  options={[
                    { label: '110001 - Peeled Garlic 12x1 LB', value: '110001' },
                    { label: '110002 - Peeled Garlic 12x3 LB', value: '110002' },
                    { label: '130030 - Garlic Puree 40 LB', value: '130030' },
                  ]}
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
            dataSource={last6Months}
            rowKey="_id"
            scroll={{ x: 1200 }}
            pagination={{
              pageSize: 20,
              showTotal: (total) => `Total ${total} records`,
            }}
          />
        </Space>
      </Card>
    </div>
    </Spin>
  );
}
