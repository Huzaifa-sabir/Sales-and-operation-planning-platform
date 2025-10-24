import { useState, useEffect } from 'react';
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
  ShoppingOutlined,
} from '@ant-design/icons';
import type { Product, ProductFormData } from '@/types';
import ProductForm from '@/components/forms/ProductForm';
import { productsAPI } from '@/api/products';

const { Title } = Typography;

export default function ProductList() {
  const [form] = Form.useForm();
  const [products, setProducts] = useState<Product[]>([]);
  const [searchText, setSearchText] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedGroup, setSelectedGroup] = useState<string | undefined>();
  const [selectedLocation, setSelectedLocation] = useState<string | undefined>();
  const [pagination, setPagination] = useState({ page: 1, limit: 20, total: 0 });

  // Fetch products from API
  useEffect(() => {
    fetchProducts();
  }, [searchText, selectedGroup, selectedLocation, pagination.page]);

  const fetchProducts = async () => {
    try {
      setLoading(true);
      const response = await productsAPI.getAll({
        page: pagination.page,
        limit: pagination.limit,
        search: searchText || undefined,
        groupCode: selectedGroup,
        location: selectedLocation,
      });
      setProducts(response.products || []);
      setPagination(prev => ({ ...prev, total: response.total || 0 }));
    } catch (error) {
      message.error('Failed to load products');
      console.error('Error fetching products:', error);
    } finally {
      setLoading(false);
    }
  };

  // Statistics
  const stats = {
    total: pagination.total,
    active: products.filter((p) => p.isActive).length,
    groups: new Set(products.map((p) => p.group?.code).filter(Boolean)).size,
  };

  const columns: ColumnsType<Product> = [
    {
      title: 'Item Code',
      dataIndex: 'itemCode',
      key: 'itemCode',
      width: 120,
      fixed: 'left',
      render: (text) => <span style={{ fontFamily: 'monospace', fontWeight: 500 }}>{text}</span>,
    },
    {
      title: 'Description',
      dataIndex: 'itemDescription',
      key: 'itemDescription',
      width: 350,
      render: (text) => <strong>{text}</strong>,
    },
    {
      title: 'Group',
      key: 'group',
      width: 100,
      render: (_, record) => (
        record.group?.code ? <Tag color="purple">{record.group.code}</Tag> : <span>-</span>
      ),
    },
    {
      title: 'Sub-Group',
      key: 'subgroup',
      width: 120,
      render: (_, record) => record.group?.subgroup || '-',
    },
    {
      title: 'Location',
      key: 'location',
      width: 150,
      render: (_, record) => (
        record.manufacturing?.location ? <Tag color="blue">{record.manufacturing.location}</Tag> : <span>-</span>
      ),
    },
    {
      title: 'Weight',
      dataIndex: 'weight',
      key: 'weight',
      width: 100,
      align: 'right',
      render: (weight) => (weight ? `${weight} LB` : '-'),
    },
    {
      title: 'UOM',
      dataIndex: 'uom',
      key: 'uom',
      width: 80,
      align: 'center',
      render: (uom) => uom || '-',
    },
    {
      title: 'Avg Price',
      key: 'avgPrice',
      width: 120,
      align: 'right',
      render: (_, record) =>
        record.pricing?.avgPrice ? `$${record.pricing.avgPrice.toFixed(2)}` : '-',
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
            title="Delete Product"
            description="Are you sure you want to delete this product?"
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
    setEditingProduct(null);
    form.resetFields();
    setIsModalOpen(true);
  };

  const handleEdit = (product: Product) => {
    setEditingProduct(product);
    setIsModalOpen(true);
  };

  const handleDelete = async (id: string) => {
    try {
      await productsAPI.delete(id);
      message.success('Product deleted successfully');
      fetchProducts();
    } catch (error) {
      message.error('Failed to delete product');
      console.error('Error deleting product:', error);
    }
  };

  const handleSubmit = async () => {
    try {
      setLoading(true);
      const rawValues = await form.validateFields();

      // Transform flat form values to nested ProductFormData structure
      const productData: ProductFormData = {
        itemCode: rawValues.itemCode,
        itemDescription: rawValues.itemDescription,
        group: {
          code: rawValues.groupCode,
          subgroup: rawValues.groupSubgroup,
          desc: rawValues.groupDesc,
        },
        manufacturing: {
          location: rawValues.location,
          line: rawValues.line,
        },
        weight: rawValues.weight,
        uom: rawValues.uom,
        pricing: {
          avgPrice: rawValues.avgPrice || 0,
          costPrice: rawValues.costPrice,
        },
      };

      if (editingProduct) {
        // Update
        await productsAPI.update(editingProduct._id, productData);
        message.success('Product updated successfully');
      } else {
        // Create
        await productsAPI.create(productData);
        message.success('Product created successfully');
      }

      setIsModalOpen(false);
      form.resetFields();
      fetchProducts();
    } catch (error) {
      message.error('Failed to save product');
      console.error('Form submission error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleImport = async (file: File) => {
    try {
      const result = await productsAPI.importExcel(file);
      message.success(`Imported ${result.successful} products successfully`);
      fetchProducts();
      return false; // Prevent default upload
    } catch (error) {
      message.error('Failed to import Excel file');
      console.error('Error importing:', error);
      return false;
    }
  };

  const handleExport = async () => {
    try {
      const blob = await productsAPI.exportExcel();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `products-${new Date().toISOString().split('T')[0]}.xlsx`;
      link.click();
      window.URL.revokeObjectURL(url);
      message.success('Products exported successfully');
    } catch (error) {
      message.error('Failed to export products');
      console.error('Error exporting:', error);
    }
  };

  return (
    <div>
      {/* Statistics Cards */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="Total Products"
              value={stats.total}
              prefix={<ShoppingOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="Active Products"
              value={stats.active}
              suffix={`/ ${stats.total}`}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="Product Groups"
              value={stats.groups}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Header */}
      <div style={{ marginBottom: 16 }}>
        <Title level={3} style={{ marginBottom: 16 }}>
          Products
        </Title>

        <Space direction="vertical" style={{ width: '100%' }} size="middle">
          {/* Search and Filters */}
          <Row gutter={16}>
            <Col flex="auto">
              <Input
                placeholder="Search by item code or description..."
                prefix={<SearchOutlined />}
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
                size="large"
                allowClear
              />
            </Col>
            <Col>
              <Select
                placeholder="Filter by Group"
                style={{ width: 150 }}
                size="large"
                allowClear
                value={selectedGroup}
                onChange={setSelectedGroup}
                options={[
                  { label: 'G1', value: 'G1' },
                  { label: 'G2', value: 'G2' },
                  { label: 'G3', value: 'G3' },
                  { label: 'G5', value: 'G5' },
                ]}
              />
            </Col>
            <Col>
              <Select
                placeholder="Filter by Location"
                style={{ width: 150 }}
                size="large"
                allowClear
                value={selectedLocation}
                onChange={setSelectedLocation}
                options={[
                  { label: 'Miami', value: 'Miami' },
                  { label: 'New York', value: 'New York' },
                  { label: 'Los Angeles', value: 'Los Angeles' },
                ]}
              />
            </Col>
          </Row>

          {/* Action Buttons */}
          <Space wrap>
            <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd} size="large">
              Add Product
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
        dataSource={products}
        rowKey="_id"
        loading={loading}
        scroll={{ x: 1600 }}
        pagination={{
          current: pagination.page,
          pageSize: pagination.limit,
          total: pagination.total,
          showSizeChanger: true,
          showTotal: (total) => `Total ${total} products`,
          onChange: (page, pageSize) => {
            setPagination(prev => ({ ...prev, page, limit: pageSize || 20 }));
          },
        }}
      />

      {/* Add/Edit Modal */}
      <Modal
        title={editingProduct ? 'Edit Product' : 'Add New Product'}
        open={isModalOpen}
        onOk={handleSubmit}
        onCancel={() => {
          setIsModalOpen(false);
          form.resetFields();
        }}
        width={800}
        confirmLoading={loading}
        okText={editingProduct ? 'Update' : 'Create'}
      >
        <ProductForm form={form} initialValues={editingProduct || undefined} onSubmit={async () => {}} />
      </Modal>
    </div>
  );
}
