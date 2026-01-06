import { useEffect, useState } from 'react';
import { Row, Col, Card, Statistic, Table, Progress, Typography, Spin } from 'antd';
import {
  DatabaseOutlined,
  LaptopOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
} from '@ant-design/icons';
import { apiService } from '../../services/api';
import type { OverviewStatistics, RecentDevice } from '../../types/api';
import dayjs from 'dayjs';

const { Title } = Typography;

export function Dashboard() {
  const [stats, setStats] = useState<OverviewStatistics | null>(null);
  const [recentDevices, setRecentDevices] = useState<RecentDevice[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [statsData, devicesData] = await Promise.all([
        apiService.getOverviewStats(),
        apiService.getRecentDevices(10),
      ]);
      setStats(statsData);
      setRecentDevices(devicesData.devices);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !stats) {
    return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;
  }

  const rangeColumns = [
    {
      title: 'Rozsah',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'Sieť',
      dataIndex: 'network',
      key: 'network',
    },
    {
      title: 'Priradené',
      dataIndex: 'assigned',
      key: 'assigned',
    },
    {
      title: 'Voľné',
      dataIndex: 'available',
      key: 'available',
    },
    {
      title: 'Využitie',
      key: 'utilization',
      render: (_: unknown, record: { utilization: number }) => (
        <Progress
          percent={Number(record.utilization.toFixed(1))}
          status={record.utilization > 80 ? 'exception' : 'active'}
          size="small"
        />
      ),
    },
  ];

  const devicesColumns = [
    {
      title: 'Hostname',
      dataIndex: 'hostname',
      key: 'hostname',
    },
    {
      title: 'IP Adresa',
      dataIndex: 'ip_address',
      key: 'ip_address',
    },
    {
      title: 'MAC Adresa',
      dataIndex: 'mac_address',
      key: 'mac_address',
    },
    {
      title: 'Rozsah',
      dataIndex: 'range_name',
      key: 'range_name',
    },
    {
      title: 'Vytvorené',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => dayjs(date).format('DD.MM.YYYY HH:mm'),
    },
  ];

  return (
    <div>
      <Title level={2}>Dashboard</Title>

      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="IP Rozsahy"
              value={stats.summary.total_ranges}
              prefix={<DatabaseOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Celkom Zariadení"
              value={stats.summary.total_devices}
              prefix={<LaptopOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Aktívne"
              value={stats.summary.active_devices}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Neaktívne"
              value={stats.summary.inactive_devices}
              prefix={<CloseCircleOutlined />}
              valueStyle={{ color: '#ff4d4f' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} lg={12}>
          <Card>
            <Statistic
              title="Celkové Využitie IP Adries"
              value={stats.summary.overall_utilization_percent}
              suffix="%"
              valueStyle={{
                color: stats.summary.overall_utilization_percent > 80 ? '#ff4d4f' : '#3f8600'
              }}
            />
            <Progress
              percent={stats.summary.overall_utilization_percent}
              status={stats.summary.overall_utilization_percent > 80 ? 'exception' : 'active'}
              style={{ marginTop: 16 }}
            />
            <div style={{ marginTop: 8, fontSize: 14, color: '#666' }}>
              {stats.summary.total_assigned_ips} / {stats.summary.total_usable_ips} IP adries priradených
            </div>
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card>
            <Title level={4}>Voľné IP Adresy</Title>
            <Statistic
              value={stats.summary.total_available_ips}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24}>
          <Card title="Využitie IP Rozsahov">
            <Table
              dataSource={stats.ranges}
              columns={rangeColumns}
              rowKey="id"
              pagination={false}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24}>
          <Card title="Nedávno Pridané Zariadenia">
            <Table
              dataSource={recentDevices}
              columns={devicesColumns}
              rowKey="id"
              pagination={false}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
}
