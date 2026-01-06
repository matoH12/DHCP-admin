import { Card, Spin, Radio, Empty, Alert } from 'antd';
import { useState, useEffect } from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { apiService } from '../../../services/api';
import type { ActivityTimelineResponse } from '../../../types/api';
import dayjs from 'dayjs';

type TimePeriod = 7 | 30;

export function DeviceActivityTimeline() {
  const [period, setPeriod] = useState<TimePeriod>(7);
  const [data, setData] = useState<ActivityTimelineResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, [period]);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await apiService.getActivityTimeline(period);
      setData(result);
    } catch (err) {
      console.error('Failed to load activity timeline:', err);
      setError('Nepodarilo sa načítať dáta aktivity');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr: string) => {
    return dayjs(dateStr).format('DD.MM');
  };

  const chartData = data?.data.map(point => ({
    ...point,
    dateFormatted: formatDate(point.date)
  })) || [];

  return (
    <Card
      title="Aktivita Zariadení"
      extra={
        <Radio.Group value={period} onChange={(e) => setPeriod(e.target.value)}>
          <Radio.Button value={7}>7 dní</Radio.Button>
          <Radio.Button value={30}>30 dní</Radio.Button>
        </Radio.Group>
      }
    >
      {loading ? (
        <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}>
          <Spin size="large" />
        </div>
      ) : error ? (
        <Alert message={error} type="error" showIcon />
      ) : chartData.length === 0 ? (
        <Empty description="Žiadne dáta o aktivite zariadení" />
      ) : (
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart
            data={chartData}
            margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
          >
            <defs>
              <linearGradient id="colorDevices" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#1890ff" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#1890ff" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="dateFormatted" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Area
              type="monotone"
              dataKey="active_devices"
              stroke="#1890ff"
              fillOpacity={1}
              fill="url(#colorDevices)"
              name="Aktívne Zariadenia"
            />
          </AreaChart>
        </ResponsiveContainer>
      )}
    </Card>
  );
}
