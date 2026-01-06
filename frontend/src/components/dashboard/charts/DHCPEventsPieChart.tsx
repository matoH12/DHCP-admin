import { Card, Spin, Empty, Statistic, Row, Col, Alert } from 'antd';
import { useState, useEffect } from 'react';
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { apiService } from '../../../services/api';
import type { DHCPEventsResponse } from '../../../types/api';

export function DHCPEventsPieChart() {
  const [data, setData] = useState<DHCPEventsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
    // Auto-refresh every 60 seconds
    const interval = setInterval(loadData, 60000);
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await apiService.getDHCPEvents(24);
      setData(result);
    } catch (err) {
      console.error('Failed to load DHCP events:', err);
      setError('Nepodarilo sa načítať DHCP udalosti');
    } finally {
      setLoading(false);
    }
  };

  // Custom label for pie chart showing percentage
  const renderLabel = (props: any) => {
    const { cx, cy, midAngle, innerRadius, outerRadius, percent } = props;
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
    const x = cx + radius * Math.cos(-midAngle * Math.PI / 180);
    const y = cy + radius * Math.sin(-midAngle * Math.PI / 180);

    return (
      <text
        x={x}
        y={y}
        fill="white"
        textAnchor={x > cx ? 'start' : 'end'}
        dominantBaseline="central"
        style={{ fontSize: '12px', fontWeight: 'bold' }}
      >
        {`${(percent * 100).toFixed(0)}%`}
      </text>
    );
  };

  if (loading) {
    return (
      <Card title="DHCP Udalosti (24h)">
        <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}>
          <Spin size="large" />
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card title="DHCP Udalosti (24h)">
        <Alert message={error} type="error" showIcon />
      </Card>
    );
  }

  if (!data || data.data.length === 0) {
    return (
      <Card title="DHCP Udalosti (24h)">
        <Empty description="Žiadne DHCP udalosti za posledných 24 hodín" />
      </Card>
    );
  }

  return (
    <Card title="DHCP Udalosti (24h)">
      <Row gutter={16}>
        <Col xs={24} md={12}>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={data.data}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={renderLabel}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {data.data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </Col>
        <Col xs={24} md={12}>
          <Statistic
            title="Celkom Udalostí"
            value={data.total_events}
            style={{ marginTop: 20 }}
          />
          <div style={{ marginTop: 20 }}>
            {data.data.map((event) => (
              <div key={event.name} style={{ marginBottom: 8 }}>
                <span
                  style={{
                    display: 'inline-block',
                    width: 12,
                    height: 12,
                    backgroundColor: event.color,
                    marginRight: 8,
                    borderRadius: '2px'
                  }}
                />
                <strong>{event.name}:</strong> {event.value}
              </div>
            ))}
          </div>
        </Col>
      </Row>
    </Card>
  );
}
