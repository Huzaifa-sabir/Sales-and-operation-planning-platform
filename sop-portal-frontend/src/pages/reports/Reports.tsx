import { useState, useEffect } from 'react';
import {
  Card,
  Row,
  Col,
  Select,
  DatePicker,
  Button,
  Space,
  Typography,
  Divider,
  List,
  Tag,
  Alert,
  App,
  Spin,
} from 'antd';
import {
  FileExcelOutlined,
  FilePdfOutlined,
  BarChartOutlined,
  DollarOutlined,
  ShoppingOutlined,
  TeamOutlined,
  DownloadOutlined,
  EyeOutlined,
  LineChartOutlined,
  PieChartOutlined,
} from '@ant-design/icons';
import dayjs from 'dayjs';
import { reportsAPI } from '@/api/reports';
import { cyclesAPI } from '@/api/cycles';
import { customersAPI } from '@/api/customers';
import { productsAPI } from '@/api/products';

const { Title, Text, Paragraph } = Typography;
const { RangePicker } = DatePicker;

interface ReportTemplate {
  id: string;
  name: string;
  description: string;
  category: 'sales' | 'forecast' | 'customer' | 'product' | 'performance';
  icon: React.ReactNode;
  formats: ('excel' | 'pdf' | 'powerbi')[];
  parameters: {
    dateRange?: boolean;
    customer?: boolean;
    product?: boolean;
    salesRep?: boolean;
    cycle?: boolean;
  };
}

const reportTemplates: ReportTemplate[] = [
  {
    id: 'sales-summary',
    name: 'Sales Summary Report',
    description: 'Comprehensive sales analysis with trends, totals, and breakdowns by customer and product',
    category: 'sales',
    icon: <DollarOutlined style={{ fontSize: 24, color: '#52c41a' }} />,
    formats: ['excel', 'pdf', 'powerbi'],
    parameters: {
      dateRange: true,
      customer: true,
      product: true,
      salesRep: true,
    },
  },
  {
    id: 'forecast-vs-actual',
    name: 'Forecast vs Actual',
    description: 'Compare forecasted quantities and amounts against actual sales performance',
    category: 'forecast',
    icon: <LineChartOutlined style={{ fontSize: 24, color: '#1890ff' }} />,
    formats: ['excel', 'pdf', 'powerbi'],
    parameters: {
      cycle: true,
      customer: true,
      product: true,
    },
  },
  {
    id: 'customer-performance',
    name: 'Customer Performance Report',
    description: 'Detailed customer analysis including sales trends, forecast accuracy, and rankings',
    category: 'customer',
    icon: <TeamOutlined style={{ fontSize: 24, color: '#722ed1' }} />,
    formats: ['excel', 'pdf'],
    parameters: {
      dateRange: true,
      customer: true,
    },
  },
  {
    id: 'product-analysis',
    name: 'Product Analysis Report',
    description: 'Product performance metrics, sales volumes, pricing trends, and profitability',
    category: 'product',
    icon: <ShoppingOutlined style={{ fontSize: 24, color: '#fa8c16' }} />,
    formats: ['excel', 'pdf', 'powerbi'],
    parameters: {
      dateRange: true,
      product: true,
    },
  },
  {
    id: 'cycle-submission',
    name: 'Cycle Submission Status',
    description: 'Track S&OP cycle submissions by sales rep, including completion rates and timeliness',
    category: 'performance',
    icon: <BarChartOutlined style={{ fontSize: 24, color: '#eb2f96' }} />,
    formats: ['excel', 'pdf'],
    parameters: {
      cycle: true,
      salesRep: true,
    },
  },
  {
    id: 'gross-profit',
    name: 'Gross Profit Analysis',
    description: 'Profitability analysis by customer, product, and sales rep with margin trends',
    category: 'sales',
    icon: <PieChartOutlined style={{ fontSize: 24, color: '#13c2c2' }} />,
    formats: ['excel', 'pdf', 'powerbi'],
    parameters: {
      dateRange: true,
      customer: true,
      product: true,
    },
  },
  {
    id: 'forecast-accuracy',
    name: 'Forecast Accuracy Report',
    description: 'Measure forecast accuracy by sales rep, customer, and product over time',
    category: 'performance',
    icon: <LineChartOutlined style={{ fontSize: 24, color: '#faad14' }} />,
    formats: ['excel', 'pdf'],
    parameters: {
      dateRange: true,
      salesRep: true,
    },
  },
  {
    id: 'monthly-dashboard',
    name: 'Monthly Dashboard',
    description: 'Executive summary with key metrics, charts, and KPIs for monthly review',
    category: 'performance',
    icon: <BarChartOutlined style={{ fontSize: 24, color: '#f5222d' }} />,
    formats: ['excel', 'pdf', 'powerbi'],
    parameters: {
      dateRange: true,
    },
  },
];

const mockCustomers = [
  { label: 'Industria Los Patitos', value: '1' },
  { label: 'Canadawide', value: '2' },
  { label: 'A&A Organic', value: '3' },
];

const mockProducts = [
  { label: '110001 - Peeled Garlic 12x1 LB', value: '1' },
  { label: '110002 - Peeled Garlic 12x3 LB', value: '2' },
  { label: '130030 - Garlic Puree 40 LB', value: '3' },
];

const mockSalesReps = [
  { label: 'David Brace', value: '1' },
  { label: 'John Smith', value: '2' },
  { label: 'Sarah Johnson', value: '3' },
];

const mockCycles = [
  { label: 'November 2025', value: '1' },
  { label: 'October 2025', value: '2' },
  { label: 'December 2025', value: '3' },
];

const getCategoryColor = (category: string) => {
  switch (category) {
    case 'sales':
      return 'green';
    case 'forecast':
      return 'blue';
    case 'customer':
      return 'purple';
    case 'product':
      return 'orange';
    case 'performance':
      return 'red';
    default:
      return 'default';
  }
};

export default function Reports() {
  const { message } = App.useApp();
  const [selectedReport, setSelectedReport] = useState<ReportTemplate | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string | undefined>();
  const [reportParams, setReportParams] = useState<any>({
    dateRange: [dayjs().subtract(6, 'months'), dayjs()],
    customer: undefined,
    product: undefined,
    salesRep: undefined,
    cycle: undefined,
  });
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [cycles, setCycles] = useState<any[]>([]);
  const [customers, setCustomers] = useState<any[]>([]);
  const [products, setProducts] = useState<any[]>([]);
  const [recentReports, setRecentReports] = useState<any[]>([]);

  // Load data on component mount
  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      // Load cycles
      const cyclesResponse = await cyclesAPI.list({ page: 1, limit: 100 });
      setCycles(cyclesResponse.cycles.map(c => ({ label: c.cycleName, value: c._id })));

      // Load customers
      const customersResponse = await customersAPI.getAll({ page: 1, limit: 100 });
      setCustomers(customersResponse.customers.map(c => ({ label: c.customerName, value: c._id })));

      // Load products
      const productsResponse = await productsAPI.getAll({ page: 1, limit: 100 });
      setProducts(productsResponse.products.map(p => ({ label: p.itemDescription, value: p._id })));

      // Load recent reports
      const reportsResponse = await reportsAPI.list({ limit: 10 });
      setRecentReports(reportsResponse.reports);
    } catch (error) {
      console.error('Failed to load data:', error);
      message.error('Failed to load report data');
    } finally {
      setLoading(false);
    }
  };

  const filteredReports = selectedCategory
    ? reportTemplates.filter((r) => r.category === selectedCategory)
    : reportTemplates;

  const handleSelectReport = (report: ReportTemplate) => {
    setSelectedReport(report);
    // Reset parameters
    setReportParams({
      dateRange: report.parameters.dateRange ? [dayjs().subtract(6, 'months'), dayjs()] : undefined,
      customer: undefined,
      product: undefined,
      salesRep: undefined,
      cycle: undefined,
    });
  };

  const handleGenerateReport = async (format: 'excel' | 'pdf' | 'powerbi') => {
    if (!selectedReport) return;

    if (format === 'powerbi') {
      // Open Power BI dashboard
      window.open('https://powerbi.microsoft.com/', '_blank');
      return;
    }

    setGenerating(true);
    try {
      // Map report template to backend report type
      const reportTypeMap: { [key: string]: string } = {
        'sales_summary': 'sales_summary',
        'forecast_vs_actual': 'forecast_vs_actual',
        'customer_performance': 'customer_performance',
        'product_analysis': 'product_analysis',
        'territory_performance': 'monthly_dashboard',
        'cycle_submission_status': 'cycle_submission_status',
        'gross_profit_analysis': 'gross_profit_analysis',
        'forecast_accuracy': 'forecast_accuracy',
        'monthly_dashboard': 'monthly_dashboard'
      };

      const reportType = reportTypeMap[selectedReport.id] || 'sales_summary';
      
      // Prepare parameters
      const params: any = {
        reportType,
        format: format === 'excel' ? 'excel' : 'pdf',
        includeCharts: true,
        includeRawData: false
      };

      // Add filters based on selected parameters
      if (reportParams.cycle) {
        params.cycleId = reportParams.cycle;
      }
      if (reportParams.customer) {
        params.customerId = reportParams.customer;
      }
      if (reportParams.product) {
        params.productId = reportParams.product;
      }
      if (reportParams.dateRange && reportParams.dateRange.length === 2) {
        params.startDate = reportParams.dateRange[0].format('YYYY-MM-DD');
        params.endDate = reportParams.dateRange[1].format('YYYY-MM-DD');
      }

      // Generate report
      const report = await reportsAPI.generate(params);
      
      message.success(`Report generation started! Report ID: ${report.reportId}`);
      
      // Poll for completion
      pollReportStatus(report.reportId);
      
    } catch (error) {
      console.error('Failed to generate report:', error);
      message.error('Failed to generate report');
    } finally {
      setGenerating(false);
    }
  };

  const pollReportStatus = async (reportId: string) => {
    const maxAttempts = 30; // 5 minutes max
    let attempts = 0;
    
    const poll = async () => {
      try {
        const report = await reportsAPI.getStatus(reportId);
        
        if (report.status === 'completed') {
          message.success('Report generated successfully!');
          // Trigger download
          const blob = await reportsAPI.download(reportId);
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = report.fileName || 'report.xlsx';
          document.body.appendChild(a);
          a.click();
          window.URL.revokeObjectURL(url);
          document.body.removeChild(a);
          
          // Refresh recent reports
          loadData();
        } else if (report.status === 'failed') {
          message.error('Report generation failed');
        } else if (attempts < maxAttempts) {
          // Continue polling
          attempts++;
          setTimeout(poll, 10000); // Poll every 10 seconds
        } else {
          message.warning('Report generation is taking longer than expected. Please check back later.');
        }
      } catch (error) {
        console.error('Failed to check report status:', error);
        message.error('Failed to check report status');
      }
    };
    
    poll();
  };

  return (
    <div>
      <Title level={3}>Reports & Analytics</Title>
      <Paragraph type="secondary">
        Generate reports, export data, and analyze S&OP performance metrics
      </Paragraph>

      {/* Power BI Integration Alert */}
      <Alert
        message="Power BI Integration Available"
        description="Selected reports can be opened directly in Power BI for advanced analytics and interactive dashboards"
        type="info"
        icon={<BarChartOutlined />}
        showIcon
        style={{ marginBottom: 24 }}
      />

      <Row gutter={16}>
        {/* Left Sidebar - Report List */}
        <Col xs={24} lg={10}>
          <Card
            title={
              <Space>
                <FileExcelOutlined />
                <Text strong>Available Reports</Text>
              </Space>
            }
            extra={
              <Select
                placeholder="Filter by category"
                style={{ width: 150 }}
                allowClear
                value={selectedCategory}
                onChange={setSelectedCategory}
                options={[
                  { label: 'Sales', value: 'sales' },
                  { label: 'Forecast', value: 'forecast' },
                  { label: 'Customer', value: 'customer' },
                  { label: 'Product', value: 'product' },
                  { label: 'Performance', value: 'performance' },
                ]}
              />
            }
          >
            <List
              dataSource={filteredReports}
              renderItem={(report) => (
                <List.Item
                  style={{
                    cursor: 'pointer',
                    background: selectedReport?.id === report.id ? '#e6f7ff' : 'transparent',
                    padding: 16,
                    borderRadius: 4,
                  }}
                  onClick={() => handleSelectReport(report)}
                >
                  <List.Item.Meta
                    avatar={report.icon}
                    title={
                      <Space>
                        <Text strong>{report.name}</Text>
                        <Tag color={getCategoryColor(report.category)} style={{ textTransform: 'capitalize' }}>
                          {report.category}
                        </Tag>
                      </Space>
                    }
                    description={<Text type="secondary" style={{ fontSize: 13 }}>{report.description}</Text>}
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>

        {/* Right Panel - Report Configuration */}
        <Col xs={24} lg={14}>
          {!selectedReport ? (
            <Card style={{ height: 600, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <div style={{ textAlign: 'center' }}>
                <BarChartOutlined style={{ fontSize: 64, color: '#d9d9d9', marginBottom: 16 }} />
                <Title level={4} type="secondary">
                  Select a Report
                </Title>
                <Text type="secondary">Choose a report from the list to configure and generate</Text>
              </div>
            </Card>
          ) : (
            <Card
              title={
                <Space>
                  {selectedReport.icon}
                  <Text strong>{selectedReport.name}</Text>
                </Space>
              }
            >
              <Paragraph type="secondary">{selectedReport.description}</Paragraph>

              <Divider orientation="left">Report Parameters</Divider>

              <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                {/* Date Range */}
                {selectedReport.parameters.dateRange && (
                  <div>
                    <Text strong>Date Range:</Text>
                    <RangePicker
                      style={{ width: '100%', marginTop: 8 }}
                      value={reportParams.dateRange}
                      onChange={(dates) => setReportParams({ ...reportParams, dateRange: dates })}
                      size="large"
                    />
                  </div>
                )}

                {/* S&OP Cycle */}
                {selectedReport.parameters.cycle && (
                  <div>
                    <Text strong>S&OP Cycle:</Text>
                    <Select
                      placeholder="Select cycle (optional)"
                      style={{ width: '100%', marginTop: 8 }}
                      allowClear
                      size="large"
                      value={reportParams.cycle}
                      onChange={(value) => setReportParams({ ...reportParams, cycle: value })}
                      options={cycles}
                      loading={loading}
                    />
                  </div>
                )}

                {/* Customer Filter */}
                {selectedReport.parameters.customer && (
                  <div>
                    <Text strong>Customer:</Text>
                    <Select
                      placeholder="All customers"
                      style={{ width: '100%', marginTop: 8 }}
                      allowClear
                      size="large"
                      value={reportParams.customer}
                      onChange={(value) => setReportParams({ ...reportParams, customer: value })}
                      options={customers}
                      loading={loading}
                    />
                  </div>
                )}

                {/* Product Filter */}
                {selectedReport.parameters.product && (
                  <div>
                    <Text strong>Product:</Text>
                    <Select
                      placeholder="All products"
                      style={{ width: '100%', marginTop: 8 }}
                      allowClear
                      size="large"
                      value={reportParams.product}
                      onChange={(value) => setReportParams({ ...reportParams, product: value })}
                      options={products}
                      loading={loading}
                    />
                  </div>
                )}

                {/* Sales Rep Filter */}
                {selectedReport.parameters.salesRep && (
                  <div>
                    <Text strong>Sales Rep:</Text>
                    <Select
                      placeholder="All sales reps"
                      style={{ width: '100%', marginTop: 8 }}
                      allowClear
                      size="large"
                      value={reportParams.salesRep}
                      onChange={(value) => setReportParams({ ...reportParams, salesRep: value })}
                      options={mockSalesReps}
                    />
                  </div>
                )}
              </Space>

              <Divider orientation="left">Output Format</Divider>

              <Space size="middle" wrap>
                {selectedReport.formats.includes('excel') && (
                  <Button
                    type="primary"
                    size="large"
                    icon={<FileExcelOutlined />}
                    loading={generating}
                    onClick={() => handleGenerateReport('excel')}
                  >
                    Generate Excel
                  </Button>
                )}
                {selectedReport.formats.includes('pdf') && (
                  <Button
                    size="large"
                    icon={<FilePdfOutlined />}
                    loading={generating}
                    onClick={() => handleGenerateReport('pdf')}
                  >
                    Generate PDF
                  </Button>
                )}
                {selectedReport.formats.includes('powerbi') && (
                  <Button
                    size="large"
                    icon={<BarChartOutlined />}
                    onClick={() => handleGenerateReport('powerbi')}
                  >
                    Open in Power BI
                  </Button>
                )}
              </Space>

              <Divider />

              {/* Quick Actions */}
              <Card size="small" style={{ background: '#fafafa' }}>
                <Title level={5}>Quick Actions</Title>
                <Space direction="vertical" size="small" style={{ width: '100%' }}>
                  <Button
                    type="link"
                    icon={<EyeOutlined />}
                    onClick={() => alert('Preview will be implemented with backend')}
                  >
                    Preview Report
                  </Button>
                  <Button
                    type="link"
                    icon={<DownloadOutlined />}
                    onClick={() => alert('Schedule feature will be implemented')}
                  >
                    Schedule Recurring Report
                  </Button>
                </Space>
              </Card>
            </Card>
          )}
        </Col>
      </Row>

      {/* Recently Generated Reports */}
      <Card title="Recently Generated Reports" style={{ marginTop: 24 }}>
        <Spin spinning={loading}>
          <List
            dataSource={recentReports}
            renderItem={(item) => (
              <List.Item
                actions={[
                  <Button 
                    type="link" 
                    icon={<DownloadOutlined />}
                    onClick={async () => {
                      try {
                        const blob = await reportsAPI.download(item.id);
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = item.fileName || 'report.xlsx';
                        document.body.appendChild(a);
                        a.click();
                        window.URL.revokeObjectURL(url);
                        document.body.removeChild(a);
                      } catch (error) {
                        message.error('Failed to download report');
                      }
                    }}
                  >
                    Download
                  </Button>,
                ]}
              >
                <List.Item.Meta
                  avatar={
                    item.format === 'excel' ? (
                      <FileExcelOutlined style={{ fontSize: 24, color: '#52c41a' }} />
                    ) : (
                      <FilePdfOutlined style={{ fontSize: 24, color: '#ff4d4f' }} />
                    )
                  }
                  title={`${item.reportType} - ${item.fileName || 'Report'}`}
                  description={`Generated on ${dayjs(item.createdAt).format('MMM DD, YYYY')} • ${item.fileSize ? `${(item.fileSize / 1024 / 1024).toFixed(1)} MB` : 'Unknown size'}`}
                />
              </List.Item>
            )}
          />
        </Spin>
      </Card>
    </div>
  );
}
