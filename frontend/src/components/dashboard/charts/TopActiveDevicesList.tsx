import { Card, List, Tag, Spin, Empty, Badge, Alert } from 'antd';
import { useState, useEffect } from 'react';
import { LaptopOutlined } from '@ant-design/icons';
import { apiService } from '../../../services/api';
import type { TopActiveDevicesResponse, TopActiveDevice } from '../../../types/api';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';
import 'dayjs/locale/sk';

dayjs.extend(relativeTime);
dayjs.locale('sk');

export function TopActiveDevicesList() {
  const [data, setData] = useState<TopActiveDevicesResponse | null>(null);
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
      const result = await apiService.getTopActiveDevices(10, 7);
      setData(result);
    } catch (err) {
      console.error('Failed to load top active devices:', err);
      setError('Nepodarilo sa načítať aktívne zariadenia');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Card title="Najaktívnejšie Zariadenia (7 dní)">
        <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}>
          <Spin size="large" />
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card title="Najaktívnejšie Zariadenia (7 dní)">
        <Alert message={error} type="error" showIcon />
      </Card>
    );
  }

  if (!data || data.data.length === 0) {
    return (
      <Card title="Najaktívnejšie Zariadenia (7 dní)">
        <Empty description="Žiadna aktivita zariadení" />
      </Card>
    );
  }

  return (
    <Card title="Najaktívnejšie Zariadenia (7 dní)">
      <List
        itemLayout="horizontal"
        dataSource={data.data}
        renderItem={(device: TopActiveDevice, index: number) => (
          <List.Item>
            <List.Item.Meta
              avatar={
                <Badge
                  count={index + 1}
                  style={{
                    backgroundColor: index < 3 ? '#52c41a' : '#1890ff'
                  }}
                >
                  <LaptopOutlined style={{ fontSize: 24, color: '#1890ff' }} />
                </Badge>
              }
              title={
                <div>
                  <strong>{device.hostname}</strong>
                  <Tag color="blue" style={{ marginLeft: 8 }}>
                    {device.activity_count} aktivít
                  </Tag>
                </div>
              }
              description={
                <div>
                  <div style={{ marginBottom: 4 }}>
                    <span style={{ color: '#666' }}>IP:</span> {device.ip_address}
                    {' '}<span style={{ color: '#999' }}>|</span>{' '}
                    <span style={{ color: '#666' }}>MAC:</span> {device.mac_address}
                  </div>
                  <div>
                    {device.range_name && (
                      <Tag color="default" style={{ marginRight: 8 }}>
                        {device.range_name}
                      </Tag>
                    )}
                    {device.last_seen && (
                      <span style={{ fontSize: 12, color: '#888' }}>
                        Naposledy: {dayjs(device.last_seen).fromNow()}
                      </span>
                    )}
                  </div>
                </div>
              }
            />
          </List.Item>
        )}
      />
    </Card>
  );
}
