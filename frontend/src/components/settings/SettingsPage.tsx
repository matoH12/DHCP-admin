import { useEffect, useState } from 'react';
import {
  Typography,
  Card,
  Form,
  InputNumber,
  Switch,
  Button,
  message,
  Divider,
  Space,
  Alert,
  Row,
  Col,
} from 'antd';
import { SaveOutlined, ApiOutlined, FileTextOutlined } from '@ant-design/icons';
import { apiService } from '../../services/api';
import type { Setting } from '../../types/api';

const { Title, Paragraph, Text } = Typography;

export function SettingsPage() {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [settings, setSettings] = useState<Setting[]>([]);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    setLoading(true);
    try {
      const data = await apiService.getSettings();
      setSettings(data);

      // Set form values
      const formData: Record<string, any> = {};
      data.forEach(setting => {
        if (setting.key === 'syslog_retention_days') {
          formData.retentionDays = parseInt(setting.value);
        } else if (setting.key === 'syslog_cleanup_enabled') {
          formData.cleanupEnabled = setting.value === 'true';
        } else if (setting.key === 'syslog_cleanup_hour') {
          formData.cleanupHour = parseInt(setting.value);
        }
      });
      form.setFieldsValue(formData);
    } catch (error) {
      message.error('Nepodarilo sa načítať nastavenia');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      setSaving(true);

      // Update each setting
      await Promise.all([
        apiService.updateSetting('syslog_retention_days', {
          value: values.retentionDays.toString()
        }),
        apiService.updateSetting('syslog_cleanup_enabled', {
          value: values.cleanupEnabled ? 'true' : 'false'
        }),
        apiService.updateSetting('syslog_cleanup_hour', {
          value: values.cleanupHour.toString()
        }),
      ]);

      message.success('Nastavenia boli uložené');
      loadSettings();
    } catch (error: any) {
      if (error.response?.data?.detail) {
        message.error(error.response.data.detail);
      } else {
        message.error('Nepodarilo sa uložiť nastavenia');
      }
    } finally {
      setSaving(false);
    }
  };

  const getRetentionInfo = () => {
    const days = form.getFieldValue('retentionDays');
    if (!days) return '';

    const months = Math.floor(days / 30);
    const remainingDays = days % 30;

    if (months > 0) {
      return remainingDays > 0
        ? `${months} mesiacov a ${remainingDays} dní`
        : `${months} mesiacov`;
    }
    return `${days} dní`;
  };

  const openSwaggerDocs = () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      message.error('Nie ste prihlásený');
      return;
    }

    // Open Swagger UI in new window with token in Authorization header
    const backendUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    const docsUrl = `${backendUrl}/api/docs`;

    // Create a form to POST the request with Authorization header
    const form = document.createElement('form');
    form.method = 'GET';
    form.action = docsUrl;
    form.target = '_blank';

    // We'll use a different approach - open in new window and set headers via fetch
    const newWindow = window.open('about:blank', '_blank');
    if (newWindow) {
      fetch(docsUrl, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
        .then(response => response.text())
        .then(html => {
          if (newWindow) {
            newWindow.document.write(html);
            newWindow.document.close();
          }
        })
        .catch(() => {
          message.error('Nepodarilo sa otvoriť Swagger dokumentáciu');
          if (newWindow) newWindow.close();
        });
    }
  };

  const openRedocDocs = () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      message.error('Nie ste prihlásený');
      return;
    }

    const backendUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    const redocUrl = `${backendUrl}/api/redoc`;

    const newWindow = window.open('about:blank', '_blank');
    if (newWindow) {
      fetch(redocUrl, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
        .then(response => response.text())
        .then(html => {
          if (newWindow) {
            newWindow.document.write(html);
            newWindow.document.close();
          }
        })
        .catch(() => {
          message.error('Nepodarilo sa otvoriť ReDoc dokumentáciu');
          if (newWindow) newWindow.close();
        });
    }
  };

  return (
    <div>
      <Title level={2}>Nastavenia</Title>

      <Card
        title="API Dokumentácia"
        style={{ maxWidth: 800, marginBottom: 24 }}
      >
        <Alert
          message="Interaktívna API dokumentácia"
          description="Prístup k Swagger UI a ReDoc dokumentácii pre REST API endpointy. Dokumentácia je chránená prihlásením a automaticky obsahuje váš autentifikačný token."
          type="info"
          showIcon
          style={{ marginBottom: 24 }}
        />

        <Row gutter={16}>
          <Col xs={24} sm={12}>
            <Card
              hoverable
              onClick={openSwaggerDocs}
              style={{ cursor: 'pointer', textAlign: 'center' }}
            >
              <ApiOutlined style={{ fontSize: 48, color: '#1890ff', marginBottom: 16 }} />
              <Title level={4}>Swagger UI</Title>
              <Paragraph type="secondary">
                Interaktívna dokumentácia s možnosťou testovať API endpointy priamo v prehliadači
              </Paragraph>
              <Button type="primary" icon={<ApiOutlined />}>
                Otvoriť Swagger
              </Button>
            </Card>
          </Col>

          <Col xs={24} sm={12}>
            <Card
              hoverable
              onClick={openRedocDocs}
              style={{ cursor: 'pointer', textAlign: 'center' }}
            >
              <FileTextOutlined style={{ fontSize: 48, color: '#52c41a', marginBottom: 16 }} />
              <Title level={4}>ReDoc</Title>
              <Paragraph type="secondary">
                Prehľadná a čitateľná dokumentácia API s lepšou navigáciou a vyhľadávaním
              </Paragraph>
              <Button type="primary" icon={<FileTextOutlined />} style={{ backgroundColor: '#52c41a', borderColor: '#52c41a' }}>
                Otvoriť ReDoc
              </Button>
            </Card>
          </Col>
        </Row>

        <Divider />

        <div>
          <Title level={5}>Informácie</Title>
          <Paragraph>
            <ul>
              <li>
                <strong>Swagger UI:</strong> Ideálne pre testovanie API - obsahuje formuláre pre zadávanie parametrov
              </li>
              <li>
                <strong>ReDoc:</strong> Lepšie pre čítanie dokumentácie - prehľadnejšia štruktúra a navigácia
              </li>
              <li>
                <strong>Autentifikácia:</strong> Dokumentácia sa otvorí s vaším JWT tokenom automaticky nakonfigurovaným
              </li>
              <li>
                <strong>Bezpečnosť:</strong> Prístup k dokumentácii je chránený - vyžaduje platné prihlásenie
              </li>
            </ul>
          </Paragraph>
        </div>
      </Card>

      <Card
        title="Syslog - Automatické čistenie"
        loading={loading}
        style={{ maxWidth: 800 }}
      >
        <Alert
          message="Automatické mazanie starých logov"
          description="Systém automaticky maže staré syslog záznamy podľa nastavenia. Toto pomáha udržať databázu v rozumnej veľkosti a zlepšuje výkon."
          type="info"
          showIcon
          style={{ marginBottom: 24 }}
        />

        <Form
          form={form}
          layout="vertical"
          onFinish={handleSave}
        >
          <Form.Item
            label="Uchovávať logy"
            name="retentionDays"
            rules={[
              { required: true, message: 'Počet dní je povinný' },
              { type: 'number', min: 1, max: 3650, message: 'Počet dní musí byť medzi 1 a 3650' },
            ]}
            extra={
              <Space direction="vertical" size="small">
                <Text type="secondary">
                  Počet dní, počas ktorých sa budú uchovávať syslog záznamy.
                </Text>
                {getRetentionInfo() && (
                  <Text strong>Aktuálne: {getRetentionInfo()}</Text>
                )}
              </Space>
            }
          >
            <InputNumber
              min={1}
              max={3650}
              style={{ width: 200 }}
              addonAfter="dní"
            />
          </Form.Item>

          <Divider />

          <Form.Item
            label="Automatické čistenie"
            name="cleanupEnabled"
            valuePropName="checked"
            extra="Ak je vypnuté, logy sa nebudú automaticky mazať"
          >
            <Switch checkedChildren="Zapnuté" unCheckedChildren="Vypnuté" />
          </Form.Item>

          <Form.Item
            label="Hodina spustenia čistenia"
            name="cleanupHour"
            rules={[
              { required: true, message: 'Hodina je povinná' },
              { type: 'number', min: 0, max: 23, message: 'Hodina musí byť medzi 0 a 23' },
            ]}
            extra="Hodina dňa (0-23), kedy sa má spustiť automatické čistenie"
          >
            <InputNumber
              min={0}
              max={23}
              style={{ width: 150 }}
              addonAfter="h"
            />
          </Form.Item>

          <Divider />

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              icon={<SaveOutlined />}
              loading={saving}
              size="large"
            >
              Uložiť nastavenia
            </Button>
          </Form.Item>
        </Form>

        <Divider />

        <div>
          <Title level={5}>Informácie</Title>
          <Paragraph>
            <ul>
              <li>
                <strong>Automatické čistenie:</strong> Automaticky sa spúšťa každý deň o nastavenej hodine
              </li>
              <li>
                <strong>Výkon:</strong> Odstránením starých logov sa zlepšuje výkon databázy
              </li>
              <li>
                <strong>Odporúčanie:</strong> Pre DHCP server sa odporúča uchovávať logy 3-6 mesiacov (90-180 dní)
              </li>
              <li>
                <strong>DHCP logy:</strong> Pri vysokej záťaži môže DHCP server generovať tisíce záznamov denne
              </li>
            </ul>
          </Paragraph>
        </div>
      </Card>
    </div>
  );
}
