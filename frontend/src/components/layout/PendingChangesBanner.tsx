import { useState, useEffect } from 'react';
import { Alert, Button, Space, message } from 'antd';
import { SyncOutlined } from '@ant-design/icons';
import { apiService } from '../../services/api';
import { useAuth } from '../../hooks/useAuth';

export function PendingChangesBanner() {
  const [hasPendingChanges, setHasPendingChanges] = useState(false);
  const [loading, setLoading] = useState(false);
  const { user } = useAuth();

  // Check for pending changes on mount and poll every 10 seconds
  useEffect(() => {
    checkPendingChanges();
    const interval = setInterval(checkPendingChanges, 10000);
    return () => clearInterval(interval);
  }, []);

  const checkPendingChanges = async () => {
    try {
      const status = await apiService.getDHCPStatus();
      console.log('[PendingChangesBanner] DHCP status:', status);
      setHasPendingChanges(status.pending_changes);
    } catch (error) {
      console.error('[PendingChangesBanner] Failed to check DHCP status:', error);
    }
  };

  const handleActivate = async () => {
    setLoading(true);
    try {
      await apiService.activateDHCPConfig();
      message.success('Zmeny boli úspešne aktivované');
      setHasPendingChanges(false);
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'Nepodarilo sa aktivovať zmeny';
      message.error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  if (!hasPendingChanges) {
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
