import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Form, Input, Button, Card, message, Typography } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useAuth } from '../../hooks/useAuth';
import type { LoginRequest } from '../../types/api';

const { Title } = Typography;

export function LoginPage() {
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const onFinish = async (values: LoginRequest) => {
    setLoading(true);
    try {
      await login(values);
      message.success('Prihlásenie úspešné!');
      navigate('/');
    } catch (error) {
      message.error('Nesprávne prihlasovacie údaje');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    }}>
      <Card style={{ width: 400, boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <Title level={2}>DHCP Admin</Title>
          <p style={{ color: '#666' }}>Prihlásenie do systému</p>
        </div>

        <Form
          name="login"
          onFinish={onFinish}
          autoComplete="off"
          size="large"
        >
          <Form.Item
            name="username"
            rules={[{ required: true, message: 'Zadajte používateľské meno!' }]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="Používateľské meno"
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ required: true, message: 'Zadajte heslo!' }]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="Heslo"
            />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block>
              Prihlásiť sa
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
}
