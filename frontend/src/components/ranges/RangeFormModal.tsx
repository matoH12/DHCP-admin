import { useEffect, useState } from 'react';
import { Modal, Form, Input, InputNumber, Select, Button, message, Checkbox } from 'antd';
import { apiService } from '../../services/api';
import type { IPRange } from '../../types/api';

interface RangeFormModalProps {
  open: boolean;
  range: IPRange | null;
  onCancel: () => void;
  onSuccess: () => void;
}

// Helper function to calculate usable IP range
function calculateIPRange(networkAddress: string, cidr: number): { start: string; end: string; count: number; ips: string[] } | null {
  try {
    const parts = networkAddress.split('.').map(Number);
    if (parts.length !== 4 || parts.some(p => p < 0 || p > 255)) {
      return null;
    }

    const hostBits = 32 - cidr;
    const totalHosts = Math.pow(2, hostBits);
    const usableHosts = totalHosts - 2; // exclude network and broadcast

    if (usableHosts < 1) {
      return null;
    }

    // Calculate first usable IP (network + 1)
    const networkInt = (parts[0] << 24) + (parts[1] << 16) + (parts[2] << 8) + parts[3];
    const firstUsable = networkInt + 1;
    const lastUsable = networkInt + totalHosts - 2;

    const firstIP = [
      (firstUsable >>> 24) & 0xFF,
      (firstUsable >>> 16) & 0xFF,
      (firstUsable >>> 8) & 0xFF,
      firstUsable & 0xFF
    ].join('.');

    const lastIP = [
      (lastUsable >>> 24) & 0xFF,
      (lastUsable >>> 16) & 0xFF,
      (lastUsable >>> 8) & 0xFF,
      lastUsable & 0xFF
    ].join('.');

    // Generate list of all IPs (limit to 1000 for performance)
    const ips: string[] = [];
    const maxIPs = Math.min(usableHosts, 1000);

    for (let i = 0; i < maxIPs; i++) {
      const ipInt = firstUsable + i;
      const ip = [
        (ipInt >>> 24) & 0xFF,
        (ipInt >>> 16) & 0xFF,
        (ipInt >>> 8) & 0xFF,
        ipInt & 0xFF
      ].join('.');
      ips.push(ip);
    }

    return { start: firstIP, end: lastIP, count: usableHosts, ips };
  } catch {
    return null;
  }
}

export function RangeFormModal({ open, range, onCancel, onSuccess }: RangeFormModalProps) {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [poolEnabled, setPoolEnabled] = useState(false);
  const [networkInfo, setNetworkInfo] = useState<{ start: string; end: string; count: number; ips: string[] } | null>(null);

  useEffect(() => {
    if (open) {
      if (range) {
        form.setFieldsValue(range);
        // Check if range has pool enabled
        if (range.pool_start && range.pool_end) {
          setPoolEnabled(true);
        } else {
          setPoolEnabled(false);
        }
        // Calculate network info if network_address and cidr are present
        if (range.network_address && range.cidr) {
          const info = calculateIPRange(range.network_address, range.cidr);
          setNetworkInfo(info);
        }
      } else {
        form.resetFields();
        setPoolEnabled(false);
        setNetworkInfo(null);
      }
    }
  }, [open, range, form]);

  // Watch for changes in network_address and cidr
  const handleNetworkChange = () => {
    const networkAddress = form.getFieldValue('network_address');
    const cidr = form.getFieldValue('cidr');

    if (networkAddress && cidr) {
      // Validate IP format
      const ipRegex = /^(\d{1,3}\.){3}\d{1,3}$/;
      if (ipRegex.test(networkAddress)) {
        const parts = networkAddress.split('.').map(Number);
        if (!parts.some(p => p > 255)) {
          const info = calculateIPRange(networkAddress, cidr);
          setNetworkInfo(info);
          return;
        }
      }
    }
    setNetworkInfo(null);
  };

  const validateIP = (_: unknown, value: string) => {
    if (!value) {
      return Promise.reject('IP adresa je povinná');
    }
    const ipRegex = /^(\d{1,3}\.){3}\d{1,3}$/;
    if (!ipRegex.test(value)) {
      return Promise.reject('Neplatný formát IP adresy');
    }
    const parts = value.split('.').map(Number);
    if (parts.some(p => p > 255)) {
      return Promise.reject('Neplatná IP adresa');
    }
    return Promise.resolve();
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      setLoading(true);

      // Clear pool fields if pool is not enabled
      if (!poolEnabled) {
        values.pool_start = null;
        values.pool_end = null;
      }

      if (range) {
        await apiService.updateRange(range.id, values);
        message.success('IP rozsah bol aktualizovaný');
      } else {
        await apiService.createRange(values);
        message.success('IP rozsah bol vytvorený');
      }

      onSuccess();
    } catch (error: unknown) {
      if (error && typeof error === 'object' && 'response' in error) {
        const response = (error as { response?: { data?: { detail?: string } } }).response;
        message.error(response?.data?.detail || 'Nepodarilo sa uložiť rozsah');
      } else if (error && typeof error === 'object' && 'errorFields' in error) {
        // Validation error
      } else {
        message.error('Nepodarilo sa uložiť rozsah');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      title={range ? 'Upraviť IP rozsah' : 'Pridať IP rozsah'}
      open={open}
      onCancel={onCancel}
      footer={[
        <Button key="cancel" onClick={onCancel}>
          Zrušiť
        </Button>,
        <Button key="submit" type="primary" loading={loading} onClick={handleSubmit}>
          {range ? 'Uložiť' : 'Vytvoriť'}
        </Button>,
      ]}
      width={600}
    >
      <Form
        form={form}
        layout="vertical"
      >
        <Form.Item
          label="Názov"
          name="name"
          rules={[{ required: true, message: 'Názov je povinný' }]}
        >
          <Input placeholder="napr. Office Network" />
        </Form.Item>

        <Form.Item
          label="Sieťová adresa"
          name="network_address"
          rules={[{ validator: validateIP }]}
          extra="Napr. 192.168.1.0"
        >
          <Input placeholder="192.168.1.0" onChange={handleNetworkChange} />
        </Form.Item>

        <Form.Item
          label="CIDR"
          name="cidr"
          rules={[
            { required: true, message: 'CIDR je povinný' },
            { type: 'number', min: 8, max: 30, message: 'CIDR musí byť medzi 8 a 30' },
          ]}
          extra="Napr. 24 pre masku 255.255.255.0"
        >
          <InputNumber min={8} max={30} style={{ width: '100%' }} onChange={handleNetworkChange} />
        </Form.Item>

        <Form.Item
          label="Gateway"
          name="gateway"
          rules={[{ validator: validateIP }]}
        >
          <Input placeholder="192.168.1.1" />
        </Form.Item>

        <Form.Item
          label="DNS Servery"
          name="dns_servers"
          rules={[{ required: true, message: 'Aspoň jeden DNS server je povinný' }]}
          extra="Napr. 8.8.8.8, 8.8.4.4"
        >
          <Select
            mode="tags"
            placeholder="Zadajte DNS servery"
            tokenSeparators={[',']}
          />
        </Form.Item>

        <Form.Item
          label="Doménové meno"
          name="domain_name"
          rules={[{ required: true, message: 'Doménové meno je povinné' }]}
        >
          <Input placeholder="napr. office.local" />
        </Form.Item>

        <Form.Item
          label="Popis"
          name="description"
        >
          <Input.TextArea rows={3} placeholder="Voliteľný popis rozsahu" />
        </Form.Item>

        <div style={{ marginTop: 24, marginBottom: 16, borderTop: '1px solid #d9d9d9', paddingTop: 16 }}>
          <h4 style={{ marginBottom: 16 }}>DHCP Pool (Dynamické prideľovanie IP)</h4>

          {networkInfo && (
            <div style={{
              marginBottom: 16,
              padding: 12,
              backgroundColor: '#f0f5ff',
              borderRadius: 4,
              border: '1px solid #adc6ff'
            }}>
              <div style={{ fontSize: 13, color: '#1890ff', fontWeight: 500, marginBottom: 4 }}>
                Dostupný rozsah IP adries v sieti:
              </div>
              <div style={{ fontSize: 14, color: '#262626' }}>
                {networkInfo.start} - {networkInfo.end}
              </div>
              <div style={{ fontSize: 12, color: '#666', marginTop: 4 }}>
                Celkom {networkInfo.count} použiteľných IP adries
                {networkInfo.count > 1000 && ' (zobrazených prvých 1000)'}
              </div>
            </div>
          )}

          <Form.Item style={{ marginBottom: 16 }}>
            <Checkbox
              checked={poolEnabled}
              onChange={(e) => {
                setPoolEnabled(e.target.checked);
                if (!e.target.checked) {
                  form.setFieldsValue({ pool_start: undefined, pool_end: undefined });
                }
              }}
              disabled={!networkInfo}
            >
              Povoliť DHCP pool pre dynamické prideľovanie IP adries
            </Checkbox>
            <div style={{ fontSize: 12, color: '#666', marginTop: 4, marginLeft: 24 }}>
              {!networkInfo && 'Najprv vyplňte sieťovú adresu a CIDR'}
            </div>
          </Form.Item>

          {poolEnabled && (
            <>
              <p style={{ fontSize: 12, color: '#666', marginBottom: 16 }}>
                Definujte rozsah IP adries pre automatické prideľovanie (DHCP pool).
                Tieto IP nebudú k dispozícii pre statické rezervácie.
              </p>

              <Form.Item
                label="Pool - začiatok"
                name="pool_start"
                rules={[{ required: true, message: 'Vyberte počiatočnú IP pre pool' }]}
                extra={networkInfo ? `Vyberte IP medzi ${networkInfo.start} a ${networkInfo.end}` : ''}
              >
                <Select
                  showSearch
                  placeholder="Vyberte začiatočnú IP adresu"
                  options={networkInfo?.ips.map(ip => ({
                    label: ip,
                    value: ip,
                  }))}
                  filterOption={(input, option) =>
                    (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
                  }
                />
              </Form.Item>

              <Form.Item
                label="Pool - koniec"
                name="pool_end"
                rules={[{ required: true, message: 'Vyberte konečnú IP pre pool' }]}
                extra={networkInfo ? `Vyberte IP medzi ${networkInfo.start} a ${networkInfo.end}` : ''}
              >
                <Select
                  showSearch
                  placeholder="Vyberte konečnú IP adresu"
                  options={networkInfo?.ips.map(ip => ({
                    label: ip,
                    value: ip,
                  }))}
                  filterOption={(input, option) =>
                    (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
                  }
                />
              </Form.Item>
            </>
          )}
        </div>
      </Form>
    </Modal>
  );
}
