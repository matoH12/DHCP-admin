import { useEffect, useState } from 'react';
import {
  Table,
  Button,
  Space,
  Tag,
  Typography,
  message,
  Popconfirm,
  Progress,
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
} from '@ant-design/icons';
import { apiService } from '../../services/api';
import type { IPRange, IPRangeStats } from '../../types/api';
import { RangeFormModal } from './RangeFormModal';

const { Title } = Typography;

interface RangeWithStats extends IPRange {
  stats?: IPRangeStats;
}

export function RangesPage() {
  const [ranges, setRanges] = useState<RangeWithStats[]>([]);
  const [loading, setLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingRange, setEditingRange] = useState<IPRange | null>(null);

  useEffect(() => {
    loadRanges();
  }, []);

  const loadRanges = async () => {
    setLoading(true);
    try {
      const data = await apiService.getRanges();

      // Load stats for each range
      const rangesWithStats = await Promise.all(
        data.map(async (range) => {
          try {
            const stats = await apiService.getRangeStats(range.id);
            return { ...range, stats };
          } catch {
            return range;
          }
        })
      );

      setRanges(rangesWithStats);
    } catch (error) {
      message.error('Nepodarilo sa načítať IP rozsahy');
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = () => {
    setEditingRange(null);
    setIsModalOpen(true);
  };

  const handleEdit = (range: IPRange) => {
    setEditingRange(range);
    setIsModalOpen(true);
  };

  const handleDelete = async (id: number) => {
    try {
      await apiService.deleteRange(id);
      message.success('IP rozsah bol zmazaný');
      loadRanges();
    } catch (error) {
      message.error('Nepodarilo sa zmazať IP rozsah');
    }
  };

  const handleFormSubmit = async () => {
    setIsModalOpen(false);
    await loadRanges();
  };

  const columns = [
    {
      title: 'Názov',
      dataIndex: 'name',
      key: 'name',
      sorter: (a: IPRange, b: IPRange) => a.name.localeCompare(b.name),
    },
    {
      title: 'Sieť',
      key: 'network',
      render: (_: unknown, record: IPRange) => `${record.network_address}/${record.cidr}`,
    },
    {
      title: 'Gateway',
      dataIndex: 'gateway',
      key: 'gateway',
    },
    {
      title: 'DNS',
      dataIndex: 'dns_servers',
      key: 'dns_servers',
      render: (dns: string[]) => dns.join(', '),
    },
    {
      title: 'Doména',
      dataIndex: 'domain_name',
      key: 'domain_name',
    },
    {
      title: 'DHCP Pool',
      key: 'dhcp_pool',
      render: (_: unknown, record: IPRange) => {
        if (record.pool_start && record.pool_end) {
          return `${record.pool_start} - ${record.pool_end}`;
        }
        return '-';
      },
    },
    {
      title: 'Využitie',
      key: 'utilization',
      render: (_: unknown, record: RangeWithStats) => {
        if (!record.stats) return '-';
        return (
          <div>
            <Progress
              percent={Number(record.stats.utilization_percent.toFixed(1))}
              status={record.stats.utilization_percent > 80 ? 'exception' : 'active'}
              size="small"
            />
            <div style={{ fontSize: 12, color: '#666', marginTop: 4 }}>
              {record.stats.assigned_ips} / {record.stats.total_usable_ips} priradených
            </div>
          </div>
        );
      },
    },
    {
      title: 'Stav',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (isActive: boolean) => (
        <Tag color={isActive ? 'green' : 'red'}>
          {isActive ? 'Aktívny' : 'Neaktívny'}
        </Tag>
      ),
    },
    {
      title: 'Akcie',
      key: 'actions',
      render: (_: unknown, record: IPRange) => (
        <Space>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            Upraviť
          </Button>
          <Popconfirm
            title="Naozaj chcete zmazať tento rozsah?"
            description="Toto zmaže aj všetky zariadenia v tomto rozsahu!"
            onConfirm={() => handleDelete(record.id)}
            okText="Áno"
            cancelText="Nie"
          >
            <Button type="link" danger icon={<DeleteOutlined />}>
              Zmazať
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <Title level={2}>IP Rozsahy</Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
          Pridať rozsah
        </Button>
      </div>

      <Table
        dataSource={ranges}
        columns={columns}
        rowKey="id"
        loading={loading}
        pagination={{
          pageSize: 10,
          showTotal: (total) => `Celkom ${total} rozsahov`,
        }}
      />

      <RangeFormModal
        open={isModalOpen}
        range={editingRange}
        onCancel={() => setIsModalOpen(false)}
        onSuccess={handleFormSubmit}
      />
    </div>
  );
}
