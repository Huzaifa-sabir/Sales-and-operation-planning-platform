import { useEffect } from 'react';
import { Form, Input, Select, InputNumber, Row, Col } from 'antd';
import type { Product, ProductFormData } from '@/types';
import { PRODUCT_GROUPS, MANUFACTURING_LOCATIONS, UNITS_OF_MEASURE } from '@/config/constants';

interface ProductFormProps {
  form: any;
  initialValues?: Product;
  onSubmit: (values: ProductFormData) => Promise<void>;
}

export default function ProductForm({ form, initialValues }: ProductFormProps) {
  useEffect(() => {
    if (initialValues) {
      form.setFieldsValue({
        itemCode: initialValues.itemCode,
        itemDescription: initialValues.itemDescription,
        groupCode: initialValues.group.code,
        groupSubgroup: initialValues.group.subgroup,
        groupDesc: initialValues.group.desc,
        location: initialValues.manufacturing.location,
        line: initialValues.manufacturing.line,
        weight: initialValues.weight,
        uom: initialValues.uom,
        avgPrice: initialValues.pricing?.avgPrice,
        costPrice: initialValues.pricing?.costPrice,
      });
    }
  }, [initialValues, form]);

  return (
    <Form form={form} layout="vertical" autoComplete="off">
      <Row gutter={16}>
        <Col span={12}>
          <Form.Item
            name="itemCode"
            label="Item Code"
            rules={[{ required: true, message: 'Please enter item code' }]}
          >
            <Input placeholder="e.g., 110001" />
          </Form.Item>
        </Col>

        <Col span={12}>
          <Form.Item
            name="groupCode"
            label="Product Group"
            rules={[{ required: true, message: 'Please select product group' }]}
          >
            <Select
              placeholder="Select group"
              options={PRODUCT_GROUPS.map((group) => ({ label: group, value: group }))}
            />
          </Form.Item>
        </Col>
      </Row>

      <Form.Item
        name="itemDescription"
        label="Description"
        rules={[{ required: true, message: 'Please enter description' }]}
      >
        <Input.TextArea
          placeholder="e.g., Peeled Garlic 12x1 LB Garland"
          rows={3}
          showCount
          maxLength={500}
        />
      </Form.Item>

      <Row gutter={16}>
        <Col span={12}>
          <Form.Item
            name="groupSubgroup"
            label="Sub-Group"
          >
            <Input placeholder="e.g., G1S7" />
          </Form.Item>
        </Col>
        <Col span={12}>
          <Form.Item
            name="groupDesc"
            label="Group Description"
          >
            <Input placeholder="e.g., Group 1-2" />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={12}>
          <Form.Item
            name="location"
            label="Manufacturing Location"
            rules={[{ required: true, message: 'Please select location' }]}
          >
            <Select
              placeholder="Select location"
              showSearch
              options={MANUFACTURING_LOCATIONS.map((loc) => ({ label: loc, value: loc }))}
            />
          </Form.Item>
        </Col>

        <Col span={12}>
          <Form.Item
            name="line"
            label="Production Line"
          >
            <Input placeholder="e.g., Peeled Garlic Repack" />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={8}>
          <Form.Item
            name="weight"
            label="Weight (LB)"
          >
            <InputNumber
              placeholder="e.g., 12"
              style={{ width: '100%' }}
              min={0}
              step={0.1}
            />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item
            name="uom"
            label="Unit of Measure"
            rules={[{ required: true, message: 'Please select UOM' }]}
          >
            <Select
              placeholder="Select UOM"
              options={UNITS_OF_MEASURE.map((uom) => ({ label: uom, value: uom }))}
            />
          </Form.Item>
        </Col>
        <Col span={8}>
          <Form.Item
            name="avgPrice"
            label="Avg Price ($)"
            rules={[{ required: true, message: 'Please enter average price' }]}
          >
            <InputNumber
              placeholder="e.g., 52.00"
              style={{ width: '100%' }}
              min={0}
              step={0.01}
              precision={2}
            />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={12}>
          <Form.Item
            name="costPrice"
            label="Cost Price ($)"
          >
            <InputNumber
              placeholder="e.g., 45.00"
              style={{ width: '100%' }}
              min={0}
              step={0.01}
              precision={2}
            />
          </Form.Item>
        </Col>
      </Row>
    </Form>
  );
}
