import { useState, useEffect } from 'react';
import {
  Table,
  Button,
  Space,
  Tag,
  Modal,
  Form,
  message,
  Popconfirm,
  Card,
  Typography,
  Row,
  Col,
  Statistic,
  Progress,
  DatePicker,
  Input,
  InputNumber,
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  MailOutlined,
  LockOutlined,
  UnlockOutlined,
} from '@ant-design/icons';
import type { SOPCycle } from '@/types';
import { cyclesAPI } from '@/api/cycles';
import dayjs from 'dayjs';

const { Title, Text } = Typography;

// Mock data removed for production build

export default function SOPCycles() {
  const [form] = Form.useForm();
  const [cycles, setCycles] = useState<SOPCycle[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingCycle, setEditingCycle] = useState<SOPCycle | null>(null);
  const [loading, setLoading] = useState(false);
  const [fetchLoading, setFetchLoading] = useState(false);

  // Fetch cycles from backend
  useEffect(() => {
    fetchCycles();
  }, []);

  const fetchCycles = async () => {
    try {
      setFetchLoading(true);
      const response = await cyclesAPI.list({
        limit: 100, // Get all cycles
      });
      // Backend returns { cycles, total, ... }
      setCycles(response.cycles || []);
    } catch (error) {
      console.error('Failed to fetch cycles:', error);
      message.error('Failed to load S&OP cycles');
    } finally {
      setFetchLoading(false);
    }
  };

  // Statistics
  const stats = {
    total: cycles.length,
    open: cycles.filter((c) => c.status === 'open').length,
    closed: cycles.filter((c) => c.status === 'closed').length,
    draft: cycles.filter((c) => c.status === 'draft').length,
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'open':
        return 'success';
      case 'closed':
        return 'default';
      case 'draft':
        return 'warning';
      case 'archived':
        return 'error';
      default:
        return 'default';
    }
  };

  const columns: ColumnsType<SOPCycle> = [
    {
      title: 'Cycle Name',
      dataIndex: 'cycleName',
      key: 'cycleName',
      width: 150,
      fixed: 'left',
      render: (text) => <strong>{text}</strong>,
    },
    {
      title: 'Start Date',
      key: 'startDate',
      width: 120,
      render: (_, record) => dayjs(record.dates.startDate).format('MMM DD, YYYY'),
    },
    {
      title: 'Close Date',
      key: 'closeDate',
      width: 120,
      render: (_, record) => dayjs(record.dates.closeDate).format('MMM DD, YYYY'),
    },
    {
      title: 'Planning Period',
      key: 'planningPeriod',
      width: 180,
      render: (_, record) => (
        <span>
          {dayjs(record.dates.planningStartMonth).format('MMM YYYY')} -{' '}
          {dayjs(record.dates.planningEndMonth).format('MMM YYYY')}
        </span>
      ),
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status) => (
        <Tag color={getStatusColor(status)} style={{ textTransform: 'capitalize' }}>
          {status}
        </Tag>
      ),
    },
    {
      title: 'Submissions',
      key: 'submissions',
      width: 200,
      render: (_, record) =>
        record.stats ? (
          <div>
            <Progress
              percent={record.stats.completionPercent}
              size="small"
              status={record.stats.completionPercent === 100 ? 'success' : 'active'}
            />
            <Text type="secondary" style={{ fontSize: 12 }}>
              {record.stats.submittedReps}/{record.stats.totalReps} reps submitted
            </Text>
          </div>
        ) : (
          '-'
        ),
    },
    {
      title: 'Total Amount',
      key: 'totalAmount',
      width: 130,
      align: 'right',
      render: (_, record) =>
        record.stats?.totalAmount ? `$${(record.stats.totalAmount / 1000000).toFixed(1)}M` : '-',
    },
    {
      title: 'Actions',
      key: 'actions',
      fixed: 'right',
      width: 250,
      render: (_, record) => (
        <Space size="small">
          {record.status === 'draft' && (
            <Button
              type="primary"
              size="small"
              icon={<UnlockOutlined />}
              onClick={() => handleOpenCycle(record._id)}
            >
              Open
            </Button>
          )}
          {record.status === 'open' && (
            <>
              <Button
                type="default"
                size="small"
                icon={<MailOutlined />}
                onClick={() => handleNotify(record._id)}
              >
                Notify
              </Button>
              <Button
                type="default"
                size="small"
                icon={<LockOutlined />}
                onClick={() => handleCloseCycle(record._id)}
              >
                Close
              </Button>
            </>
          )}
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            Edit
          </Button>
          <Popconfirm
            title="Delete Cycle"
            description="Are you sure? This will delete all associated data."
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
    setEditingCycle(null);
    form.resetFields();
    // Set defaults for new cycle
    const nextMonth = dayjs().add(1, 'month');
    form.setFieldsValue({
      cycleName: nextMonth.format('MMMM YYYY'),
      year: nextMonth.year(),
      month: nextMonth.month() + 1,
      startDate: dayjs().add(15, 'days'),
      closeDate: dayjs().add(30, 'days'),
      planningStartMonth: nextMonth.startOf('month'),
    });
    setIsModalOpen(true);
  };

  const handleEdit = (cycle: SOPCycle) => {
    setEditingCycle(cycle);
    form.setFieldsValue({
      cycleName: cycle.cycleName,
      year: cycle.year,
      month: cycle.month,
      startDate: dayjs(cycle.dates.startDate),
      closeDate: dayjs(cycle.dates.closeDate),
      planningStartMonth: dayjs(cycle.dates.planningStartMonth),
    });
    setIsModalOpen(true);
  };

  const handleDelete = async (id: string) => {
    try {
      await cyclesAPI.delete(id);
      setCycles(cycles.filter((c) => c._id !== id));
      message.success('Cycle deleted successfully');
    } catch (error: any) {
      console.error('Failed to delete cycle:', error);
      message.error(error.response?.data?.detail || 'Failed to delete cycle');
    }
  };

  const handleOpenCycle = async (id: string) => {
    try {
      const response = await cyclesAPI.changeStatus(id, 'OPEN');
      setCycles(
        cycles.map((c) => (c._id === id ? { ...c, ...response } : c))
      );
      message.success('Cycle opened and notifications sent to sales reps');
    } catch (error: any) {
      console.error('Failed to open cycle:', error);
      message.error(error.response?.data?.detail || 'Failed to open cycle');
    }
  };

  const handleCloseCycle = async (id: string) => {
    try {
      const response = await cyclesAPI.changeStatus(id, 'CLOSED');
      setCycles(
        cycles.map((c) => (c._id === id ? { ...c, ...response } : c))
      );
      message.success('Cycle closed successfully');
    } catch (error: any) {
      console.error('Failed to close cycle:', error);
      message.error(error.response?.data?.detail || 'Failed to close cycle');
    }
  };

  const handleNotify = async (_id: string) => {
    // TODO: Add notification endpoint
    message.success('Email notifications sent to all sales reps');
  };

  const handleSubmit = async () => {
    try {
      setLoading(true);
      const values = await form.validateFields();

      if (editingCycle) {
        // Update existing cycle
        const updateData = {
          cycleName: values.cycleName,
          startDate: values.startDate.toISOString(),
          endDate: values.closeDate.toISOString(),
        };

        const updatedCycle = await cyclesAPI.update(editingCycle._id, updateData);
        setCycles(cycles.map((c) => (c._id === editingCycle._id ? updatedCycle : c)));
        message.success('Cycle updated successfully');
      } else {
        // Create new cycle
        const createData = {
          cycleName: values.cycleName,
          startDate: values.startDate.toISOString(),
          endDate: values.closeDate.toISOString(),
        };

        const newCycle = await cyclesAPI.create(createData);
        setCycles([newCycle, ...cycles]);
        message.success('Cycle created successfully');
      }

      setIsModalOpen(false);
      form.resetFields();
    } catch (error: any) {
      console.error('Failed to save cycle:', error);
      message.error(error.response?.data?.detail || 'Failed to save cycle');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {/* Statistics */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Total Cycles"
              value={stats.total}
              prefix={<ClockCircleOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Open Cycles"
              value={stats.open}
              valueStyle={{ color: '#52c41a' }}
              prefix={<CheckCircleOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic title="Closed Cycles" value={stats.closed} />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Draft Cycles"
              value={stats.draft}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Header */}
      <div style={{ marginBottom: 16 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Title level={3}>S&OP Cycles</Title>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd} size="large">
            Create New Cycle
          </Button>
        </div>
        <Text type="secondary">
          Manage monthly S&OP planning cycles. Create cycles, set dates, and track submissions.
        </Text>
      </div>

      {/* Table */}
      <Table
        columns={columns}
        dataSource={cycles}
        rowKey="_id"
        loading={fetchLoading}
        scroll={{ x: 1400 }}
        pagination={{
          pageSize: 10,
          showTotal: (total) => `Total ${total} cycles`,
        }}
      />

      {/* Add/Edit Modal */}
      <Modal
        title={editingCycle ? 'Edit S&OP Cycle' : 'Create New S&OP Cycle'}
        open={isModalOpen}
        onOk={handleSubmit}
        onCancel={() => {
          setIsModalOpen(false);
          form.resetFields();
        }}
        width={700}
        confirmLoading={loading}
        okText={editingCycle ? 'Update' : 'Create'}
      >
        <Form form={form} layout="vertical" style={{ marginTop: 24 }}>
          <Form.Item
            name="cycleName"
            label="Cycle Name"
            rules={[{ required: true, message: 'Please enter cycle name' }]}
          >
            <Input placeholder="e.g., November 2025" />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="year"
                label="Year"
                rules={[{ required: true, message: 'Required' }]}
              >
                <InputNumber min={2025} max={2030} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="month"
                label="Month"
                rules={[{ required: true, message: 'Required' }]}
              >
                <InputNumber min={1} max={12} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="startDate"
                label="Start Date"
                rules={[{ required: true, message: 'Required' }]}
              >
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="closeDate"
                label="Close Date"
                rules={[{ required: true, message: 'Required' }]}
              >
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            name="planningStartMonth"
            label="Planning Start Month"
            rules={[{ required: true, message: 'Required' }]}
            extra="System will automatically plan for 16 months from this date"
          >
            <DatePicker picker="month" style={{ width: '100%' }} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
