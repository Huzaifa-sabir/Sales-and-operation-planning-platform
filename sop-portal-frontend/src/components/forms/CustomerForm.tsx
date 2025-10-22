import { useEffect } from 'react';
import { Form, Input, Select, Switch, Row, Col, message } from 'antd';
import type { Customer, CustomerFormData } from '@/types';
import { US_STATES } from '@/config/constants';

interface CustomerFormProps {
  form: any;
  initialValues?: Customer;
  onSubmit: (values: CustomerFormData) => Promise<void>;
}

export default function CustomerForm({ form, initialValues }: CustomerFormProps) {
  useEffect(() => {
    if (initialValues) {
      form.setFieldsValue({
        customerId: initialValues.customerId,
        customerName: initialValues.customerName,
        sopCustomerName: initialValues.sopCustomerName,
        salesRepId: initialValues.salesRepId,
        city: initialValues.location?.city,
        state: initialValues.location?.state,
        address1: initialValues.location?.address1,
        address2: initialValues.location?.address2,
        zip: initialValues.location?.zip,
        corporateGroup: initialValues.corporateGroup,
      });
    }
  }, [initialValues, form]);

  return (
    <Form form={form} layout="vertical" autoComplete="off">
      <Row gutter={16}>
        <Col span={12}>
          <Form.Item
            name="customerId"
            label="Customer ID"
            rules={[{ required: true, message: 'Please enter customer ID' }]}
          >
            <Input placeholder="e.g., PATITO-000001" />
          </Form.Item>
        </Col>

        <Col span={12}>
          <Form.Item
            name="customerName"
            label="Customer Name"
            rules={[{ required: true, message: 'Please enter customer name' }]}
          >
            <Input placeholder="e.g., Industria Los Patitos" />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={12}>
          <Form.Item name="sopCustomerName" label="S&OP Customer Name">
            <Input placeholder="Short name for S&OP reports" />
          </Form.Item>
        </Col>

        <Col span={12}>
          <Form.Item
            name="salesRepId"
            label="Sales Representative"
            rules={[{ required: true, message: 'Please select sales rep' }]}
          >
            <Select
              placeholder="Select sales rep"
              showSearch
              options={[
                { label: 'David Brace', value: 'rep1' },
                { label: 'Pedro Galavis', value: 'rep2' },
                { label: 'Mario Pfaeffle JR', value: 'rep3' },
                { label: 'Mario Celsi', value: 'rep4' },
                { label: 'Roger Guevara', value: 'rep5' },
                { label: 'Mario Pfaeffle SR', value: 'rep6' },
                { label: 'Joe Cardi', value: 'rep7' },
                { label: 'Jim Rodman', value: 'rep8' },
                { label: 'Randell Nichols', value: 'rep9' },
                { label: 'Keith JC', value: 'rep10' },
              ]}
            />
          </Form.Item>
        </Col>
      </Row>

      <Form.Item name="address1" label="Address Line 1">
        <Input placeholder="Street address" />
      </Form.Item>

      <Form.Item name="address2" label="Address Line 2">
        <Input placeholder="Apt, suite, building (optional)" />
      </Form.Item>

      <Row gutter={16}>
        <Col span={8}>
          <Form.Item name="city" label="City">
            <Input placeholder="e.g., Miami" />
          </Form.Item>
        </Col>

        <Col span={8}>
          <Form.Item name="state" label="State">
            <Select
              placeholder="Select state"
              showSearch
              options={US_STATES.map((state) => ({ label: state, value: state }))}
            />
          </Form.Item>
        </Col>

        <Col span={8}>
          <Form.Item
            name="zip"
            label="ZIP Code"
            rules={[
              {
                pattern: /^\d{5}(-\d{4})?$/,
                message: 'Please enter valid ZIP code',
              },
            ]}
          >
            <Input placeholder="e.g., 33101" />
          </Form.Item>
        </Col>
      </Row>

      <Form.Item name="corporateGroup" label="Corporate Group">
        <Input placeholder="e.g., Food Services" />
      </Form.Item>
    </Form>
  );
}
