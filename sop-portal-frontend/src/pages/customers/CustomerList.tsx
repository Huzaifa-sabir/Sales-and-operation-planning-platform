import { useState } from 'react';
import {
  Table,
  Button,
  Input,
  Space,
  Tag,
  Modal,
  Form,
  message,
  Popconfirm,
  Select,
  Upload,
  Card,
  Typography,
  Row,
  Col,
  Statistic,
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import {
  PlusOutlined,
  SearchOutlined,
  EditOutlined,
  DeleteOutlined,
  UploadOutlined,
  DownloadOutlined,
  TeamOutlined,
} from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import type { Customer, TableFilters } from '@/types';
import { customersAPI } from '@/api/customers';
import CustomerForm from '@/components/forms/CustomerForm';

const { Title } = Typography;

// Mock data based on your Excel files
// const mockCustomers: Customer[] = [
  {
    _id: '1',
    customerId: 'PATITO-000001',
    customerName: 'Industria Los Patitos, S.A.',
    sopCustomerName: 'Los Patitos',
    trimCustomerId: 'PATITO-000001',
    salesRepId: 'rep1',
    salesRepName: 'David Brace',
    location: {
      city: 'La Casona Del Cerdo',
      state: 'HR',
      address1: '175 Oeste del Rest.',
      zip: '40801',
    },
    corporateGroup: 'Food Services',
    isActive: true,
    metadata: {
      totalSalesYTD: 125000.5,
    },
    createdAt: '2025-01-01T00:00:00Z',
    updatedAt: '2025-10-15T00:00:00Z',
  },
  {
    _id: '2',
    customerId: '100PFG-000001',
    customerName: '100% Food Group',
    sopCustomerName: '100% Food',
    salesRepId: 'rep1',
    salesRepName: 'David Brace',
    location: {
      city: 'Hialeah',
      state: 'FL',
    },
    corporateGroup: 'Other Customers',
    isActive: true,
    metadata: {
      totalSalesYTD: 85000.0,
    },
    createdAt: '2025-01-01T00:00:00Z',
    updatedAt: '2025-10-15T00:00:00Z',
  },
  {
    _id: '3',
    customerId: '89IN-000001',
    customerName: '89 INTERNATIONAL INC',
    sopCustomerName: '89 International',
    salesRepId: 'rep2',
    salesRepName: 'Pedro Galavis',
    location: {
      city: 'Miami',
      state: 'FL',
    },
    corporateGroup: 'Other Customers',
    isActive: true,
    metadata: {
      totalSalesYTD: 65000.0,
    },
    createdAt: '2025-01-01T00:00:00Z',
    updatedAt: '2025-10-15T00:00:00Z',
  },
  {
    _id: '4',
    customerId: 'AAORGA-AAORGA',
    customerName: 'A&A ORGANIC FARMS CORP',
    sopCustomerName: 'A&A Organic',
    salesRepId: 'rep1',
    salesRepName: 'David Brace',
    location: {
      city: 'WATSONVILLE',
      state: 'CA',
    },
    corporateGroup: 'Other Customers',
    isActive: true,
    metadata: {
      totalSalesYTD: 120000.0,
    },
    createdAt: '2025-01-01T00:00:00Z',
    updatedAt: '2025-10-15T00:00:00Z',
  },
  {
    _id: '5',
    customerId: 'AGSF-000001',
    customerName: 'A&G Specialty Foods, LLC',
    sopCustomerName: 'A&G',
    salesRepId: 'rep1',
    salesRepName: 'David Brace',
    location: {
      city: 'Lauderdale Lakes',
      state: 'FL',
    },
    corporateGroup: 'Other Customers',
    isActive: true,
    metadata: {
      totalSalesYTD: 95000.0,
    },
    createdAt: '2025-01-01T00:00:00Z',
    updatedAt: '2025-10-15T00:00:00Z',
  },
  {
    _id: '6',
    customerId: 'CANAD-001',
    customerName: 'Canadawide',
    sopCustomerName: 'Canadawide',
    salesRepId: 'rep8',
    salesRepName: 'Jim Rodman',
    location: {
      city: 'Toronto',
      state: 'ON',
    },
    corporateGroup: 'International',
    isActive: true,
    metadata: {
      totalSalesYTD: 250000.0,
    },
    createdAt: '2025-01-01T00:00:00Z',
    updatedAt: '2025-10-15T00:00:00Z',
  },
// ];

export default function CustomerList() {
  const queryClient = useQueryClient();
  const [form] = Form.useForm();
  const [filters, setFilters] = useState<TableFilters>({
    page: 1,
    limit: 10,
    search: '',
    salesRepId: undefined,
    isActive: undefined,
  });
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingCustomer, setEditingCustomer] = useState<Customer | null>(null);

  // Fetch customers from API following integration guide
  const {
    data: customersData,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['customers', filters],
    queryFn: () => customersAPI.getAll(filters),
  });

  const customers = customersData?.customers || [];
  const total = customersData?.total || 0;

  // Mutations for CRUD operations following integration guide
  const createMutation = useMutation({
    mutationFn: customersAPI.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['customers'] });
      message.success('Customer created successfully');
      setIsModalOpen(false);
      form.resetFields();
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'Failed to create customer');
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Customer> }) =>
      customersAPI.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['customers'] });
      message.success('Customer updated successfully');
      setIsModalOpen(false);
      setEditingCustomer(null);
      form.resetFields();
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'Failed to update customer');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: customersAPI.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['customers'] });
      message.success('Customer deleted successfully');
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'Failed to delete customer');
    },
  });

  // Handle search and filter changes
  const handleSearch = (value: string) => {
    setFilters(prev => ({ ...prev, search: value, page: 1 }));
  };

  const handleSalesRepFilter = (value: string) => {
    setFilters(prev => ({ ...prev, salesRepId: value as string, page: 1 }));
  };

  // Backend handles filtering, no need for client-side filtering

  // Statistics
  const stats = {
    total: customers.length,
    active: customers.filter((c) => c.isActive).length,
    totalSales: customers.reduce((sum, c) => sum + (c.metadata?.totalSalesYTD || 0), 0),
  };

  const columns: ColumnsType<Customer> = [
    {
      title: 'Customer ID',
      dataIndex: 'customerId',
      key: 'customerId',
      width: 150,
      fixed: 'left',
      render: (text) => <span style={{ fontFamily: 'monospace', fontWeight: 500 }}>{text}</span>,
    },
    {
      title: 'Customer Name',
      dataIndex: 'customerName',
      key: 'customerName',
      width: 250,
      render: (text) => <strong>{text}</strong>,
    },
    {
      title: 'S&OP Name',
      dataIndex: 'sopCustomerName',
      key: 'sopCustomerName',
      width: 150,
    },
    {
      title: 'Sales Rep',
      dataIndex: 'salesRepName',
      key: 'salesRepName',
      width: 150,
      render: (text) => <Tag color="blue">{text}</Tag>,
    },
    {
      title: 'Location',
      key: 'location',
      width: 200,
      render: (_, record) => (
        <span>
          {record.location?.city && `${record.location.city}, `}
          {record.location?.state}
        </span>
      ),
    },
    {
      title: 'Corporate Group',
      dataIndex: 'corporateGroup',
      key: 'corporateGroup',
      width: 180,
    },
    {
      title: 'YTD Sales',
      key: 'totalSales',
      width: 120,
      align: 'right',
      render: (_, record) =>
        record.metadata?.totalSalesYTD
          ? `$${record.metadata.totalSalesYTD.toLocaleString()}`
          : '-',
    },
    {
      title: 'Status',
      dataIndex: 'isActive',
      key: 'isActive',
      width: 100,
      render: (isActive) => (
        <Tag color={isActive ? 'success' : 'default'}>{isActive ? 'Active' : 'Inactive'}</Tag>
      ),
    },
    {
      title: 'Actions',
      key: 'actions',
      fixed: 'right',
      width: 120,
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
            size="small"
          >
            Edit
          </Button>
          <Popconfirm
            title="Delete Customer"
            description="Are you sure you want to delete this customer?"
            onConfirm={() => handleDelete(record._id)}
            okText="Yes"
            cancelText="No"
          >
            <Button type="link" danger icon={<DeleteOutlined />} size="small">
              Delete
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  const handleAdd = () => {
    setEditingCustomer(null);
    form.resetFields();
    setIsModalOpen(true);
  };

  const handleEdit = (customer: Customer) => {
    setEditingCustomer(customer);
    setIsModalOpen(true);
  };

  const handleDelete = (id: string) => {
    deleteMutation.mutate(id);
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();

      if (editingCustomer) {
        // Update using API - transform data to match backend schema
        updateMutation.mutate({
          id: editingCustomer._id,
          data: {
            customerName: values.customerName,
            location: {
              city: values.city,
              state: values.state,
              address1: values.address1, // Map address1 to address1
              zipCode: values.zip, // Map zip to zipCode
              country: 'USA', // Default country
            },
            contactPerson: values.corporateGroup, // Map corporateGroup to contactPerson for now
          },
        });
      } else {
        // Create using API - transform data to match backend schema
        createMutation.mutate({
          customerId: values.customerId,
          customerName: values.customerName,
          location: {
            city: values.city,
            state: values.state,
            address1: values.address1, // Map address1 to address1
            zipCode: values.zip, // Map zip to zipCode
            country: 'USA', // Default country
          },
          contactPerson: values.corporateGroup, // Map corporateGroup to contactPerson for now
        });
      }
    } catch (error: any) {
      console.error('Form validation failed:', error);
    }
  };

  const handleImport = async (file: File) => {
    try {
      const result = await customersAPI.importExcel(file);
      message.success(`Import completed: ${result.successful} successful, ${result.failed} failed`);
      queryClient.invalidateQueries({ queryKey: ['customers'] });
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Import failed');
    }
  };

  const handleExport = async () => {
    try {
      const blob = await customersAPI.exportExcel();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `customers_${new Date().toISOString().split('T')[0]}.xlsx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      message.success('Export completed');
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Export failed');
    }
  };

  return (
    <div>
      {/* Statistics Cards */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="Total Customers"
              value={stats.total}
              prefix={<TeamOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="Active Customers"
              value={stats.active}
              suffix={`/ ${stats.total}`}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="Total YTD Sales"
              value={stats.totalSales}
              precision={0}
              prefix="$"
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Header */}
      <div style={{ marginBottom: 16 }}>
        <Title level={3} style={{ marginBottom: 16 }}>
          Customers
        </Title>

        <Space direction="vertical" style={{ width: '100%' }} size="middle">
          {/* Search and Actions */}
          <Row gutter={16}>
            <Col flex="auto">
              <Input
                placeholder="Search by customer name, ID, or sales rep..."
                prefix={<SearchOutlined />}
                value={filters.search}
                onChange={(e) => handleSearch(e.target.value)}
                size="large"
                allowClear
              />
            </Col>
            <Col>
              <Select
                placeholder="Filter by Sales Rep"
                style={{ width: 200 }}
                size="large"
                allowClear
                value={filters.salesRepId}
                onChange={handleSalesRepFilter}
                options={[
                  { label: 'David Brace', value: 'rep1' },
                  { label: 'Pedro Galavis', value: 'rep2' },
                  { label: 'Jim Rodman', value: 'rep8' },
                ]}
              />
            </Col>
          </Row>

          {/* Action Buttons */}
          <Space wrap>
            <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd} size="large">
              Add Customer
            </Button>
            <Upload beforeUpload={handleImport} showUploadList={false}>
              <Button icon={<UploadOutlined />} size="large">
                Import Excel
              </Button>
            </Upload>
            <Button icon={<DownloadOutlined />} onClick={handleExport} size="large">
              Export Excel
            </Button>
          </Space>
        </Space>
      </div>

      {/* Table */}
      <Table
        columns={columns}
        dataSource={customers}
        loading={isLoading}
        rowKey="_id"
        scroll={{ x: 1500 }}
        pagination={{
          total: total,
          pageSize: filters.limit,
          current: filters.page,
          onChange: (page, pageSize) => {
            setFilters(prev => ({ ...prev, page, limit: pageSize || 10 }));
          },
          showSizeChanger: true,
          showTotal: (total) => `Total ${total} customers`,
        }}
      />

      {/* Add/Edit Modal */}
      <Modal
        title={editingCustomer ? 'Edit Customer' : 'Add New Customer'}
        open={isModalOpen}
        onOk={handleSubmit}
        onCancel={() => {
          setIsModalOpen(false);
          form.resetFields();
        }}
        width={800}
        confirmLoading={createMutation.isPending || updateMutation.isPending}
        okText={editingCustomer ? 'Update' : 'Create'}
      >
        <CustomerForm form={form} initialValues={editingCustomer || undefined} onSubmit={async () => {}} />
      </Modal>
    </div>
  );
}
