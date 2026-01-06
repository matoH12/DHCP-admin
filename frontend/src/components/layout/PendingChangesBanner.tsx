import { useState } from 'react';
import { Alert, Button, Space, message } from 'antd';
import { SyncOutlined } from '@ant-design/icons';
import { apiService } from '../../services/api';
import { useAuth } from '../../hooks/useAuth';
import { useDHCPStatus } from '../../contexts/DHCPStatusContext';

export function PendingChangesBanner() {
  const [loading, setLoading] = useState(false);
  const { user } = useAuth();
  const { pendingChanges, checkPendingChanges } = useDHCPStatus();

  const handleActivate = async () => {
    setLoading(true);
    try {
      await apiService.activateDHCPConfig();
      message.success('Zmeny boli úspešne aktivované');
      await checkPendingChanges();
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'Nepodarilo sa aktivovať zmeny';
      message.error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  if (!pendingChanges) {
    return null;
  }

  const isAdmin = user?.role === 'ADMIN';

  return (
    <Alert
      message="Čakajúce zmeny v konfigurácii"
      description={
        <Space direction="vertical" size="small" style={{ width: '100%' }}>
          <span>
            Vykonali ste zmeny v zariadeniach alebo IP rozsahoch.
            Pre aplikovanie zmien je potrebné vygenerovať a aktivovať novú DHCP konfiguráciu.
          </span>
          {isAdmin ? (
            <Button
              type="primary"
              icon={<SyncOutlined />}
              onClick={handleActivate}
              loading={loading}
              size="small"
            >
              Aktivovať zmeny
            </Button>
          ) : (
            <span style={{ color: '#faad14' }}>
              Pre aktiváciu zmien kontaktujte administrátora.
            </span>
          )}
        </Space>
      }
      type="warning"
      showIcon
      closable={false}
      style={{ marginBottom: 16 }}
    />
  );
}
