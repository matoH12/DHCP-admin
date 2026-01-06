import { Card, Spin, Empty } from 'antd';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  TooltipProps
} from 'recharts';

interface IPUtilizationData {
  name: string;
  assigned: number;
  available: number;
  utilization: number;
}

interface IPUtilizationBarChartProps {
  data: IPUtilizationData[];
  loading?: boolean;
}

// Custom tooltip component
const CustomTooltip = ({ active, payload, label }: TooltipProps<number, string>) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div style={{
        backgroundColor: 'white',
        padding: '10px',
        border: '1px solid #ccc',
        borderRadius: '4px'
      }}>
        <p style={{ margin: 0, fontWeight: 'bold' }}>{label}</p>
        <p style={{ margin: '4px 0', color: '#1890ff' }}>
          Priradené: {payload[0].value}
        </p>
        <p style={{ margin: '4px 0', color: '#52c41a' }}>
          Voľné: {payload[1].value}
        </p>
        <p style={{ margin: '4px 0' }}>
          Využitie: {data.utilization.toFixed(1)}%
        </p>
      </div>
    );
  }
  return null;
};

export function IPUtilizationBarChart({ data, loading }: IPUtilizationBarChartProps) {
  if (loading) {
    return (
      <Card title="Využitie IP Rozsahov">
        <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}>
          <Spin size="large" />
        </div>
      </Card>
    );
  }

  if (!data || data.length === 0) {
    return (
      <Card title="Využitie IP Rozsahov">
        <Empty description="Žiadne IP rozsahy" />
      </Card>
    );
  }

  return (
    <Card title="Využitie IP Rozsahov">
      <ResponsiveContainer width="100%" height={300}>
        <BarChart
          data={data}
          margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis label={{ value: 'IP Adresy', angle: -90, position: 'insideLeft' }} />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          <Bar dataKey="assigned" stackId="a" fill="#1890ff" name="Priradené" />
          <Bar dataKey="available" stackId="a" fill="#52c41a" name="Voľné" />
        </BarChart>
      </ResponsiveContainer>
    </Card>
  );
}
