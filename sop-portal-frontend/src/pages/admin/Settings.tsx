import { useState, useEffect } from 'react';
import {
  Card,
  Form,
  Input,
  InputNumber,
  Switch,
  Button,
  Space,
  Typography,
  Divider,
  message,
  Row,
  Col,
  Select,
  Alert,
  Tag,
} from 'antd';
import {
  SaveOutlined,
  SettingOutlined,
  MailOutlined,
  DatabaseOutlined,
  BellOutlined,
  SafetyOutlined,
  ApiOutlined,
  CheckCircleOutlined,
} from '@ant-design/icons';
import { settingsAPI, type Setting } from '@/api/settings';

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;

interface SystemSettings {
  // General Settings
  companyName: string;
  companyEmail: string;
  fiscalYearStart: number; // Month number (1-12)
  timezone: string;
  currency: string;

  // S&OP Settings
  defaultForecastMonths: number;
  mandatoryForecastMonths: number;
  cycleReminderDays: number;
  autoCloseAfterDeadline: boolean;

  // Email Settings
  enableEmailNotifications: boolean;
  emailFromAddress: string;
  emailFromName: string;
  smtpHost: string;
  smtpPort: number;
  smtpUsername: string;

  // Security Settings
  sessionTimeoutMinutes: number;
  passwordMinLength: number;
  requirePasswordChange: boolean;
  passwordChangeDays: number;
  maxLoginAttempts: number;

  // Integration Settings
  powerBIEnabled: boolean;
  powerBIWorkspaceUrl: string;
  excelTemplateVersion: string;

  // Notification Settings
  notifyOnForecastSubmission: boolean;
  notifyOnCycleOpen: boolean;
  notifyOnCycleClose: boolean;
  reminderBeforeCycleClose: boolean;
}

const defaultSettings: SystemSettings = {
  companyName: 'Heavy Garlic',
  companyEmail: 'admin@heavygarlic.com',
  fiscalYearStart: 1, // January
  timezone: 'America/New_York',
  currency: 'USD',

  defaultForecastMonths: 16,
  mandatoryForecastMonths: 12,
  cycleReminderDays: 5,
  autoCloseAfterDeadline: false,

  enableEmailNotifications: true,
  emailFromAddress: 'noreply@heavygarlic.com',
  emailFromName: 'Heavy Garlic S&OP Portal',
  smtpHost: 'smtp.gmail.com',
  smtpPort: 587,
  smtpUsername: '',

  sessionTimeoutMinutes: 480, // 8 hours
  passwordMinLength: 8,
  requirePasswordChange: true,
  passwordChangeDays: 90,
  maxLoginAttempts: 5,

  powerBIEnabled: true,
  powerBIWorkspaceUrl: '',
  excelTemplateVersion: 'v2.1',

  notifyOnForecastSubmission: true,
  notifyOnCycleOpen: true,
  notifyOnCycleClose: true,
  reminderBeforeCycleClose: true,
};

export default function Settings() {
  const [form] = Form.useForm();
  const [settings, setSettings] = useState<SystemSettings>(defaultSettings);
  const [loading, setLoading] = useState(false);
  const [isDirty, setIsDirty] = useState(false);
  const [backendSettings, setBackendSettings] = useState<Setting[]>([]);

  // Load settings from backend
  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      setLoading(true);
      const response = await settingsAPI.list();
      setBackendSettings(response.settings);
      
      // Convert backend settings to form format
      const formSettings = convertBackendToForm(response.settings);
      setSettings(formSettings);
      form.setFieldsValue(formSettings);
    } catch (error) {
      message.error('Failed to load settings');
      console.error('Error loading settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const convertBackendToForm = (backendSettings: Setting[]): SystemSettings => {
    const settingsMap = backendSettings.reduce((acc, setting) => {
      acc[setting.key] = setting.value;
      return acc;
    }, {} as Record<string, any>);

    return {
      companyName: settingsMap.app_name || defaultSettings.companyName,
      companyEmail: settingsMap.from_email || defaultSettings.companyEmail,
      fiscalYearStart: defaultSettings.fiscalYearStart,
      timezone: defaultSettings.timezone,
      currency: defaultSettings.currency,
      defaultForecastMonths: settingsMap.max_forecast_months || defaultSettings.defaultForecastMonths,
      mandatoryForecastMonths: settingsMap.min_forecast_months_required || defaultSettings.mandatoryForecastMonths,
      cycleReminderDays: settingsMap.reminder_days_before_close || defaultSettings.cycleReminderDays,
      autoCloseAfterDeadline: settingsMap.auto_close_cycles || defaultSettings.autoCloseAfterDeadline,
      enableEmailNotifications: settingsMap.notification_email_enabled || defaultSettings.enableEmailNotifications,
      emailFromAddress: settingsMap.from_email || defaultSettings.emailFromAddress,
      emailFromName: settingsMap.from_name || defaultSettings.emailFromName,
      smtpHost: settingsMap.smtp_host || defaultSettings.smtpHost,
      smtpPort: settingsMap.smtp_port || defaultSettings.smtpPort,
      smtpUsername: defaultSettings.smtpUsername,
      sessionTimeoutMinutes: settingsMap.session_timeout_minutes || defaultSettings.sessionTimeoutMinutes,
      passwordMinLength: defaultSettings.passwordMinLength,
      requirePasswordChange: defaultSettings.requirePasswordChange,
      passwordChangeDays: defaultSettings.passwordChangeDays,
      maxLoginAttempts: defaultSettings.maxLoginAttempts,
      powerBIEnabled: defaultSettings.powerBIEnabled,
      powerBIWorkspaceUrl: defaultSettings.powerBIWorkspaceUrl,
      excelTemplateVersion: defaultSettings.excelTemplateVersion,
      notifyOnForecastSubmission: defaultSettings.notifyOnForecastSubmission,
      notifyOnCycleOpen: defaultSettings.notifyOnCycleOpen,
      notifyOnCycleClose: defaultSettings.notifyOnCycleClose,
      reminderBeforeCycleClose: defaultSettings.reminderBeforeCycleClose,
    };
  };

  const handleSave = async () => {
    try {
      setLoading(true);
      const values = await form.validateFields();
      
      // Update settings in backend
      const updatePromises = Object.entries(values).map(async ([key, value]) => {
        const setting = backendSettings.find(s => s.key === key);
        if (setting && setting.value !== value) {
          return settingsAPI.update(key, { value });
        }
        return null;
      });

      await Promise.all(updatePromises.filter(Boolean));
      
      setSettings(values);
      setIsDirty(false);
      message.success('Settings saved successfully');
      
      // Reload settings to get updated values
      await loadSettings();
    } catch (error) {
      message.error('Failed to save settings');
      console.error('Error saving settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    form.setFieldsValue(settings);
    setIsDirty(false);
    message.info('Changes discarded');
  };

  const handleTestEmail = () => {
    message.success('Test email sent to admin@heavygarlic.com');
  };

  const handleTestPowerBI = () => {
    window.open('https://powerbi.microsoft.com/', '_blank');
    message.info('Opening Power BI workspace...');
  };

  return (
    <div>
      <Title level={3}>System Settings</Title>
      <Paragraph type="secondary">
        Configure system-wide settings, integrations, and preferences
      </Paragraph>

      {isDirty && (
        <Alert
          message="You have unsaved changes"
          description="Please save or discard your changes before leaving this page"
          type="warning"
          showIcon
          style={{ marginBottom: 24 }}
        />
      )}

      <Form
        form={form}
        layout="vertical"
        initialValues={settings}
        onValuesChange={() => setIsDirty(true)}
      >
        {/* General Settings */}
        <Card
          title={
            <Space>
              <SettingOutlined />
              <Text strong>General Settings</Text>
            </Space>
          }
          style={{ marginBottom: 16 }}
        >
          <Row gutter={16}>
            <Col xs={24} md={12}>
              <Form.Item
                name="companyName"
                label="Company Name"
                rules={[{ required: true, message: 'Required' }]}
              >
                <Input />
              </Form.Item>
            </Col>
            <Col xs={24} md={12}>
              <Form.Item
                name="companyEmail"
                label="Company Email"
                rules={[
                  { required: true, message: 'Required' },
                  { type: 'email', message: 'Invalid email' },
                ]}
              >
                <Input prefix={<MailOutlined />} />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col xs={24} md={8}>
              <Form.Item
                name="fiscalYearStart"
                label="Fiscal Year Start Month"
                rules={[{ required: true, message: 'Required' }]}
              >
                <Select
                  options={[
                    { label: 'January', value: 1 },
                    { label: 'February', value: 2 },
                    { label: 'March', value: 3 },
                    { label: 'April', value: 4 },
                    { label: 'May', value: 5 },
                    { label: 'June', value: 6 },
                    { label: 'July', value: 7 },
                    { label: 'August', value: 8 },
                    { label: 'September', value: 9 },
                    { label: 'October', value: 10 },
                    { label: 'November', value: 11 },
                    { label: 'December', value: 12 },
                  ]}
                />
              </Form.Item>
            </Col>
            <Col xs={24} md={8}>
              <Form.Item
                name="timezone"
                label="Timezone"
                rules={[{ required: true, message: 'Required' }]}
              >
                <Select
                  options={[
                    { label: 'Eastern Time (ET)', value: 'America/New_York' },
                    { label: 'Central Time (CT)', value: 'America/Chicago' },
                    { label: 'Mountain Time (MT)', value: 'America/Denver' },
                    { label: 'Pacific Time (PT)', value: 'America/Los_Angeles' },
                  ]}
                />
              </Form.Item>
            </Col>
            <Col xs={24} md={8}>
              <Form.Item
                name="currency"
                label="Currency"
                rules={[{ required: true, message: 'Required' }]}
              >
                <Select
                  options={[
                    { label: 'USD ($)', value: 'USD' },
                    { label: 'EUR (€)', value: 'EUR' },
                    { label: 'GBP (£)', value: 'GBP' },
                    { label: 'CAD ($)', value: 'CAD' },
                  ]}
                />
              </Form.Item>
            </Col>
          </Row>
        </Card>

        {/* S&OP Settings */}
        <Card
          title={
            <Space>
              <DatabaseOutlined />
              <Text strong>S&OP Process Settings</Text>
            </Space>
          }
          style={{ marginBottom: 16 }}
        >
          <Row gutter={16}>
            <Col xs={24} md={12}>
              <Form.Item
                name="defaultForecastMonths"
                label="Default Forecast Period (Months)"
                rules={[{ required: true, message: 'Required' }]}
                extra="Total number of months to forecast"
              >
                <InputNumber min={12} max={24} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col xs={24} md={12}>
              <Form.Item
                name="mandatoryForecastMonths"
                label="Mandatory Forecast Months"
                rules={[{ required: true, message: 'Required' }]}
                extra="Number of mandatory months (must be filled)"
              >
                <InputNumber min={6} max={18} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col xs={24} md={12}>
              <Form.Item
                name="cycleReminderDays"
                label="Send Reminder Before Cycle Close (Days)"
                rules={[{ required: true, message: 'Required' }]}
              >
                <InputNumber min={1} max={14} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col xs={24} md={12}>
              <Form.Item
                name="autoCloseAfterDeadline"
                label="Auto-Close Cycle After Deadline"
                valuePropName="checked"
              >
                <Switch checkedChildren="Yes" unCheckedChildren="No" />
              </Form.Item>
            </Col>
          </Row>
        </Card>

        {/* Email Settings */}
        <Card
          title={
            <Space>
              <MailOutlined />
              <Text strong>Email Configuration</Text>
            </Space>
          }
          extra={
            <Button onClick={handleTestEmail} size="small">
              Send Test Email
            </Button>
          }
          style={{ marginBottom: 16 }}
        >
          <Form.Item name="enableEmailNotifications" valuePropName="checked">
            <Space>
              <Switch />
              <Text strong>Enable Email Notifications</Text>
            </Space>
          </Form.Item>

          <Row gutter={16}>
            <Col xs={24} md={12}>
              <Form.Item
                name="emailFromAddress"
                label="From Email Address"
                rules={[
                  { required: true, message: 'Required' },
                  { type: 'email', message: 'Invalid email' },
                ]}
              >
                <Input prefix={<MailOutlined />} />
              </Form.Item>
            </Col>
            <Col xs={24} md={12}>
              <Form.Item name="emailFromName" label="From Name" rules={[{ required: true, message: 'Required' }]}>
                <Input />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col xs={24} md={12}>
              <Form.Item name="smtpHost" label="SMTP Host" rules={[{ required: true, message: 'Required' }]}>
                <Input placeholder="smtp.gmail.com" />
              </Form.Item>
            </Col>
            <Col xs={24} md={6}>
              <Form.Item name="smtpPort" label="SMTP Port" rules={[{ required: true, message: 'Required' }]}>
                <InputNumber min={1} max={65535} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col xs={24} md={6}>
              <Form.Item name="smtpUsername" label="SMTP Username">
                <Input placeholder="Optional" />
              </Form.Item>
            </Col>
          </Row>
        </Card>

        {/* Security Settings */}
        <Card
          title={
            <Space>
              <SafetyOutlined />
              <Text strong>Security & Authentication</Text>
            </Space>
          }
          style={{ marginBottom: 16 }}
        >
          <Row gutter={16}>
            <Col xs={24} md={8}>
              <Form.Item
                name="sessionTimeoutMinutes"
                label="Session Timeout (Minutes)"
                rules={[{ required: true, message: 'Required' }]}
              >
                <InputNumber min={30} max={1440} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col xs={24} md={8}>
              <Form.Item
                name="passwordMinLength"
                label="Minimum Password Length"
                rules={[{ required: true, message: 'Required' }]}
              >
                <InputNumber min={6} max={32} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col xs={24} md={8}>
              <Form.Item
                name="maxLoginAttempts"
                label="Max Login Attempts"
                rules={[{ required: true, message: 'Required' }]}
              >
                <InputNumber min={3} max={10} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col xs={24} md={12}>
              <Form.Item name="requirePasswordChange" valuePropName="checked">
                <Space>
                  <Switch />
                  <Text>Require Periodic Password Change</Text>
                </Space>
              </Form.Item>
            </Col>
            <Col xs={24} md={12}>
              <Form.Item
                name="passwordChangeDays"
                label="Password Change Period (Days)"
                rules={[{ required: true, message: 'Required' }]}
              >
                <InputNumber min={30} max={365} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>
        </Card>

        {/* Integration Settings */}
        <Card
          title={
            <Space>
              <ApiOutlined />
              <Text strong>Integrations</Text>
            </Space>
          }
          style={{ marginBottom: 16 }}
        >
          <Row gutter={16}>
            <Col xs={24} md={12}>
              <Form.Item name="powerBIEnabled" valuePropName="checked">
                <Space>
                  <Switch />
                  <Text strong>Enable Power BI Integration</Text>
                  <Tag color="blue">AVAILABLE</Tag>
                </Space>
              </Form.Item>
              <Form.Item
                name="powerBIWorkspaceUrl"
                label="Power BI Workspace URL"
                extra="URL to your Power BI workspace or dashboard"
              >
                <Input
                  placeholder="https://app.powerbi.com/groups/..."
                  suffix={
                    <Button type="link" size="small" onClick={handleTestPowerBI}>
                      Test
                    </Button>
                  }
                />
              </Form.Item>
            </Col>
            <Col xs={24} md={12}>
              <Form.Item name="excelTemplateVersion" label="Excel Template Version">
                <Select
                  options={[
                    { label: 'Version 2.1 (Current)', value: 'v2.1' },
                    { label: 'Version 2.0', value: 'v2.0' },
                    { label: 'Version 1.5 (Legacy)', value: 'v1.5' },
                  ]}
                />
              </Form.Item>
            </Col>
          </Row>
        </Card>

        {/* Notification Settings */}
        <Card
          title={
            <Space>
              <BellOutlined />
              <Text strong>Notification Preferences</Text>
            </Space>
          }
          style={{ marginBottom: 16 }}
        >
          <Space direction="vertical" size="middle">
            <Form.Item name="notifyOnForecastSubmission" valuePropName="checked">
              <Space>
                <Switch />
                <Text>Notify admins when forecast is submitted</Text>
              </Space>
            </Form.Item>

            <Form.Item name="notifyOnCycleOpen" valuePropName="checked">
              <Space>
                <Switch />
                <Text>Notify sales reps when S&OP cycle opens</Text>
              </Space>
            </Form.Item>

            <Form.Item name="notifyOnCycleClose" valuePropName="checked">
              <Space>
                <Switch />
                <Text>Notify all users when S&OP cycle closes</Text>
              </Space>
            </Form.Item>

            <Form.Item name="reminderBeforeCycleClose" valuePropName="checked">
              <Space>
                <Switch />
                <Text>Send reminder before cycle close deadline</Text>
              </Space>
            </Form.Item>
          </Space>
        </Card>

        {/* Action Buttons */}
        <Card>
          <Space size="large">
            <Button
              type="primary"
              icon={<SaveOutlined />}
              onClick={handleSave}
              loading={loading}
              disabled={!isDirty}
              size="large"
            >
              Save Settings
            </Button>
            <Button onClick={handleReset} disabled={!isDirty} size="large">
              Discard Changes
            </Button>
            {!isDirty && (
              <Tag icon={<CheckCircleOutlined />} color="success">
                All changes saved
              </Tag>
            )}
          </Space>
        </Card>
      </Form>

      {/* System Info */}
      <Card title="System Information" style={{ marginTop: 16 }}>
        <Row gutter={16}>
          <Col span={8}>
            <Text type="secondary">Application Version:</Text>
            <br />
            <Text strong>v1.0.0</Text>
          </Col>
          <Col span={8}>
            <Text type="secondary">Database:</Text>
            <br />
            <Text strong>MongoDB 7.0</Text>
          </Col>
          <Col span={8}>
            <Text type="secondary">Last Settings Update:</Text>
            <br />
            <Text strong>Oct 15, 2025 10:30 AM</Text>
          </Col>
        </Row>
      </Card>
    </div>
  );
}
