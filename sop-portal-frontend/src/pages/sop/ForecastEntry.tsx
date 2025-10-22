import { useState, useMemo, useEffect } from 'react';
import {
  Card,
  Select,
  Button,
  Table,
  InputNumber,
  Typography,
  Space,
  Row,
  Col,
  Statistic,
  Tag,
  Alert,
  Spin,
  App,
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import {
  SaveOutlined,
  SendOutlined,
  DownloadOutlined,
  UploadOutlined,
  InfoCircleOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons';
import type { SOPCycle, Customer, Product } from '@/types';
import { cyclesAPI } from '@/api/cycles';
import { customersAPI } from '@/api/customers';
import { productsAPI } from '@/api/products';
import { forecastsAPI } from '@/api/forecasts';
// import type { ForecastCreate, ForecastMonthData } from '@/api/forecasts';
import dayjs from 'dayjs';

const { Title, Text } = Typography;


// Generate 16 months from planning start date
const generateMonthColumns = (startDate: string) => {
  const months = [];
  const start = dayjs(startDate);
  for (let i = 0; i < 16; i++) {
    const monthDate = start.add(i, 'months');
    months.push({
      key: monthDate.format('YYYY-MM'),
      label: monthDate.format('MMM YY'),
      isMandatory: i < 12, // First 12 months are mandatory
    });
  }
  return months;
};

interface ForecastRow {
  key: string;
  customerId: string;
  customerName: string;
  productId: string;
  productCode: string;
  productDescription: string;
  avgPrice: number;
  [monthKey: string]: string | number; // Dynamic month columns
}

export default function ForecastEntry() {
  const { message } = App.useApp();
  const [selectedCustomer, setSelectedCustomer] = useState<string | undefined>();
  const [selectedProduct, setSelectedProduct] = useState<string | undefined>();
  const [forecastData, setForecastData] = useState<Record<string, ForecastRow>>({});
  const [isDirty, setIsDirty] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);

  // Backend data
  const [activeCycle, setActiveCycle] = useState<SOPCycle | null>(null);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  // Fetch active cycle on mount
  useEffect(() => {
    fetchActiveCycle();
    fetchCustomers();
    fetchProducts();
  }, []);

  const fetchActiveCycle = async () => {
    try {
      setLoading(true);
      const cycle = await cyclesAPI.getCurrent();
      setActiveCycle(cycle);
    } catch (error: any) {
      console.error('Failed to fetch active cycle:', error);
      message.error(error.response?.data?.detail || 'Failed to load active S&OP cycle');
    } finally {
      setLoading(false);
    }
  };

  const fetchCustomers = async () => {
    try {
      const response = await customersAPI.getAll({ page: 1, limit: 100, isActive: true });
      setCustomers(response.customers);
    } catch (error: any) {
      console.error('Failed to fetch customers:', error);
      message.error('Failed to load customers');
    }
  };

  const fetchProducts = async () => {
    try {
      const response = await productsAPI.getAll({ page: 1, limit: 100, isActive: true });
      setProducts(response.products);
    } catch (error: any) {
      console.error('Failed to fetch products:', error);
      message.error('Failed to load products');
    }
  };

  // Generate month columns
  const monthColumns = useMemo(
    () => activeCycle ? generateMonthColumns(activeCycle.dates.planningStartMonth) : [],
    [activeCycle]
  );

  // Generate initial forecast rows based on selections
  const generateForecastRows = (): ForecastRow[] => {
    if (!selectedCustomer || !selectedProduct) return [];

    const customer = customers.find((c) => c._id === selectedCustomer);
    const product = products.find((p) => p._id === selectedProduct);

    if (!customer || !product) return [];

    const rowKey = `${customer._id}-${product._id}`;

    // Check if we already have data for this row
    if (forecastData[rowKey]) {
      return [forecastData[rowKey]];
    }

    // Generate new row with empty forecast values
    const newRow: ForecastRow = {
      key: rowKey,
      customerId: customer._id,
      customerName: customer.sopCustomerName || customer.customerName,
      productId: product._id,
      productCode: product.itemCode,
      productDescription: product.itemDescription,
      avgPrice: product.pricing?.avgPrice || 0,
    };

    // Initialize all month columns with 0
    monthColumns.forEach((month) => {
      newRow[month.key] = 0;
    });

    return [newRow];
  };

  const currentRows = generateForecastRows();

  // Handle cell value change
  const handleCellChange = (rowKey: string, monthKey: string, value: number | null) => {
    const row = currentRows[0];
    if (!row) return;

    const updatedRow = { ...row, [monthKey]: value || 0 };
    setForecastData({ ...forecastData, [rowKey]: updatedRow });
    setIsDirty(true);
  };

  // Calculate statistics
  const calculateStats = () => {
    if (currentRows.length === 0) return { totalQty: 0, totalAmount: 0, avgMonthly: 0 };

    const row = currentRows[0];
    let totalQty = 0;

    monthColumns.forEach((month) => {
      totalQty += Number(row[month.key] || 0);
    });

    const totalAmount = totalQty * row.avgPrice;
    const avgMonthly = totalQty / 16;

    return { totalQty, totalAmount, avgMonthly };
  };

  const stats = calculateStats();

  // Create dynamic columns for the table
  const columns: ColumnsType<ForecastRow> = [
    {
      title: 'Customer',
      dataIndex: 'customerName',
      key: 'customerName',
      width: 150,
      fixed: 'left',
      render: (text) => <strong>{text}</strong>,
    },
    {
      title: 'Product',
      key: 'product',
      width: 200,
      fixed: 'left',
      render: (_, record) => (
        <div>
          <Text strong>{record.productCode}</Text>
          <br />
          <Text type="secondary" style={{ fontSize: 11 }}>
            {record.productDescription}
          </Text>
        </div>
      ),
    },
    {
      title: 'Avg Price',
      dataIndex: 'avgPrice',
      key: 'avgPrice',
      width: 100,
      fixed: 'left',
      align: 'right',
      render: (price) => `$${price.toFixed(2)}`,
    },
    ...monthColumns.map((month) => ({
      title: (
        <div>
          {month.label}
          {month.isMandatory && (
            <Text type="danger" style={{ marginLeft: 4 }}>
              *
            </Text>
          )}
        </div>
      ),
      dataIndex: month.key,
      key: month.key,
      width: 100,
      align: 'right' as const,
      render: (_: any, record: ForecastRow) => (
        <InputNumber
          size="small"
          min={0}
          value={record[month.key] as number}
          onChange={(value) => handleCellChange(record.key, month.key, value)}
          style={{ width: '100%' }}
          disabled={isSubmitted || saving}
        />
      ),
    })),
  ];

  const handleSaveDraft = async () => {
    if (!activeCycle || currentRows.length === 0) {
      message.error('Please select customer and product to create forecast');
      return;
    }

    try {
      setSaving(true);
      const row = currentRows[0];

      // Prepare forecast data for API
      const monthlyForecasts = monthColumns.map((month) => {
        const [year, monthNum] = month.key.split('-').map(Number);
        return {
          year,
          month: monthNum,
          monthLabel: month.key,
          quantity: Number(row[month.key] || 0),
          unitPrice: row.avgPrice,
          revenue: Number(row[month.key] || 0) * row.avgPrice,
          isHistorical: false,
          isCurrent: false,
          isFuture: true,
        };
      });

      const forecastData: any = {
        cycleId: activeCycle._id,
        customerId: row.customerId,
        productId: row.productId,
        monthlyForecasts,
        useCustomerPrice: false,
        overridePrice: row.avgPrice,
      };

      await forecastsAPI.create(forecastData);
      message.success('Forecast saved as draft');
      setIsDirty(false);
    } catch (error: any) {
      console.error('Failed to save forecast:', error);
      message.error(error.response?.data?.detail || 'Failed to save forecast');
    } finally {
      setSaving(false);
    }
  };

  const handleSubmit = async () => {
    if (!activeCycle || currentRows.length === 0) {
      message.error('Please select customer and product to create forecast');
      return;
    }

    // Validate mandatory months (first 12)
    const row = currentRows[0];
    const mandatoryMonths = monthColumns.slice(0, 12);
    const missingMonths = mandatoryMonths.filter((month) => !row[month.key] || row[month.key] === 0);

    if (missingMonths.length > 0) {
      message.error(`Please fill in all mandatory months (first 12 months). Missing: ${missingMonths.map(m => m.label).join(', ')}`);
      return;
    }

    try {
      setSaving(true);

      // Prepare forecast data for API
      const monthlyForecasts = monthColumns.map((month) => {
        const [year, monthNum] = month.key.split('-').map(Number);
        return {
          year,
          month: monthNum,
          monthLabel: month.key,
          quantity: Number(row[month.key] || 0),
          unitPrice: row.avgPrice,
          revenue: Number(row[month.key] || 0) * row.avgPrice,
          isHistorical: false,
          isCurrent: false,
          isFuture: true,
        };
      });

      const forecastData: any = {
        cycleId: activeCycle._id,
        customerId: row.customerId,
        productId: row.productId,
        monthlyForecasts,
        useCustomerPrice: false,
        overridePrice: row.avgPrice,
      };

      // Create forecast
      const createdForecast = await forecastsAPI.create(forecastData);

      // Submit forecast
      await forecastsAPI.submit(createdForecast._id);

      setIsSubmitted(true);
      setIsDirty(false);
      message.success('Forecast submitted successfully');
    } catch (error: any) {
      console.error('Failed to submit forecast:', error);
      message.error(error.response?.data?.detail || 'Failed to submit forecast');
    } finally {
      setSaving(false);
    }
  };

  const handleImport = async () => {
    if (!activeCycle) {
      message.error('No active cycle found');
      return;
    }

    // Create file input element
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.xlsx,.xls';
    input.onchange = async (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (!file) return;

      try {
        setSaving(true);
        const result = await forecastsAPI.bulkImport(activeCycle._id, file);
        
        if (result.imported > 0) {
          message.success(`Successfully imported ${result.imported} forecasts`);
          // Refresh the page or reload data
          window.location.reload();
        } else {
          message.warning('No forecasts were imported');
        }
        
        if (result.failed > 0) {
          message.error(`${result.failed} forecasts failed to import`);
          console.error('Import errors:', result.errors);
        }
      } catch (error: any) {
        console.error('Import failed:', error);
        message.error(error.response?.data?.detail || 'Failed to import Excel file');
      } finally {
        setSaving(false);
      }
    };
    input.click();
  };

  const handleExport = async () => {
    if (!activeCycle) {
      message.error('No active cycle found');
      return;
    }

    try {
      setSaving(true);
      const blob = await forecastsAPI.exportForecasts(activeCycle._id);
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `forecasts_${activeCycle.cycleName}_${new Date().toISOString().split('T')[0]}.xlsx`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      message.success('Excel file downloaded successfully');
    } catch (error: any) {
      console.error('Export failed:', error);
      message.error(error.response?.data?.detail || 'Failed to export Excel file');
    } finally {
      setSaving(false);
    }
  };

  // Days remaining until cycle closes
  const daysRemaining = activeCycle ? dayjs(activeCycle.dates.closeDate).diff(dayjs(), 'days') : 0;
  const isNearDeadline = daysRemaining <= 5;

  if (loading || !activeCycle) {
    return (
      <div style={{ textAlign: 'center', padding: 60 }}>
        <Spin size="large" />
        <div style={{ marginTop: 16 }}>
          <Text type="secondary">Loading forecast entry page...</Text>
        </div>
      </div>
    );
  }

  return (
    <div>
      <Title level={3}>Forecast Entry - {activeCycle.cycleName}</Title>

      {/* Cycle Status Alert */}
      <Alert
        message={
          <Space>
            <ClockCircleOutlined />
            <Text strong>
              Cycle closes in {daysRemaining} days ({dayjs(activeCycle.dates.closeDate).format('MMM DD, YYYY')})
            </Text>
          </Space>
        }
        type={isNearDeadline ? 'warning' : 'info'}
        style={{ marginBottom: 16 }}
        showIcon
      />

      {/* Info Box */}
      <Card style={{ marginBottom: 16, background: '#f6f8fa' }}>
        <Space direction="vertical" size="small">
          <Text strong>
            <InfoCircleOutlined style={{ marginRight: 8 }} />
            Forecast Requirements:
          </Text>
          <Text type="secondary">
            • First 12 months are <Text type="danger" strong>mandatory</Text> (marked with *)
          </Text>
          <Text type="secondary">
            • Months 13-16 are optional but recommended
          </Text>
          <Text type="secondary">
            • Enter quantities in units (CS, BAG, etc.)
          </Text>
          <Text type="secondary">
            • Use "Save Draft" to save progress, "Submit" when complete
          </Text>
        </Space>
      </Card>

      {/* Selection and Statistics */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col xs={24} lg={12}>
          <Card>
            <Space direction="vertical" style={{ width: '100%' }} size="middle">
              <Select
                placeholder="Select Customer"
                style={{ width: '100%' }}
                size="large"
                value={selectedCustomer}
                onChange={(value) => {
                  setSelectedCustomer(value);
                  setIsSubmitted(false);
                }}
                disabled={isSubmitted || saving}
                options={customers.map((c) => ({
                  label: `${c.sopCustomerName || c.customerName} (${c.customerId})`,
                  value: c._id,
                }))}
              />
              <Select
                placeholder="Select Product"
                style={{ width: '100%' }}
                size="large"
                value={selectedProduct}
                onChange={(value) => {
                  setSelectedProduct(value);
                  setIsSubmitted(false);
                }}
                disabled={isSubmitted || saving}
                options={products.map((p) => ({
                  label: `${p.itemCode} - ${p.itemDescription}`,
                  value: p._id,
                }))}
              />
            </Space>
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Row gutter={16}>
            <Col span={8}>
              <Card>
                <Statistic
                  title="Total Quantity"
                  value={stats.totalQty}
                  suffix="units"
                  valueStyle={{ fontSize: 20 }}
                />
              </Card>
            </Col>
            <Col span={8}>
              <Card>
                <Statistic
                  title="Total Amount"
                  value={stats.totalAmount}
                  precision={0}
                  prefix="$"
                  valueStyle={{ fontSize: 20, color: '#3f8600' }}
                />
              </Card>
            </Col>
            <Col span={8}>
              <Card>
                <Statistic
                  title="Avg/Month"
                  value={stats.avgMonthly}
                  precision={0}
                  suffix="units"
                  valueStyle={{ fontSize: 20 }}
                />
              </Card>
            </Col>
          </Row>
        </Col>
      </Row>

      {/* Action Buttons */}
      <Card style={{ marginBottom: 16 }}>
        <Space>
          <Button
            type="default"
            icon={<SaveOutlined />}
            onClick={handleSaveDraft}
            disabled={!isDirty || isSubmitted || saving}
            loading={saving}
            size="large"
          >
            Save Draft
          </Button>
          <Button
            type="primary"
            icon={<SendOutlined />}
            onClick={handleSubmit}
            disabled={currentRows.length === 0 || isSubmitted || saving}
            loading={saving}
            size="large"
          >
            Submit Forecast
          </Button>
          <Button icon={<UploadOutlined />} onClick={handleImport} size="large">
            Import Excel
          </Button>
          <Button icon={<DownloadOutlined />} onClick={handleExport} size="large">
            Export Excel
          </Button>
          {isSubmitted && (
            <Tag icon={<CheckCircleOutlined />} color="success" style={{ fontSize: 14, padding: '4px 12px' }}>
              Submitted
            </Tag>
          )}
        </Space>
      </Card>

      {/* Forecast Grid */}
      <Card title={<Text strong>16-Month Forecast Grid</Text>}>
        {currentRows.length === 0 ? (
          <div style={{ textAlign: 'center', padding: 60 }}>
            <Text type="secondary" style={{ fontSize: 16 }}>
              Please select a customer and product to start entering forecast data
            </Text>
          </div>
        ) : (
          <Table
            columns={columns}
            dataSource={currentRows}
            pagination={false}
            scroll={{ x: 2400 }}
            bordered
            size="small"
          />
        )}
      </Card>

      {/* Help Text */}
      <Card style={{ marginTop: 16, background: '#fffbe6', borderColor: '#ffe58f' }}>
        <Space direction="vertical" size="small">
          <Text strong>
            <InfoCircleOutlined style={{ marginRight: 8, color: '#faad14' }} />
            Tips for accurate forecasting:
          </Text>
          <Text type="secondary">
            • Review historical sales data before entering forecasts
          </Text>
          <Text type="secondary">
            • Consider seasonal trends and customer ordering patterns
          </Text>
          <Text type="secondary">
            • Consult with customers for their upcoming requirements
          </Text>
          <Text type="secondary">
            • Update forecasts regularly as conditions change
          </Text>
        </Space>
      </Card>
    </div>
  );
}
