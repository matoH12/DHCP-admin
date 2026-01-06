import { useState, useEffect } from 'react';
import { Button, Card, Typography, Space, message, Modal, Table } from 'antd';
import {
  FileTextOutlined,
  DownloadOutlined,
  EyeOutlined,
  SyncOutlined,
} from '@ant-design/icons';
import { apiService } from '../../services/api';
import type { DHCPConfig } from '../../types/api';
import dayjs from 'dayjs';

const { Title, Paragraph } = Typography;

export function DHCPPage() {
  const [activeConfig, setActiveConfig] = useState<DHCPConfig | null>(null);
  const [history, setHistory] = useState<DHCPConfig[]>([]);
  const [loading, setLoading] = useState(false);
  const [previewVisible, setPreviewVisible] = useState(false);
  const [previewContent, setPreviewContent] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [config, historyData] = await Promise.all([
        apiService.getActiveDHCPConfig().catch(() => null),
        apiService.getDHCPHistory(),
      ]);
      setActiveConfig(config);
      setHistory(historyData);
    } catch (error) {
      message.error('Nepodarilo sa načítať údaje');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async () => {
    setLoading(true);
    try {
      await apiService.generateDHCPConfig();
      message.success('DHCP konfigurácia bola vygenerovaná');
      await loadData();
    } catch (error) {
      message.error('Nepodarilo sa vygenerovať konfiguráciu');
    } finally {
      setLoading(false);
    }
  };

  const handlePreview = async () => {
    try {
      const content = await apiService.previewDHCPConfig();
      setPreviewContent(content);
      setPreviewVisible(true);
    } catch (error) {
      message.error('Nepodarilo sa zobraziť náhľad');
    }
  };

  const handleDownload = async () => {
    try {
      const blob = await apiService.downloadDHCPConfig();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'dhcpd.conf';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      message.success('Súbor bol stiahnutý');
    } catch (error) {
      message.error('Nepodarilo sa stiahnuť súbor');
    }
  };

  const columns = [
    {
      title: 'Verzia',
      dataIndex: 'version',
      key: 'version',
    },
    {
      title: 'Vygenerované',
      dataIndex: 'generated_at',
      key: 'generated_at',
      render: (date: string) => dayjs(date).format('DD.MM.YYYY HH:mm:ss'),
    },
    {
      title: 'Cesta k súboru',
      dataIndex: 'file_path',
      key: 'file_path',
    },
    {
      title: 'Stav',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (isActive: boolean) => (isActive ? '✅ Aktívna' : ''),
    },
  ];

  return (
    <div>
      <Title level={2}>DHCP Konfigurácia</Title>

      <Card style={{ marginBottom: 16 }}>
        <Title level={4}>Aktívna Konfigurácia</Title>
        {activeConfig ? (
          <div>
            <Paragraph>
              <strong>Verzia:</strong> {activeConfig.version}
            </Paragraph>
            <Paragraph>
              <strong>Vygenerované:</strong>{' '}
              {dayjs(activeConfig.generated_at).format('DD.MM.YYYY HH:mm:ss')}
            </Paragraph>
            <Paragraph>
              <strong>Cesta:</strong> {activeConfig.file_path}
            </Paragraph>
          </div>
        ) : (
          <Paragraph type="secondary">Žiadna konfigurácia nie je aktívna</Paragraph>
        )}

        <Space style={{ marginTop: 16 }}>
          <Button
            type="primary"
            icon={<SyncOutlined />}
            onClick={handleGenerate}
            loading={loading}
          >
            Generovať novú konfiguráciu
          </Button>
          <Button icon={<EyeOutlined />} onClick={handlePreview}>
            Náhľad
          </Button>
          <Button
            icon={<DownloadOutlined />}
            onClick={handleDownload}
            disabled={!activeConfig}
          >
            Stiahnuť
          </Button>
        </Space>
      </Card>

      <Card title="História Konfigurácií">
        <Table
          dataSource={history}
          columns={columns}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      <Modal
        title="Náhľad DHCP Konfigurácie"
        open={previewVisible}
        onCancel={() => setPreviewVisible(false)}
        width={800}
        footer={[
          <Button key="close" onClick={() => setPreviewVisible(false)}>
            Zavrieť
          </Button>,
        ]}
      >
        <pre
          style={{
            background: '#f5f5f5',
            padding: 16,
            borderRadius: 4,
            maxHeight: 500,
            overflow: 'auto',
          }}
        >
          {previewContent}
        </pre>
      </Modal>
    </div>
  );
}
