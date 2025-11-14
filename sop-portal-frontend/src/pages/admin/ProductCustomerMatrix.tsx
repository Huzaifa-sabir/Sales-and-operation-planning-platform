import { useState, useEffect } from 'react';
import { Card, Typography, Table, Button, Space, message, Input, Checkbox, Select, Tag, Spin, Divider } from 'antd';
import { SearchOutlined, SaveOutlined, CheckOutlined, CloseOutlined } from '@ant-design/icons';
import { customersAPI } from '@/api/customers';
import { productsAPI } from '@/api/products';
import { matrixAPI, type ProductCustomerMatrix } from '@/api/matrix';
import type { Customer, Product } from '@/types';

const { Title, Text } = Typography;

export default function ProductCustomerMatrix() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [selectedCustomerId, setSelectedCustomerId] = useState<string | null>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const [matrixEntries, setMatrixEntries] = useState<ProductCustomerMatrix[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingProducts, setLoadingProducts] = useState(false);
  const [saving, setSaving] = useState(false);
  const [searchCustomer, setSearchCustomer] = useState('');
  const [searchProduct, setSearchProduct] = useState('');

  useEffect(() => {
    loadCustomers();
    loadProducts();
  }, []);

  useEffect(() => {
    if (selectedCustomerId) {
      loadMatrixForCustomer();
    } else {
      setMatrixEntries([]);
    }
  }, [selectedCustomerId]);

  const loadCustomers = async () => {
    try {
      setLoading(true);
      const result = await customersAPI.getAll({ page: 1, limit: 1000 });
      setCustomers(result.customers || []);
    } catch (e) {
      console.error('Failed to load customers:', e);
      message.error('Failed to load customers');
    } finally {
      setLoading(false);
    }
  };

  const loadProducts = async () => {
    try {
      setLoadingProducts(true);
      const result = await productsAPI.getAll({ page: 1, limit: 10000 });
      setProducts(result.products || []);
    } catch (e) {
      console.error('Failed to load products:', e);
      message.error('Failed to load products');
    } finally {
      setLoadingProducts(false);
    }
  };

  const loadMatrixForCustomer = async () => {
    if (!selectedCustomerId) return;
    try {
      setLoading(true);
      const entries = await matrixAPI.getByCustomer(selectedCustomerId);
      setMatrixEntries(entries);
    } catch (e) {
      console.error('Failed to load matrix:', e);
      message.error('Failed to load product-customer matrix');
    } finally {
      setLoading(false);
    }
  };

  const filteredCustomers = customers.filter(c =>
    c.customerName.toLowerCase().includes(searchCustomer.toLowerCase()) ||
    c.customerId.toLowerCase().includes(searchCustomer.toLowerCase())
  );

  const filteredProducts = products.filter(p =>
    p.itemDescription.toLowerCase().includes(searchProduct.toLowerCase()) ||
    p.itemCode.toLowerCase().includes(searchProduct.toLowerCase())
  );

  const isProductActive = (productId: string): boolean => {
    const entry = matrixEntries.find(e => e.productId === productId);
    return entry?.isActive || false;
  };

  const getMatrixEntryId = (productId: string): string | null => {
    const entry = matrixEntries.find(e => e.productId === productId);
    return entry?._id || null;
  };

  const toggleProduct = async (productId: string) => {
    const entryId = getMatrixEntryId(productId);
    const product = products.find(p => p.itemCode === productId);
    const customer = customers.find(c => c.customerId === selectedCustomerId);
    
    if (!customer || !product) return;

    try {
      if (entryId) {
        // Update existing entry
        await matrixAPI.update(entryId, { isActive: !isProductActive(productId) });
        message.success(`Product ${isProductActive(productId) ? 'deactivated' : 'activated'}`);
      } else {
        // Create new entry
        await matrixAPI.create({
          customerId: selectedCustomerId!,
          productId: productId,
        });
        message.success('Product activated');
      }
      await loadMatrixForCustomer();
    } catch (e: any) {
      message.error(e?.response?.data?.detail || 'Failed to update product');
    }
  };

  const activateAll = async () => {
    if (!selectedCustomerId) return;
    const customer = customers.find(c => c.customerId === selectedCustomerId);
    if (!customer) return;

    try {
      setSaving(true);
      const inactiveProducts = filteredProducts.filter(p => !isProductActive(p.itemCode));
      
      const entries = inactiveProducts.map(product => ({
        customerId: selectedCustomerId,
        productId: product.itemCode,
      }));

      if (entries.length > 0) {
        await matrixAPI.bulkCreate(entries);
        message.success(`Activated ${entries.length} products`);
        await loadMatrixForCustomer();
      } else {
        message.info('All products are already active');
      }
    } catch (e: any) {
      message.error(e?.response?.data?.detail || 'Failed to activate products');
    } finally {
      setSaving(false);
    }
  };

  const deactivateAll = async () => {
    if (!selectedCustomerId) return;

    try {
      setSaving(true);
      const activeEntries = matrixEntries.filter(e => e.isActive);
      
      for (const entry of activeEntries) {
        await matrixAPI.update(entry._id, { isActive: false });
      }

      if (activeEntries.length > 0) {
        message.success(`Deactivated ${activeEntries.length} products`);
        await loadMatrixForCustomer();
      } else {
        message.info('No active products to deactivate');
      }
    } catch (e: any) {
      message.error(e?.response?.data?.detail || 'Failed to deactivate products');
    } finally {
      setSaving(false);
    }
  };

  const selectedCustomer = customers.find(c => c.customerId === selectedCustomerId);

  const columns = [
    {
      title: 'Active',
      dataIndex: 'isActive',
      width: 80,
      render: (_: any, record: Product) => (
        <Checkbox
          checked={isProductActive(record.itemCode)}
          onChange={() => toggleProduct(record.itemCode)}
          disabled={!selectedCustomerId || saving}
        />
      ),
    },
    {
      title: 'Product Code',
      dataIndex: 'itemCode',
      width: 120,
    },
    {
      title: 'Product Description',
      dataIndex: 'itemDescription',
      width: 400,
    },
    {
      title: 'Group',
      dataIndex: 'group',
      width: 150,
      render: (group: any) => group?.code || '-',
    },
    {
      title: 'Status',
      dataIndex: 'status',
      width: 100,
      render: (_: any, record: Product) => {
        const active = isProductActive(record.itemCode);
        return <Tag color={active ? 'green' : 'default'}>{active ? 'Active' : 'Inactive'}</Tag>;
      },
    },
  ];

  return (
    <div>
      <Title level={2}>Product-Customer Matrix Management</Title>
      <Text type="secondary">Manage which products are active for each customer</Text>

      <Card style={{ marginTop: 24 }}>
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <div>
            <Text strong>Select Customer:</Text>
            <Select
              style={{ width: 400, marginLeft: 8 }}
              placeholder="Select a customer"
              showSearch
              value={selectedCustomerId}
              onChange={setSelectedCustomerId}
              loading={loading}
              optionFilterProp="children"
              filterOption={(input, option) =>
                (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
              }
              options={filteredCustomers.map(c => ({
                value: c.customerId,
                label: `${c.customerName} (${c.customerId})`
              }))}
            />
            <Input
              style={{ width: 300, marginLeft: 8 }}
              placeholder="Search customers..."
              prefix={<SearchOutlined />}
              value={searchCustomer}
              onChange={(e) => setSearchCustomer(e.target.value)}
            />
          </div>

          {selectedCustomerId && selectedCustomer && (
            <>
              <Divider />
              <div>
                <Space>
                  <Text strong>Customer: </Text>
                  <Text>{selectedCustomer.customerName}</Text>
                  <Text type="secondary">
                    ({matrixEntries.filter(e => e.isActive).length} active products)
                  </Text>
                </Space>
              </div>

              <div>
                <Space>
                  <Input
                    style={{ width: 400 }}
                    placeholder="Search products..."
                    prefix={<SearchOutlined />}
                    value={searchProduct}
                    onChange={(e) => setSearchProduct(e.target.value)}
                  />
                  <Button
                    type="primary"
                    icon={<CheckOutlined />}
                    onClick={activateAll}
                    disabled={saving}
                    loading={saving}
                  >
                    Activate All
                  </Button>
                  <Button
                    danger
                    icon={<CloseOutlined />}
                    onClick={deactivateAll}
                    disabled={saving}
                    loading={saving}
                  >
                    Deactivate All
                  </Button>
                </Space>
              </div>

              <Table
                columns={columns}
                dataSource={filteredProducts}
                rowKey="itemCode"
                loading={loadingProducts}
                pagination={{ pageSize: 50 }}
                scroll={{ y: 600 }}
                size="small"
              />
            </>
          )}

          {!selectedCustomerId && (
            <div style={{ textAlign: 'center', padding: 40 }}>
              <Text type="secondary">Please select a customer to manage products</Text>
            </div>
          )}
        </Space>
      </Card>
    </div>
  );
}

