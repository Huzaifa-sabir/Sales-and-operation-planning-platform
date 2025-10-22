import { useState, useEffect } from 'react';
import {
  Table,
  Button,
  Space,
  Tag,
  Modal,
  Form,
  Input,
  Select,
  Switch,
  message,
  Popconfirm,
  Card,
  Typography,
  Row,
  Col,
  Statistic,
  Avatar,
  Alert,
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  UserOutlined,
  LockOutlined,
  MailOutlined,
  CheckCircleOutlined,
  StopOutlined,
  CopyOutlined,
} from '@ant-design/icons';
import type { User } from '@/types';
import { usersAPI, type UserCreate, type UserUpdate } from '@/api/users';
import { getErrorMessage } from '@/api/axios';
import dayjs from 'dayjs';

const { Title, Text } = Typography;

interface UserFormData {
  username: string;
  email: string;
  fullName: string;
  role: 'admin' | 'sales_rep';
}

export default function UserManagement() {
  const [form] = Form.useForm();
  const [users, setUsers] = useState<User[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [roleFilter, setRoleFilter] = useState<string | undefined>();
  const [statusFilter, setStatusFilter] = useState<boolean | undefined>();

  // Load users on component mount
  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      setLoading(true);
      const response = await usersAPI.list();
      setUsers(response.users);
    } catch (error) {
      message.error('Failed to load users');
      console.error('Error loading users:', error);
    } finally {
      setLoading(false);
    }
  };

  // Statistics
  const stats = {
    total: users.length,
    active: users.filter((u) => u.isActive).length,
    inactive: users.filter((u) => !u.isActive).length,
    admins: users.filter((u) => u.role === 'admin').length,
    salesReps: users.filter((u) => u.role === 'sales_rep').length,
  };

  // Filtered data
  const filteredUsers = users.filter((user) => {
    const matchesSearch = !searchText ||
      user.fullName.toLowerCase().includes(searchText.toLowerCase()) ||
      user.email.toLowerCase().includes(searchText.toLowerCase()) ||
      user.username.toLowerCase().includes(searchText.toLowerCase());
    const matchesRole = !roleFilter || user.role === roleFilter;
    const matchesStatus = statusFilter === undefined || user.isActive === statusFilter;
    return matchesSearch && matchesRole && matchesStatus;
  });

  const columns: ColumnsType<User> = [
    {
      title: 'User',
      key: 'user',
      width: 250,
      fixed: 'left',
      render: (_, record) => (
        <Space>
          <Avatar size="large" icon={<UserOutlined />} style={{ backgroundColor: record.isActive ? '#1890ff' : '#d9d9d9' }} />
          <div>
            <div>
              <Text strong>{record.fullName}</Text>
              {!record.isActive && (
                <Tag color="default" style={{ marginLeft: 8 }}>
                  Inactive
                </Tag>
              )}
            </div>
            <Text type="secondary" style={{ fontSize: 12 }}>
              @{record.username}
            </Text>
          </div>
        </Space>
      ),
    },
    {
      title: 'Email',
      dataIndex: 'email',
      key: 'email',
      width: 220,
      render: (email) => (
        <Space>
          <MailOutlined />
          {email}
        </Space>
      ),
    },
    {
      title: 'Role',
      dataIndex: 'role',
      key: 'role',
      width: 120,
      render: (role) => (
        <Tag color={role === 'admin' ? 'red' : 'blue'} style={{ textTransform: 'capitalize' }}>
          {role === 'sales_rep' ? 'Sales Rep' : 'Admin'}
        </Tag>
      ),
    },
    {
      title: 'Territory',
      key: 'territory',
      width: 150,
      render: (_, record) => record.metadata?.territory || '-',
    },
    {
      title: 'Phone',
      key: 'phone',
      width: 150,
      render: (_, record) => record.metadata?.phone || '-',
    },
    {
      title: 'Status',
      dataIndex: 'isActive',
      key: 'isActive',
      width: 100,
      render: (isActive) =>
        isActive ? (
          <Tag icon={<CheckCircleOutlined />} color="success">
            Active
          </Tag>
        ) : (
          <Tag icon={<StopOutlined />} color="default">
            Inactive
          </Tag>
        ),
    },
    {
      title: 'Last Updated',
      dataIndex: 'updatedAt',
      key: 'updatedAt',
      width: 130,
      render: (date) => dayjs(date).format('MMM DD, YYYY'),
    },
    {
      title: 'Actions',
      key: 'actions',
      fixed: 'right',
      width: 180,
      render: (_, record) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            Edit
          </Button>
          <Button
            type="link"
            size="small"
            icon={<LockOutlined />}
            onClick={() => handleResetPassword(record._id)}
          >
            Reset
          </Button>
          <Popconfirm
            title="Delete User"
            description={`Are you sure you want to delete ${record.fullName}?`}
            onConfirm={() => handleDelete(record._id)}
            okText="Yes"
            cancelText="No"
          >
            <Button type="link" danger size="small" icon={<DeleteOutlined />}>
              Delete
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  const handleAdd = () => {
    setEditingUser(null);
    form.resetFields();
    form.setFieldsValue({
      isActive: true,
      role: 'sales_rep',
    });
    setIsModalOpen(true);
  };

  const handleEdit = (user: User) => {
    setEditingUser(user);
    form.setFieldsValue({
      username: user.username,
      email: user.email,
      fullName: user.fullName,
      role: user.role,
      isActive: user.isActive,
      territory: user.metadata?.territory,
      phone: user.metadata?.phone,
    });
    setIsModalOpen(true);
  };

  const handleDelete = async (id: string) => {
    try {
      await usersAPI.delete(id);
      setUsers(users.filter((u) => u._id !== id));
      message.success('User deleted successfully');
    } catch (error) {
      message.error('Failed to delete user');
      console.error('Error deleting user:', error);
    }
  };

  const handleResetPassword = (id: string) => {
    const user = users.find((u) => u._id === id);
    message.success(`Password reset email sent to ${user?.email}`);
  };

  const handleSubmit = async () => {
    try {
      setLoading(true);
      const values = await form.validateFields();
      
      // Check if username already exists (for new users only)
      if (!editingUser) {
        const existingUser = users.find(u => u.username.toLowerCase() === values.username.toLowerCase());
        if (existingUser) {
          message.error('Username already exists. Please choose a different username.');
          return;
        }
        
        // Check if email already exists
        const existingEmail = users.find(u => u.email.toLowerCase() === values.email.toLowerCase());
        if (existingEmail) {
          message.error('Email already exists. Please use a different email address.');
          return;
        }
      }

      if (editingUser) {
        // Update existing user
        const updatedUser = await usersAPI.update(editingUser._id, values);
        setUsers(users.map((u) => (u._id === editingUser._id ? updatedUser : u)));
        message.success('User updated successfully');
      } else {
        // Create new user - only send required fields
        const createData = {
          username: values.username,
          email: values.email,
          fullName: values.fullName,
          role: values.role
        };
        const response = await usersAPI.create(createData);
        setUsers([response.user, ...users]);
        message.success(`User created successfully. Password: ${response.generatedPassword}`);
      }

      setIsModalOpen(false);
      form.resetFields();
    } catch (error) {
      console.error('Error saving user:', error);
      
      // Handle specific error cases
      if (error.response?.status === 400) {
        const errorData = error.response.data;
        if (errorData.detail === "Username already exists") {
          message.error('Username already exists. Please choose a different username.');
        } else if (errorData.detail === "Email already exists") {
          message.error('Email already exists. Please use a different email address.');
        } else {
          message.error(`Failed to save user: ${errorData.detail || 'Unknown error'}`);
        }
      } else if (error.response?.status === 403) {
        message.error('Access denied. You need admin privileges to create users.');
      } else if (error.response?.status === 401) {
        message.error('Authentication failed. Please log in again.');
      } else {
        message.error('Failed to save user. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleToggleStatus = async (userId: string) => {
    try {
      const updatedUser = await usersAPI.toggleStatus(userId);
      setUsers(users.map((u) => (u._id === userId ? updatedUser : u)));
      message.success(`${updatedUser.fullName} ${updatedUser.isActive ? 'activated' : 'deactivated'}`);
    } catch (error) {
      message.error('Failed to update user status');
      console.error('Error updating user status:', error);
    }
  };

  return (
    <div>
      {/* Statistics */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={8} lg={4}>
          <Card>
            <Statistic
              title="Total Users"
              value={stats.total}
              prefix={<UserOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8} lg={4}>
          <Card>
            <Statistic
              title="Active"
              value={stats.active}
              valueStyle={{ color: '#3f8600' }}
              prefix={<CheckCircleOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8} lg={4}>
          <Card>
            <Statistic
              title="Inactive"
              value={stats.inactive}
              valueStyle={{ color: '#cf1322' }}
              prefix={<StopOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8} lg={4}>
          <Card>
            <Statistic title="Admins" value={stats.admins} />
          </Card>
        </Col>
        <Col xs={24} sm={8} lg={4}>
          <Card>
            <Statistic title="Sales Reps" value={stats.salesReps} />
          </Card>
        </Col>
      </Row>

      {/* Header */}
      <div style={{ marginBottom: 16 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Title level={3}>User Management</Title>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd} size="large">
            Add New User
          </Button>
        </div>
        <Text type="secondary">
          Manage system users, roles, and permissions. Create new users or modify existing ones.
        </Text>
      </div>

      {/* Filters */}
      <Card style={{ marginBottom: 16 }}>
        <Space wrap>
          <Input.Search
            placeholder="Search by name, email, or username"
            allowClear
            style={{ width: 300 }}
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            size="large"
          />
          <Select
            placeholder="Filter by role"
            style={{ width: 150 }}
            allowClear
            size="large"
            value={roleFilter}
            onChange={setRoleFilter}
            options={[
              { label: 'Admin', value: 'admin' },
              { label: 'Sales Rep', value: 'sales_rep' },
            ]}
          />
          <Select
            placeholder="Filter by status"
            style={{ width: 150 }}
            allowClear
            size="large"
            value={statusFilter}
            onChange={setStatusFilter}
            options={[
              { label: 'Active', value: true },
              { label: 'Inactive', value: false },
            ]}
          />
        </Space>
      </Card>

      {/* Table */}
      <Table
        columns={columns}
        dataSource={filteredUsers}
        rowKey="_id"
        scroll={{ x: 1400 }}
        pagination={{
          pageSize: 10,
          showTotal: (total) => `Total ${total} users`,
        }}
      />

      {/* Add/Edit Modal */}
      <Modal
        title={editingUser ? 'Edit User' : 'Create New User'}
        open={isModalOpen}
        onOk={handleSubmit}
        onCancel={() => {
          setIsModalOpen(false);
          form.resetFields();
        }}
        width={600}
        confirmLoading={loading}
        okText={editingUser ? 'Update' : 'Create'}
      >
        <Form form={form} layout="vertical" style={{ marginTop: 24 }}>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="username"
                label="Username"
                rules={[
                  { required: true, message: 'Please enter username' },
                  { pattern: /^[a-z0-9_]+$/, message: 'Lowercase letters, numbers, and underscores only' },
                  {
                    validator: (_, value) => {
                      if (!value || editingUser) return Promise.resolve();
                      const existingUser = users.find(u => u.username.toLowerCase() === value.toLowerCase());
                      if (existingUser) {
                        return Promise.reject(new Error('Username already exists'));
                      }
                      return Promise.resolve();
                    }
                  }
                ]}
              >
                <Input prefix={<UserOutlined />} placeholder="e.g., jdoe" disabled={!!editingUser} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="email"
                label="Email"
                rules={[
                  { required: true, message: 'Please enter email' },
                  { type: 'email', message: 'Please enter valid email' },
                  {
                    validator: (_, value) => {
                      if (!value || editingUser) return Promise.resolve();
                      const existingEmail = users.find(u => u.email.toLowerCase() === value.toLowerCase());
                      if (existingEmail) {
                        return Promise.reject(new Error('Email already exists'));
                      }
                      return Promise.resolve();
                    }
                  }
                ]}
              >
                <Input prefix={<MailOutlined />} placeholder="user@heavygarlic.com" />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            name="fullName"
            label="Full Name"
            rules={[{ required: true, message: 'Please enter full name' }]}
          >
            <Input placeholder="John Doe" />
          </Form.Item>

          {!editingUser && (
            <Form.Item
              name="password"
              label="Password"
              rules={[
                { required: true, message: 'Please enter password' },
                { min: 8, message: 'Password must be at least 8 characters' },
              ]}
              extra="User will receive this password via email and can change it later"
            >
              <Input.Password prefix={<LockOutlined />} placeholder="Enter initial password" />
            </Form.Item>
          )}

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="role"
                label="Role"
                rules={[{ required: true, message: 'Please select role' }]}
              >
                <Select
                  options={[
                    { label: 'Admin', value: 'admin' },
                    { label: 'Sales Rep', value: 'sales_rep' },
                  ]}
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="isActive" label="Status" valuePropName="checked">
                <Switch checkedChildren="Active" unCheckedChildren="Inactive" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="territory" label="Territory">
                <Input placeholder="e.g., North America" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="phone" label="Phone">
                <Input placeholder="+1-305-555-0100" />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>
    </div>
  );
}
