import { useEffect, useState } from 'react';
import {
  Table,
  Button,
  Space,
  Tag,
  Typography,
  message,
  Popconfirm,
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
} from '@ant-design/icons';
import { apiService } from '../../services/api';
import type { User } from '../../types/api';
import { UserFormModal } from './UserFormModal';

const { Title } = Typography;

const getRoleColor = (role: string) => {
  switch (role) {
    case 'ADMIN':
      return 'red';
    case 'RW':
      return 'orange';
    case 'RO':
      return 'blue';
    default:
      return 'default';
  }
};

const getRoleLabel = (role: string) => {
  switch (role) {
    case 'ADMIN':
      return 'Admin';
    case 'RW':
      return 'Čítanie/Zápis';
    case 'RO':
      return 'Len Čítanie';
    default:
      return role;
  }
};

export function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    setLoading(true);
    try {
      const data = await apiService.getUsers();
      setUsers(data);
    } catch (error) {
      message.error('Nepodarilo sa načítať používateľov');
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = () => {
    setEditingUser(null);
    setIsModalOpen(true);
  };

  const handleEdit = (user: User) => {
    setEditingUser(user);
    setIsModalOpen(true);
  };

  const handleDelete = async (id: number) => {
    try {
      await apiService.deleteUser(id);
      message.success('Používateľ bol zmazaný');
      loadUsers();
    } catch (error) {
      message.error('Nepodarilo sa zmazať používateľa');
    }
  };

  const handleFormSubmit = async () => {
    setIsModalOpen(false);
    await loadUsers();
  };

  const columns = [
    {
      title: 'Používateľské meno',
      dataIndex: 'username',
      key: 'username',
      sorter: (a: User, b: User) => a.username.localeCompare(b.username),
    },
    {
      title: 'Email',
      dataIndex: 'email',
      key: 'email',
    },
    {
      title: 'Rola',
      dataIndex: 'role',
      key: 'role',
      render: (role: string) => (
        <Tag color={getRoleColor(role)}>
          {getRoleLabel(role)}
        </Tag>
      ),
      filters: [
        { text: 'Admin', value: 'ADMIN' },
        { text: 'Čítanie/Zápis', value: 'RW' },
        { text: 'Len Čítanie', value: 'RO' },
      ],
      onFilter: (value: string | number | boolean, record: User) => record.role === value,
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
      title: 'Vytvorený',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => new Date(date).toLocaleString('sk-SK'),
    },
    {
      title: 'Akcie',
      key: 'actions',
      render: (_: unknown, record: User) => (
        <Space>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            Upraviť
          </Button>
          <Popconfirm
            title="Naozaj chcete zmazať tohto používateľa?"
            description="Táto akcia je nevratná!"
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
        <Title level={2}>Používatelia</Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
          Pridať používateľa
        </Button>
      </div>

      <Table
        dataSource={users}
        columns={columns}
        rowKey="id"
        loading={loading}
        pagination={{
          pageSize: 10,
          showTotal: (total) => `Celkom ${total} používateľov`,
        }}
      />

      <UserFormModal
        open={isModalOpen}
        user={editingUser}
        onCancel={() => setIsModalOpen(false)}
        onSuccess={handleFormSubmit}
      />
    </div>
  );
}
