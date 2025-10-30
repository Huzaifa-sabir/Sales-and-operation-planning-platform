import { useEffect, useMemo, useState } from 'react';
import { Card, Typography, Table, InputNumber, Button, Space, message, Upload, Tag } from 'antd';
import { UploadOutlined, SaveOutlined, CheckOutlined, DownloadOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import { cyclesAPI } from '@/api/cycles';
import { forecastsAPI, type Forecast, type MonthlyForecast } from '@/api/forecasts';

const { Title, Text } = Typography;

export default function ForecastEntry() {
  const [activeCycle, setActiveCycle] = useState<any | null>(null);
  const [rows, setRows] = useState<Forecast[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    load();
  }, []);

  const load = async () => {
    try {
      setLoading(true);
      const cycle = await cyclesAPI.getCurrent();
      if (!cycle) {
        setActiveCycle(null);
        setRows([]);
        return;
      }
      setActiveCycle(cycle);
      const list = await forecastsAPI.list({ page: 1, pageSize: 500, cycleId: cycle._id });
      setRows(list.forecasts || []);
    } catch (e) {
      message.error('Failed to load forecasts');
    } finally {
      setLoading(false);
    }
  };

  const months = useMemo(() => {
    const pp = activeCycle?.planningPeriod;
    if (!pp?.months || !Array.isArray(pp.months)) return [] as string[];
    return pp.months as string[]; // expecting ["2025-01", ...]
  }, [activeCycle]);

  const updateCell = (rowIndex: number, month: string, value: number) => {
    setRows(prev => {
      const copy = [...prev];
      const row = { ...copy[rowIndex] } as Forecast;
      const mf = [...(row.monthlyForecasts || [])];
      const idx = mf.findIndex(m => m.month === month);
      const next: MonthlyForecast = { month, quantity: Math.max(0, Number(value || 0)) };
      if (idx >= 0) mf[idx] = next; else mf.push(next);
      row.monthlyForecasts = mf;
      // recompute totalQuantity locally
      row.totalQuantity = mf.reduce((s, m) => s + (m.quantity || 0), 0);
      copy[rowIndex] = row;
      return copy;
    });
  };

  const saveRow = async (row: Forecast) => {
    try {
      if (row._id) {
        const updated = await forecastsAPI.update(row._id, { monthlyForecasts: row.monthlyForecasts, notes: row.notes });
        setRows(prev => prev.map(r => (r._id === updated._id ? updated : r)));
        message.success('Saved');
      }
    } catch (e: any) {
      message.error(e?.response?.data?.detail || 'Failed to save');
    }
  };

  const submitRow = async (row: Forecast) => {
    try {
      const res = await forecastsAPI.submit(row._id);
      setRows(prev => prev.map(r => (r._id === row._id ? res.forecast : r)));
      message.success('Submitted');
    } catch (e: any) {
      message.error(e?.response?.data?.detail || 'Failed to submit');
    }
  };

  const downloadTemplate = async () => {
    if (!activeCycle) return;
    const blob = await forecastsAPI.template(activeCycle._id);
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `forecast_template_${activeCycle.cycleName.replace(/\s+/g, '_')}.xlsx`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const exportAll = async () => {
    if (!activeCycle) return;
    const blob = await forecastsAPI.export(activeCycle._id);
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `forecasts_${activeCycle.cycleName.replace(/\s+/g, '_')}_${dayjs().format('YYYYMMDD')}.xlsx`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const columns: any[] = [
    {
      title: 'Customer',
      dataIndex: 'customerId',
      fixed: 'left',
      width: 150,
    },
    {
      title: 'Product',
      dataIndex: 'productId',
      fixed: 'left',
      width: 150,
    },
    ...months.map((m) => ({
      title: dayjs(m + '-01').format('MMM YY'),
      dataIndex: m,
      width: 110,
      render: (_: any, record: Forecast, index: number) => {
        const qty = record.monthlyForecasts?.find(x => x.month === m)?.quantity || 0;
        const disabled = !activeCycle || activeCycle.status !== 'open' || record.status !== 'DRAFT';
        return (
          <InputNumber
            min={0}
            value={qty}
            disabled={disabled}
            onChange={(val) => updateCell(index, m, Number(val || 0))}
            style={{ width: '100%' }}
          />
        );
      }
    })),
    {
      title: 'Total Qty',
      key: 'totalQuantity',
      width: 120,
      render: (_: any, record: Forecast) => record.totalQuantity || 0,
    },
    {
      title: 'Status',
      dataIndex: 'status',
      width: 110,
      render: (s: string) => <Tag color={s === 'SUBMITTED' ? 'blue' : s === 'APPROVED' ? 'green' : s === 'REJECTED' ? 'red' : 'default'}>{s}</Tag>
    },
    {
      title: 'Actions',
      fixed: 'right',
      width: 180,
      render: (_: any, record: Forecast) => (
        <Space>
          <Button icon={<SaveOutlined />} disabled={record.status !== 'DRAFT'} onClick={() => saveRow(record)}>Save</Button>
          <Button type="primary" icon={<CheckOutlined />} disabled={record.status !== 'DRAFT'} onClick={() => submitRow(record)}>Submit</Button>
        </Space>
      )
    }
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <div>
          <Title level={3}>Forecast Entry</Title>
          <Text type="secondary">{activeCycle ? `${activeCycle.cycleName} · ${dayjs(activeCycle.dates.startDate).format('MMM DD')} - ${dayjs(activeCycle.dates.endDate).format('MMM DD, YYYY')}` : 'No open cycle'}</Text>
        </div>
        <Space>
          <Button icon={<DownloadOutlined />} onClick={downloadTemplate} disabled={!activeCycle}>Download Template</Button>
          <Upload
            beforeUpload={() => false}
            maxCount={1}
            accept=".xlsx,.xls"
            customRequest={async ({ file, onSuccess, onError }: any) => {
              try {
                const f = file as File;
                await forecastsAPI.bulkUpload(activeCycle._id, f);
                message.success('Uploaded');
                await load();
                onSuccess && onSuccess({}, new XMLHttpRequest());
              } catch (e: any) {
                onError && onError(e);
                message.error(e?.response?.data?.detail || 'Upload failed');
              }
            }}
          >
            <Button icon={<UploadOutlined />} disabled={!activeCycle}>Bulk Upload</Button>
          </Upload>
          <Button onClick={exportAll} disabled={!activeCycle}>Export</Button>
        </Space>
      </div>

      <Card>
        <Table
          rowKey="_id"
          dataSource={rows}
          columns={columns}
          loading={loading}
          scroll={{ x: 1200 }}
          pagination={{ pageSize: 50 }}
        />
      </Card>
    </div>
  );
}


