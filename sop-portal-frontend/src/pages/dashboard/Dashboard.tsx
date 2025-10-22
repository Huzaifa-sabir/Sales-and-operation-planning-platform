import { Card, Row, Col, Statistic, Typography, Space, Alert } from 'antd';
import {
  TeamOutlined,
  ShoppingOutlined,
  UserOutlined,
  CalendarOutlined,
  RiseOutlined,
  DollarOutlined,
} from '@ant-design/icons';
import { useAuthStore } from '@/store/authStore';
import { ROLES } from '@/config/constants';

const { Title, Text } = Typography;

export default function Dashboard() {
  const { user } = useAuthStore();
  const isAdmin = user?.role === ROLES.ADMIN;

  return (
    <div>
      {/* Welcome Section */}
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <div>
          <Title level={2} style={{ marginBottom: 8 }}>
            Welcome back, {user?.fullName}!
          </Title>
          <Text type="secondary">
            {isAdmin
              ? 'Monitor S&OP cycles and team performance'
              : 'Track your forecasts and customer sales'}
          </Text>
        </div>

        {/* MVP Notice */}
        <Alert
          message="MVP Version - Limited Features"
          description="This is the MVP (Minimum Viable Product) version. Full features will be available in the next release. Currently working on backend integration."
          type="info"
          showIcon
          closable
        />

        {/* Statistics Cards */}
        {isAdmin ? (
          <>
            <Title level={4}>Overview</Title>
            <Row gutter={[16, 16]}>
              <Col xs={24} sm={12} lg={6}>
                <Card>
                  <Statistic
                    title="Total Customers"
                    value={150}
                    prefix={<TeamOutlined />}
                    valueStyle={{ color: '#3f8600' }}
                  />
                </Card>
              </Col>
              <Col xs={24} sm={12} lg={6}>
                <Card>
                  <Statistic
                    title="Total Products"
                    value={500}
                    prefix={<ShoppingOutlined />}
                    valueStyle={{ color: '#1890ff' }}
                  />
                </Card>
              </Col>
              <Col xs={24} sm={12} lg={6}>
                <Card>
                  <Statistic
                    title="Active Users"
                    value={12}
                    prefix={<UserOutlined />}
                    valueStyle={{ color: '#722ed1' }}
                  />
                </Card>
              </Col>
              <Col xs={24} sm={12} lg={6}>
                <Card>
                  <Statistic
                    title="Active Cycles"
                    value={1}
                    prefix={<CalendarOutlined />}
                    valueStyle={{ color: '#fa8c16' }}
                  />
                </Card>
              </Col>
            </Row>

            <Title level={4} style={{ marginTop: 24 }}>
              Current S&OP Cycle
            </Title>
            <Card>
              <Space direction="vertical" style={{ width: '100%' }}>
                <div>
                  <Text strong style={{ fontSize: 16 }}>
                    November 2025 Cycle
                  </Text>
                  <br />
                  <Text type="secondary">Status: Open</Text>
                </div>
                <Row gutter={16}>
                  <Col span={8}>
                    <Text type="secondary">Start Date:</Text>
                    <br />
                    <Text strong>Oct 15, 2025</Text>
                  </Col>
                  <Col span={8}>
                    <Text type="secondary">Close Date:</Text>
                    <br />
                    <Text strong>Oct 30, 2025</Text>
                  </Col>
                  <Col span={8}>
                    <Text type="secondary">Completion:</Text>
                    <br />
                    <Text strong style={{ color: '#52c41a' }}>
                      80% (8/10 reps)
                    </Text>
                  </Col>
                </Row>
              </Space>
            </Card>
          </>
        ) : (
          <>
            <Title level={4}>My Performance</Title>
            <Row gutter={[16, 16]}>
              <Col xs={24} sm={12} lg={8}>
                <Card>
                  <Statistic
                    title="My Customers"
                    value={25}
                    prefix={<TeamOutlined />}
                    suffix="active"
                  />
                </Card>
              </Col>
              <Col xs={24} sm={12} lg={8}>
                <Card>
                  <Statistic
                    title="YTD Sales"
                    value={2450000}
                    prefix={<DollarOutlined />}
                    precision={0}
                    valueStyle={{ color: '#3f8600' }}
                  />
                </Card>
              </Col>
              <Col xs={24} sm={12} lg={8}>
                <Card>
                  <Statistic
                    title="Growth"
                    value={12.5}
                    prefix={<RiseOutlined />}
                    suffix="%"
                    valueStyle={{ color: '#cf1322' }}
                  />
                </Card>
              </Col>
            </Row>

            <Title level={4} style={{ marginTop: 24 }}>
              Current S&OP Cycle
            </Title>
            <Card>
              <Space direction="vertical" style={{ width: '100%' }}>
                <div>
                  <Text strong style={{ fontSize: 16 }}>
                    November 2025 Cycle
                  </Text>
                  <br />
                  <Text type="secondary">Due Date: Oct 30, 2025</Text>
                </div>
                <Alert
                  message="Action Required"
                  description="Please submit your forecast for November 2025 cycle by October 30th."
                  type="warning"
                  showIcon
                  action={
                    <a href="/sop/forecast">
                      <Text strong style={{ color: '#fa8c16' }}>
                        Enter Forecast →
                      </Text>
                    </a>
                  }
                />
              </Space>
            </Card>
          </>
        )}

        {/* Quick Links */}
        <Title level={4}>Quick Actions</Title>
        <Row gutter={[16, 16]}>
          {isAdmin ? (
            <>
              <Col xs={24} sm={12} lg={8}>
                <Card hoverable onClick={() => (window.location.href = '/sop/cycles')}>
                  <Space>
                    <CalendarOutlined style={{ fontSize: 24, color: '#1890ff' }} />
                    <div>
                      <Text strong>Manage S&OP Cycles</Text>
                      <br />
                      <Text type="secondary">Create and manage planning cycles</Text>
                    </div>
                  </Space>
                </Card>
              </Col>
              <Col xs={24} sm={12} lg={8}>
                <Card hoverable onClick={() => (window.location.href = '/customers')}>
                  <Space>
                    <TeamOutlined style={{ fontSize: 24, color: '#52c41a' }} />
                    <div>
                      <Text strong>Manage Customers</Text>
                      <br />
                      <Text type="secondary">View and edit customer data</Text>
                    </div>
                  </Space>
                </Card>
              </Col>
              <Col xs={24} sm={12} lg={8}>
                <Card hoverable onClick={() => (window.location.href = '/reports')}>
                  <Space>
                    <ShoppingOutlined style={{ fontSize: 24, color: '#722ed1' }} />
                    <div>
                      <Text strong>View Reports</Text>
                      <br />
                      <Text type="secondary">Generate S&OP reports</Text>
                    </div>
                  </Space>
                </Card>
              </Col>
            </>
          ) : (
            <>
              <Col xs={24} sm={12} lg={8}>
                <Card hoverable onClick={() => (window.location.href = '/sop/forecast')}>
                  <Space>
                    <CalendarOutlined style={{ fontSize: 24, color: '#1890ff' }} />
                    <div>
                      <Text strong>Enter Forecast</Text>
                      <br />
                      <Text type="secondary">Submit monthly forecasts</Text>
                    </div>
                  </Space>
                </Card>
              </Col>
              <Col xs={24} sm={12} lg={8}>
                <Card hoverable onClick={() => (window.location.href = '/sales-history')}>
                  <Space>
                    <RiseOutlined style={{ fontSize: 24, color: '#52c41a' }} />
                    <div>
                      <Text strong>Sales History</Text>
                      <br />
                      <Text type="secondary">View past 24 months</Text>
                    </div>
                  </Space>
                </Card>
              </Col>
              <Col xs={24} sm={12} lg={8}>
                <Card hoverable onClick={() => (window.location.href = '/customers')}>
                  <Space>
                    <TeamOutlined style={{ fontSize: 24, color: '#722ed1' }} />
                    <div>
                      <Text strong>My Customers</Text>
                      <br />
                      <Text type="secondary">View assigned customers</Text>
                    </div>
                  </Space>
                </Card>
              </Col>
            </>
          )}
        </Row>
      </Space>
    </div>
  );
}
