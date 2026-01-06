import { useEffect, useState } from 'react';
import {
  Table,
  Button,
  Input,
  Space,
  Tag,
  Typography,
  message,
  Modal,
  Popconfirm,
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  SearchOutlined,
} from '@ant-design/icons';
import { apiService } from '../../services/api';
import type { Device } from '../../types/api';
import { DeviceFormModal } from './DeviceFormModal';
import { useDHCPStatus } from '../../contexts/DHCPStatusContext';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';
import 'dayjs/locale/sk';

dayjs.extend(relativeTime);
dayjs.locale('sk');

const { Title } = Typography;

export function DevicesPage() {
  const [devices, setDevices] = useState<Device[]>([]);
  const [filteredDevices, setFilteredDevices] = useState<Device[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingDevice, setEditingDevice] = useState<Device | null>(null);
  const { checkPendingChanges } = useDHCPStatus();

  useEffect(() => {
    loadDevices();
  }, []);

  useEffect(() => {
    if (searchText) {
      const filtered = devices.filter(
        (device) =>
          device.hostname.toLowerCase().includes(searchText.toLowerCase()) ||
          device.ip_address.includes(searchText) ||
          device.mac_address.toLowerCase().includes(searchText.toLowerCase()) ||
          device.description?.toLowerCase().includes(searchText.toLowerCase())
      );
      setFilteredDevices(filtered);
    } else {
      setFilteredDevices(devices);
    }
  }, [searchText, devices]);

  const loadDevices = async () => {
    setLoading(true);
    try {
      const data = await apiService.getDevices();
      setDevices(data);
      setFilteredDevices(data);
    } catch (error) {
      message.error('Nepodarilo sa načítať zariadenia');
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = () => {
    setEditingDevice(null);
    setIsModalOpen(true);
  };

  const handleEdit = (device: Device) => {
    setEditingDevice(device);
    setIsModalOpen(true);
  };

  const handleDelete = async (id: number) => {
    try {
      await apiService.deleteDevice(id);
      message.success('Zariadenie bolo zmazané');
      loadDevices();
      checkPendingChanges();
    } catch (error) {
      message.error('Nepodarilo sa zmazať zariadenie');
    }
  };

  const handleFormSubmit = async () => {
    setIsModalOpen(false);
    await loadDevices();
    checkPendingChanges();
  };

  const columns = [
    {
      title: 'Hostname',
      dataIndex: 'hostname',
      key: 'hostname',
      sorter: (a: Device, b: Device) => a.hostname.localeCompare(b.hostname),
    },
    {
      title: 'IP Adresa',
      dataIndex: 'ip_address',
      key: 'ip_address',
      sorter: (a: Device, b: Device) => {
        const aNum = a.ip_address.split('.').map(Number);
        const bNum = b.ip_address.split('.').map(Number);
        for (let i = 0; i < 4; i++) {
          if (aNum[i] !== bNum[i]) return aNum[i] - bNum[i];
        }
        return 0;
      },
    },
    {
      title: 'MAC Adresa',
      dataIndex: 'mac_address',
      key: 'mac_address',
    },
    {
      title: 'Popis',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
    },
    {
      title: 'Stav',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (isActive: boolean) => (
        <Tag color={isActive ? 'green' : 'red'}>
          {isActive ? 'Aktívne' : 'Neaktívne'}
        </Tag>
      ),
      filters: [
        { text: 'Aktívne', value: true },
        { text: 'Neaktívne', value: false },
      ],
      onFilter: (value: boolean | string | number, record: Device) => record.is_active === value,
    },
    {
      title: 'Vytvorené',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => dayjs(date).format('DD.MM.YYYY HH:mm'),
      sorter: (a: Device, b: Device) =>
        new Date(a.created_at).getTime() - new Date(b.created_at).getTime(),
    },
    {
      title: 'Posledne videný',
      dataIndex: 'last_seen',
      key: 'last_seen',
      render: (date: string | null) => {
        if (!date) {
          return <Tag color="default">Nikdy</Tag>;
        }
        const lastSeen = dayjs(date);
        const now = dayjs();
        const diffMinutes = now.diff(lastSeen, 'minute');

        // Color coding based on how recent
        let color = 'red'; // Not seen recently (> 24h)
        if (diffMinutes < 60) {
          color = 'green'; // Seen in last hour
        } else if (diffMinutes < 1440) {
          color = 'orange'; // Seen in last 24 hours
        }

        return (
          <Tag color={color} title={lastSeen.format('DD.MM.YYYY HH:mm:ss')}>
            {lastSeen.fromNow()}
          </Tag>
        );
      },
      sorter: (a: Device, b: Device) => {
        if (!a.last_seen && !b.last_seen) return 0;
        if (!a.last_seen) return 1;
        if (!b.last_seen) return -1;
        return new Date(b.last_seen).getTime() - new Date(a.last_seen).getTime();
      },
    },
    {
      title: 'Akcie',
      key: 'actions',
      render: (_: unknown, record: Device) => (
        <Space>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            Upraviť
          </Button>
          <Popconfirm
            title="Naozaj chcete zmazať toto zariadenie?"
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
        <Title level={2}>Zariadenia</Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
          Pridať zariadenie
        </Button>
      </div>

      <Input
        placeholder="Vyhľadať hostname, IP, MAC adresu alebo popis..."
        prefix={<SearchOutlined />}
        value={searchText}
        onChange={(e) => setSearchText(e.target.value)}
        style={{ marginBottom: 16, maxWidth: 400 }}
        allowClear
      />

      <Table
        dataSource={filteredDevices}
        columns={columns}
        rowKey="id"
        loading={loading}
        pagination={{
          pageSize: 20,
          showSizeChanger: true,
          showTotal: (total) => `Celkom ${total} zariadení`,
        }}
      />

      <DeviceFormModal
        open={isModalOpen}
        device={editingDevice}
        onCancel={() => setIsModalOpen(false)}
        onSuccess={handleFormSubmit}
      />
    </div>
  );
}
