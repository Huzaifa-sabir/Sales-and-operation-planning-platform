import { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { Layout as AntLayout, Menu, Avatar, Dropdown, Typography, Badge } from 'antd';
import type { MenuProps } from 'antd';
import {
  DashboardOutlined,
  TeamOutlined,
  ShoppingOutlined,
  BarChartOutlined,
  CalendarOutlined,
  FileTextOutlined,
  SettingOutlined,
  LogoutOutlined,
  UserOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
} from '@ant-design/icons';
import { useAuthStore } from '@/store/authStore';
import { ROUTES, ROLES } from '@/config/constants';

const { Header, Sider, Content } = AntLayout;
const { Text } = Typography;

export default function Layout() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuthStore();
  const [collapsed, setCollapsed] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate(ROUTES.LOGIN);
  };

  // User menu dropdown
  const userMenuItems: MenuProps['items'] = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: 'Profile',
      onClick: () => console.log('Profile clicked'),
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: 'Settings',
      onClick: () => navigate(ROUTES.ADMIN_SETTINGS),
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: 'Logout',
      onClick: handleLogout,
      danger: true,
    },
  ];

  // Sidebar menu items
  const menuItems: MenuProps['items'] = [
    {
      key: ROUTES.DASHBOARD,
      icon: <DashboardOutlined />,
      label: 'Dashboard',
      onClick: () => navigate(ROUTES.DASHBOARD),
    },
    {
      key: 'master-data',
      icon: <TeamOutlined />,
      label: 'Master Data',
      children: [
        {
          key: ROUTES.CUSTOMERS,
          label: 'Customers',
          onClick: () => navigate(ROUTES.CUSTOMERS),
        },
        {
          key: ROUTES.PRODUCTS,
          label: 'Products',
          onClick: () => navigate(ROUTES.PRODUCTS),
        },
      ],
    },
    {
      key: ROUTES.SALES_HISTORY,
      icon: <BarChartOutlined />,
      label: 'Sales History',
      onClick: () => navigate(ROUTES.SALES_HISTORY),
    },
    {
      key: 'sop',
      icon: <CalendarOutlined />,
      label: 'S&OP',
      children: [
        ...(user?.role === ROLES.ADMIN
          ? [
              {
                key: ROUTES.SOP_CYCLES,
                label: 'Manage Cycles',
                onClick: () => navigate(ROUTES.SOP_CYCLES),
              },
            ]
          : []),
        {
          key: 'forecast',
          label: 'Forecast Entry',
          onClick: () => navigate('/sop/forecast'),
        },
      ],
    },
    {
      key: ROUTES.REPORTS,
      icon: <FileTextOutlined />,
      label: 'Reports',
      onClick: () => navigate(ROUTES.REPORTS),
    },
    ...(user?.role === ROLES.ADMIN
      ? [
          {
            key: 'admin',
            icon: <SettingOutlined />,
            label: 'Admin',
            children: [
              {
                key: ROUTES.ADMIN_USERS,
                label: 'Users',
                onClick: () => navigate(ROUTES.ADMIN_USERS),
              },
              {
                key: ROUTES.ADMIN_SETTINGS,
                label: 'Settings',
                onClick: () => navigate(ROUTES.ADMIN_SETTINGS),
              },
            ],
          },
        ]
      : []),
  ];

  // Get current selected key based on route
  const getSelectedKey = () => {
    const path = location.pathname;
    if (path.startsWith('/customers')) return ROUTES.CUSTOMERS;
    if (path.startsWith('/products')) return ROUTES.PRODUCTS;
    if (path.startsWith('/sales-history')) return ROUTES.SALES_HISTORY;
    if (path.startsWith('/sop/cycles')) return ROUTES.SOP_CYCLES;
    if (path.startsWith('/sop')) return 'forecast';
    if (path.startsWith('/reports')) return ROUTES.REPORTS;
    if (path.startsWith('/admin/users')) return ROUTES.ADMIN_USERS;
    if (path.startsWith('/admin/settings')) return ROUTES.ADMIN_SETTINGS;
    return ROUTES.DASHBOARD;
  };

  return (
    <AntLayout style={{ minHeight: '100vh' }}>
      {/* Sidebar */}
      <Sider
        trigger={null}
        collapsible
        collapsed={collapsed}
        breakpoint="lg"
        onBreakpoint={(broken) => {
          if (broken) setCollapsed(true);
        }}
        style={{
          overflow: 'auto',
          height: '100vh',
          position: 'fixed',
          left: 0,
          top: 0,
          bottom: 0,
        }}
      >
        <div
          style={{
            height: 64,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#fff',
            fontSize: collapsed ? 16 : 18,
            fontWeight: 'bold',
            borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
          }}
        >
          {collapsed ? 'S&OP' : 'S&OP Portal'}
        </div>

        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[getSelectedKey()]}
          items={menuItems}
          style={{ borderRight: 0 }}
        />
      </Sider>

      {/* Main Layout */}
      <AntLayout style={{ marginLeft: collapsed ? 80 : 200, transition: 'all 0.2s' }}>
        {/* Header */}
        <Header
          style={{
            padding: '0 24px',
            background: '#fff',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
            position: 'sticky',
            top: 0,
            zIndex: 1,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            {collapsed ? (
              <MenuUnfoldOutlined
                style={{ fontSize: 18, cursor: 'pointer' }}
                onClick={() => setCollapsed(false)}
              />
            ) : (
              <MenuFoldOutlined
                style={{ fontSize: 18, cursor: 'pointer' }}
                onClick={() => setCollapsed(true)}
              />
            )}
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            {/* Notification Badge (future feature) */}
            <Badge count={0} showZero={false}>
              <ShoppingOutlined style={{ fontSize: 20, cursor: 'pointer' }} />
            </Badge>

            {/* User Dropdown */}
            <Dropdown menu={{ items: userMenuItems }} placement="bottomRight" arrow>
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  cursor: 'pointer',
                }}
              >
                <Avatar
                  style={{ backgroundColor: '#1890ff' }}
                  icon={<UserOutlined />}
                />
                <div style={{ display: 'flex', flexDirection: 'column', lineHeight: 1.2 }}>
                  <Text strong>{user?.fullName}</Text>
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    {user?.role === ROLES.ADMIN ? 'Administrator' : 'Sales Rep'}
                  </Text>
                </div>
              </div>
            </Dropdown>
          </div>
        </Header>

        {/* Content */}
        <Content
          style={{
            margin: '24px',
            padding: 24,
            background: '#fff',
            minHeight: 280,
            borderRadius: 8,
          }}
        >
          <Outlet />
        </Content>
      </AntLayout>
    </AntLayout>
  );
}
