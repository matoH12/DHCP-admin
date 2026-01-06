import { useEffect, useState } from 'react';
import { Modal, Form, Input, Select, Switch, Button, message } from 'antd';
import { apiService } from '../../services/api';
import type { User } from '../../types/api';

interface UserFormModalProps {
  open: boolean;
  user: User | null;
  onCancel: () => void;
  onSuccess: () => void;
}

export function UserFormModal({ open, user, onCancel, onSuccess }: UserFormModalProps) {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (open) {
      if (user) {
        form.setFieldsValue({
          username: user.username,
          email: user.email,
          role: user.role,
          is_active: user.is_active,
        });
      } else {
        form.resetFields();
        form.setFieldsValue({
          role: 'RO',
          is_active: true,
        });
      }
    }
  }, [open, user, form]);

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      setLoading(true);

      if (user) {
        // Update existing user
        const updateData: { email?: string; password?: string; is_active?: boolean; role?: 'RO' | 'RW' | 'ADMIN' } = {
          email: values.email,
          is_active: values.is_active,
          role: values.role,
        };

        // Only include password if it was provided
        if (values.password) {
          updateData.password = values.password;
        }

        await apiService.updateUser(user.id, updateData);
        message.success('Používateľ bol aktualizovaný');
      } else {
        // Create new user
        await apiService.createUser({
          username: values.username,
          email: values.email,
          password: values.password,
          role: values.role,
        });
        message.success('Používateľ bol vytvorený');
      }

      onSuccess();
    } catch (error: unknown) {
      if (error && typeof error === 'object' && 'response' in error) {
        const response = (error as { response?: { data?: { detail?: string } } }).response;
        message.error(response?.data?.detail || 'Nepodarilo sa uložiť používateľa');
      } else if (error && typeof error === 'object' && 'errorFields' in error) {
        // Validation error
      } else {
        message.error('Nepodarilo sa uložiť používateľa');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      title={user ? 'Upraviť používateľa' : 'Pridať používateľa'}
      open={open}
      onCancel={onCancel}
      footer={[
        <Button key="cancel" onClick={onCancel}>
          Zrušiť
        </Button>,
        <Button key="submit" type="primary" loading={loading} onClick={handleSubmit}>
          {user ? 'Uložiť' : 'Vytvoriť'}
        </Button>,
      ]}
      width={600}
    >
      <Form
        form={form}
        layout="vertical"
      >
        <Form.Item
          label="Používateľské meno"
          name="username"
          rules={[
            { required: true, message: 'Používateľské meno je povinné' },
            { min: 3, message: 'Používateľské meno musí mať aspoň 3 znaky' },
          ]}
        >
          <Input placeholder="napr. jan.novak" disabled={!!user} />
        </Form.Item>

        <Form.Item
          label="Email"
          name="email"
          rules={[
            { required: true, message: 'Email je povinný' },
            { type: 'email', message: 'Neplatný formát emailu' },
          ]}
        >
          <Input placeholder="jan.novak@example.com" />
        </Form.Item>

        <Form.Item
          label="Heslo"
          name="password"
          rules={[
            { required: !user, message: 'Heslo je povinné' },
            { min: 6, message: 'Heslo musí mať aspoň 6 znakov' },
          ]}
          extra={user ? 'Nechajte prázdne, ak nechcete zmeniť heslo' : undefined}
        >
          <Input.Password placeholder="Zadajte heslo" />
        </Form.Item>

        <Form.Item
          label="Rola"
          name="role"
          rules={[{ required: true, message: 'Rola je povinná' }]}
          extra="RO = Len čítanie, RW = Čítanie a zápis, ADMIN = Plný prístup"
        >
          <Select>
            <Select.Option value="RO">Len Čítanie (RO)</Select.Option>
            <Select.Option value="RW">Čítanie a Zápis (RW)</Select.Option>
            <Select.Option value="ADMIN">Administrátor (ADMIN)</Select.Option>
          </Select>
        </Form.Item>

        <Form.Item
          label="Aktívny"
          name="is_active"
          valuePropName="checked"
        >
          <Switch />
        </Form.Item>
      </Form>
    </Modal>
  );
}
