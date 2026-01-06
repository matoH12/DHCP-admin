import { useEffect, useState } from 'react';
import {
  Table,
  Input,
  Typography,
  message,
  Space,
  Card,
  Row,
  Col,
  Statistic,
  Button,
  Modal,
  Alert,
  Select,
} from 'antd';
import {
  SearchOutlined,
  ReloadOutlined,
  DeleteOutlined,
  ExclamationCircleOutlined,
  SortAscendingOutlined,
  SortDescendingOutlined,
} from '@ant-design/icons';
import { apiService } from '../../services/api';

const { Title } = Typography;
const { Search } = Input;

interface LogLine {
  line_number: number;
  content: string;
  timestamp: string | null;
  event_type: string | null;
}

interface DHCPLogsResponse {
  logs: LogLine[];
  total_lines: number;
  file_info: {
    size_bytes: number;
    modified: string;
  };
  log_file: string;
  order: string;
  event_type: string | null;
}

type EventType = 'DISCOVER' | 'OFFER' | 'REQUEST' | 'ACK' | 'NAK' | 'RELEASE' | 'INFORM' | 'DECLINE' | null;

export function LogsPage() {
  const [logsData, setLogsData] = useState<DHCPLogsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [eventTypeFilter, setEventTypeFilter] = useState<EventType>(null);

  useEffect(() => {
    loadLogs();
    // Auto-refresh every 15 seconds
    const interval = setInterval(loadLogs, 15000);
    return () => clearInterval(interval);
  }, [searchTerm, sortOrder, eventTypeFilter]);

  const loadLogs = async () => {
    setLoading(true);
    try {
      const data = await apiService.getDHCPLogs({
        lines: 500,
        ...(searchTerm && { search: searchTerm }),
        order: sortOrder,
        ...(eventTypeFilter && { event_type: eventTypeFilter }),
      });
      setLogsData(data);
    } catch (error) {
      message.error('Nepodarilo sa načítať DHCP logy');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (value: string) => {
    setSearchTerm(value);
  };

  const handleRefresh = () => {
    loadLogs();
    message.success('Logy obnovené');
  };

  const handleClearLogs = () => {
    Modal.confirm({
      title: 'Zmazať všetky DHCP logy?',
      icon: <ExclamationCircleOutlined />,
      content: 'Táto akcia vymaže všetky logy zo súborov. Túto akciu nie je možné vrátiť späť.',
      okText: 'Zmazať',
      okType: 'danger',
      cancelText: 'Zrušiť',
      onOk: async () => {
        try {
          await apiService.clearDHCPLogs();
          message.success('Logy boli úspešne vymazané');
          loadLogs();
        } catch (error) {
          message.error('Nepodarilo sa zmazať logy');
          console.error(error);
        }
      },
    });
  };

  const columns = [
    {
      title: '#',
      dataIndex: 'line_number',
      key: 'line_number',
      width: 80,
      render: (num: number) => <span style={{ color: '#999' }}>{num}</span>,
    },
    {
      title: 'Čas',
      dataIndex: 'timestamp',
      key: 'timestamp',
      width: 180,
      render: (timestamp: string | null) => timestamp || '-',
    },
    {
      title: 'Obsah logu',
      dataIndex: 'content',
      key: 'content',
      ellipsis: false,
      render: (content: string) => (
        <pre style={{
          fontFamily: 'monospace',
          fontSize: 12,
          margin: 0,
          whiteSpace: 'pre-wrap',
          wordBreak: 'break-word',
        }}>
          {content}
        </pre>
      ),
    },
  ];

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={2}>DHCP Server Logy</Title>

        {logsData && logsData.file_info && (
          <Row gutter={16} style={{ marginBottom: 24 }}>
            <Col span={8}>
              <Card>
                <Statistic
                  title="Počet riadkov"
                  value={logsData.total_lines}
                />
              </Card>
            </Col>
            <Col span={8}>
              <Card>
                <Statistic
                  title="Veľkosť súboru"
                  value={formatFileSize(logsData.file_info.size_bytes)}
                />
              </Card>
            </Col>
            <Col span={8}>
              <Card>
                <Statistic
                  title="Posledná zmena"
                  value={new Date(logsData.file_info.modified).toLocaleString('sk-SK')}
                  valueStyle={{ fontSize: 16 }}
                />
              </Card>
            </Col>
          </Row>
        )}

        <Alert
          message="Automatické obnovenie každých 15 sekúnd"
          type="info"
          showIcon
          closable
          style={{ marginBottom: 16 }}
        />

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
              value={eventTypeFilter}
              onChange={setEventTypeFilter}
              placeholder="Typ DHCP udalosti"
              allowClear
              style={{ width: 200 }}
            >
              <Select.Option value="DISCOVER">🔍 DISCOVER</Select.Option>
              <Select.Option value="OFFER">💡 OFFER</Select.Option>
              <Select.Option value="REQUEST">📨 REQUEST</Select.Option>
              <Select.Option value="ACK">✅ ACK</Select.Option>
              <Select.Option value="NAK">❌ NAK</Select.Option>
              <Select.Option value="RELEASE">🔓 RELEASE</Select.Option>
              <Select.Option value="INFORM">ℹ️ INFORM</Select.Option>
              <Select.Option value="DECLINE">⛔ DECLINE</Select.Option>
            </Select>

            <Select
              value={sortOrder}
              onChange={setSortOrder}
              style={{ width: 180 }}
            >
              <Select.Option value="desc">
                <SortDescendingOutlined /> Najnovšie prvé
              </Select.Option>
              <Select.Option value="asc">
                <SortAscendingOutlined /> Najstaršie prvé
              </Select.Option>
            </Select>

            <Button icon={<ReloadOutlined />} onClick={handleRefresh}>
              Obnoviť
            </Button>

            <Button
              danger
              icon={<DeleteOutlined />}
              onClick={handleClearLogs}
            >
              Zmazať všetky logy
            </Button>
          </Space>
        </Space>
      </div>

      <Table
        dataSource={logsData?.logs || []}
        columns={columns}
        rowKey="line_number"
        loading={loading}
        pagination={{
          pageSize: 100,
          showTotal: (total) => `Celkom ${total} riadkov`,
          showSizeChanger: true,
          pageSizeOptions: ['50', '100', '200', '500'],
        }}
        scroll={{ x: 1000 }}
        size="small"
      />
    </div>
  );
}
