import { useEffect, useState } from 'react';
import { Modal, Form, Input, Select, Switch, Button, message, Spin } from 'antd';
import { apiService } from '../../services/api';
import type { Device, IPRange } from '../../types/api';

interface DeviceFormModalProps {
  open: boolean;
  device: Device | null;
  onCancel: () => void;
  onSuccess: () => void;
}

export function DeviceFormModal({ open, device, onCancel, onSuccess }: DeviceFormModalProps) {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [ranges, setRanges] = useState<IPRange[]>([]);
  const [availableIPs, setAvailableIPs] = useState<string[]>([]);
  const [loadingIPs, setLoadingIPs] = useState(false);

  useEffect(() => {
    if (open) {
      loadRanges();
      if (device) {
        form.setFieldsValue({
          ...device,
          is_active: device.is_active ?? true,
        });
        // Load available IPs for the device's range
        if (device.ip_range_id) {
          loadAvailableIPs(device.ip_range_id);
        }
      } else {
        form.resetFields();
        form.setFieldValue('is_active', true);
        setAvailableIPs([]);
      }
    }
  }, [open, device, form]);

  const loadRanges = async () => {
    try {
      const data = await apiService.getRanges();
      setRanges(data.filter(r => r.is_active));
    } catch (error) {
      message.error('Nepodarilo sa načítať IP rozsahy');
    }
  };

  const loadAvailableIPs = async (rangeId: number) => {
    setLoadingIPs(true);
    try {
      const ips = await apiService.getAvailableIPs(rangeId);
      setAvailableIPs(ips);

      // Auto-select first available IP for new devices
      if (!device && ips.length > 0) {
        form.setFieldValue('ip_address', ips[0]);
        message.success(`Načítaných ${ips.length} voľných IP adries`);
      }
    } catch (error) {
      message.error('Nepodarilo sa načítať voľné IP adresy');
      setAvailableIPs([]);
    } finally {
      setLoadingIPs(false);
    }
  };

  const handleRangeChange = async (rangeId: number) => {
    // Load available IPs when range changes
    await loadAvailableIPs(rangeId);
  };

  const validateMAC = (_: unknown, value: string) => {
    if (!value) {
      return Promise.reject('MAC adresa je povinná');
    }
    const macRegex = /^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$/;
    if (!macRegex.test(value)) {
      return Promise.reject('Neplatný formát MAC adresy (použite XX:XX:XX:XX:XX:XX)');
    }
    return Promise.resolve();
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

  const validateHostname = (_: unknown, value: string) => {
    if (!value) {
      return Promise.reject('Hostname je povinný');
    }
    const hostnameRegex = /^[a-zA-Z0-9_-]+$/;
    if (!hostnameRegex.test(value)) {
      return Promise.reject('Hostname môže obsahovať len písmená, čísla, pomlčky a podčiarkovníky');
    }
    if (value.length > 63) {
      return Promise.reject('Hostname môže mať maximálne 63 znakov');
    }
    return Promise.resolve();
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      setLoading(true);

      if (device) {
        await apiService.updateDevice(device.id, values);
        message.success('Zariadenie bolo aktualizované');
      } else {
        await apiService.createDevice(values);
        message.success('Zariadenie bolo vytvorené');
      }

      onSuccess();
    } catch (error: unknown) {
      if (error && typeof error === 'object' && 'response' in error) {
        const response = (error as { response?: { data?: { detail?: string } } }).response;
        message.error(response?.data?.detail || 'Nepodarilo sa uložiť zariadenie');
      } else if (error && typeof error === 'object' && 'errorFields' in error) {
        // Validation error - handled by form
      } else {
        message.error('Nepodarilo sa uložiť zariadenie');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      title={device ? 'Upraviť zariadenie' : 'Pridať zariadenie'}
      open={open}
      onCancel={onCancel}
      footer={[
        <Button key="cancel" onClick={onCancel}>
          Zrušiť
        </Button>,
        <Button key="submit" type="primary" loading={loading} onClick={handleSubmit}>
          {device ? 'Uložiť' : 'Vytvoriť'}
        </Button>,
      ]}
      width={600}
    >
      <Form
        form={form}
        layout="vertical"
        initialValues={{ is_active: true }}
      >
        <Form.Item
          label="Hostname"
          name="hostname"
          rules={[{ validator: validateHostname }]}
          extra="Len písmená, čísla, pomlčky a podčiarkovníky. Max 63 znakov."
        >
          <Input placeholder="napr. printer-hp" />
        </Form.Item>

        <Form.Item
          label="IP Rozsah"
          name="ip_range_id"
          rules={[{ required: true, message: 'Vyberte IP rozsah' }]}
        >
          <Select
            placeholder="Vyberte IP rozsah"
            onChange={handleRangeChange}
            options={ranges.map(r => ({
              label: `${r.name} (${r.network_address}/${r.cidr})`,
              value: r.id,
            }))}
          />
        </Form.Item>

        <Form.Item
          label="IP Adresa"
          name="ip_address"
          rules={[{ validator: validateIP }]}
          extra={availableIPs.length > 0 ? `${availableIPs.length} voľných IP adries` : 'Najprv vyberte IP rozsah'}
        >
          <Select
            showSearch
            placeholder="Vyberte IP adresu"
            loading={loadingIPs}
            notFoundContent={loadingIPs ? <Spin size="small" /> : 'Žiadne voľné IP adresy'}
            disabled={availableIPs.length === 0}
            options={availableIPs.map(ip => ({
              label: ip,
              value: ip,
            }))}
            filterOption={(input, option) =>
              (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
            }
          />
        </Form.Item>

        <Form.Item
          label="MAC Adresa"
          name="mac_address"
          rules={[{ validator: validateMAC }]}
          extra="Formát: XX:XX:XX:XX:XX:XX"
        >
          <Input placeholder="00:11:22:33:44:55" />
        </Form.Item>

        <Form.Item
          label="Popis"
          name="description"
        >
          <Input.TextArea rows={3} placeholder="Napr. HP LaserJet Printer" />
        </Form.Item>

        <Form.Item
          label="Aktívne"
          name="is_active"
          valuePropName="checked"
        >
          <Switch />
        </Form.Item>
      </Form>
    </Modal>
  );
}
