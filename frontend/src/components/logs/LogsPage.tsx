import { useEffect, useState } from 'react';
import {
  Table,
  Input,
  Select,
  Typography,
  message,
  Tag,
  Space,
  Card,
  Row,
  Col,
  Statistic,
  Button,
} from 'antd';
import {
  SearchOutlined,
  ReloadOutlined,
  DeleteOutlined,
} from '@ant-design/icons';
import { apiService } from '../../services/api';
import type { SyslogMessage, SyslogStats } from '../../types/api';

const { Title } = Typography;
const { Search } = Input;

const getSeverityColor = (severity: string | null) => {
  if (!severity) return 'default';
  switch (severity.toLowerCase()) {
    case 'emergency':
    case 'alert':
    case 'critical':
      return 'red';
    case 'error':
      return 'volcano';
    case 'warning':
      return 'orange';
    case 'notice':
      return 'blue';
    case 'info':
      return 'cyan';
    case 'debug':
      return 'purple';
    default:
      return 'default';
  }
};

export function LogsPage() {
  const [logs, setLogs] = useState<SyslogMessage[]>([]);
  const [stats, setStats] = useState<SyslogStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState<{
    search: string;
    severity: string | undefined;
    program: string | undefined;
    hours: number;
  }>({
    search: '',
    severity: undefined,
    program: undefined,
    hours: 24,
  });

  useEffect(() => {
    loadLogs();
    loadStats();
    // Auto-refresh every 30 seconds
    const interval = setInterval(() => {
      loadLogs();
      loadStats();
    }, 30000);
    return () => clearInterval(interval);
  }, [filters]);

  const loadLogs = async () => {
    setLoading(true);
    try {
      const data = await apiService.getSyslogMessages({
        limit: 500,
        search: filters.search || undefined,
        severity: filters.severity,
        program: filters.program,
        hours: filters.hours,
      });
      setLogs(data);
    } catch (error) {
      message.error('Nepodarilo sa načítať logy');
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const data = await apiService.getSyslogStats(filters.hours);
      setStats(data);
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const handleSearch = (value: string) => {
    setFilters({ ...filters, search: value });
  };

  const handleRefresh = () => {
    loadLogs();
    loadStats();
    message.success('Logy obnovené');
  };

  const columns = [
    {
      title: 'Čas',
      dataIndex: 'timestamp',
      key: 'timestamp',
      width: 180,
      render: (timestamp: string) => new Date(timestamp).toLocaleString('sk-SK'),
      sorter: (a: SyslogMessage, b: SyslogMessage) =>
        new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime(),
    },
    {
      title: 'Závažnosť',
      dataIndex: 'severity',
      key: 'severity',
      width: 120,
      render: (severity: string | null) => severity ? (
        <Tag color={getSeverityColor(severity)}>{severity.toUpperCase()}</Tag>
      ) : '-',
      filters: [
        { text: 'Emergency', value: 'emergency' },
        { text: 'Alert', value: 'alert' },
        { text: 'Critical', value: 'critical' },
        { text: 'Error', value: 'error' },
        { text: 'Warning', value: 'warning' },
        { text: 'Notice', value: 'notice' },
        { text: 'Info', value: 'info' },
        { text: 'Debug', value: 'debug' },
      ],
      onFilter: (value: string | number | boolean, record: SyslogMessage) =>
        record.severity === value,
    },
    {
      title: 'Program',
      dataIndex: 'program',
      key: 'program',
      width: 150,
      render: (program: string | null) => program || '-',
    },
    {
      title: 'Hostname',
      dataIndex: 'hostname',
      key: 'hostname',
      width: 150,
      render: (hostname: string | null) => hostname || '-',
    },
    {
      title: 'Source IP',
      dataIndex: 'source_ip',
      key: 'source_ip',
      width: 140,
    },
    {
      title: 'Správa',
      dataIndex: 'message',
      key: 'message',
      ellipsis: true,
      render: (message: string) => (
        <span style={{ fontFamily: 'monospace', fontSize: 12 }}>{message}</span>
      ),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={2}>Syslog</Title>

        {stats && (
          <Row gutter={16} style={{ marginBottom: 24 }}>
            <Col span={6}>
              <Card>
                <Statistic
                  title="Celkom správ"
                  value={stats.total_messages}
                  suffix={`(${filters.hours}h)`}
                />
              </Card>
            </Col>
            {Object.entries(stats.severity_counts).slice(0, 3).map(([severity, count]) => (
              <Col span={6} key={severity}>
                <Card>
                  <Statistic
                    title={severity.toUpperCase()}
                    value={count}
                    valueStyle={{ color: severity === 'error' || severity === 'critical' ? '#cf1322' : undefined }}
                  />
                </Card>
              </Col>
            ))}
          </Row>
        )}

        <Space direction="vertical" style={{ width: '100%' }} size="middle">
          <Space wrap>
            <Search
              placeholder="Hľadať v logoch..."
              allowClear
              enterButton={<SearchOutlined />}
              onSearch={handleSearch}
              style={{ width: 300 }}
            />

            <Select
              placeholder="Závažnosť"
              allowClear
              style={{ width: 150 }}
              value={filters.severity}
              onChange={(value) => setFilters({ ...filters, severity: value })}
            >
              <Select.Option value="emergency">Emergency</Select.Option>
              <Select.Option value="alert">Alert</Select.Option>
              <Select.Option value="critical">Critical</Select.Option>
              <Select.Option value="error">Error</Select.Option>
              <Select.Option value="warning">Warning</Select.Option>
              <Select.Option value="notice">Notice</Select.Option>
              <Select.Option value="info">Info</Select.Option>
              <Select.Option value="debug">Debug</Select.Option>
            </Select>

            <Select
              placeholder="Časové obdobie"
              style={{ width: 150 }}
              value={filters.hours}
              onChange={(value) => setFilters({ ...filters, hours: value })}
            >
              <Select.Option value={1}>Posledná hodina</Select.Option>
              <Select.Option value={6}>Posledných 6 hodín</Select.Option>
              <Select.Option value={24}>Posledných 24 hodín</Select.Option>
              <Select.Option value={72}>Posledné 3 dni</Select.Option>
              <Select.Option value={168}>Posledný týždeň</Select.Option>
            </Select>

            <Button icon={<ReloadOutlined />} onClick={handleRefresh}>
              Obnoviť
            </Button>
          </Space>
        </Space>
      </div>

      <Table
        dataSource={logs}
        columns={columns}
        rowKey="id"
        loading={loading}
        pagination={{
          pageSize: 50,
          showTotal: (total) => `Celkom ${total} záznamov`,
          showSizeChanger: true,
          pageSizeOptions: ['20', '50', '100', '200'],
        }}
        scroll={{ x: 1200 }}
        size="small"
      />
    </div>
  );
}
