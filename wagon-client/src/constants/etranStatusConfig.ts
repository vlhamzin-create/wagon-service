import type { EtranDocStatus } from '@/types/etran'

export interface StatusConfig {
  label: string
  description: string
  bgColor: string
  textColor: string
  borderColor: string
  dotColor: string
  iconPath: string
  animateDot: boolean
}

export const ETRAN_STATUS_CONFIG: Record<EtranDocStatus, StatusConfig> = {
  sent: {
    label: 'Отправлено',
    description: 'Документ передан в ЭТРАН через SOAP SendBlock. Ожидается ответ системы.',
    bgColor: '#eff6ff',
    textColor: '#1d4ed8',
    borderColor: '#bfdbfe',
    dotColor: '#60a5fa',
    iconPath: 'M12 19l9 2-9-18-9 18 9-2zm0 0v-8',
    animateDot: true,
  },
  pending: {
    label: 'На визировании',
    description: 'Документ принят ЭТРАН и передан на визирование. Ожидается результат GetBlock.',
    bgColor: '#fffbeb',
    textColor: '#b45309',
    borderColor: '#fde68a',
    dotColor: '#fbbf24',
    iconPath: 'M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67V7z',
    animateDot: true,
  },
  accepted: {
    label: 'Принято',
    description: 'ЭТРАН подтвердил приём и визирование документа.',
    bgColor: '#ecfdf5',
    textColor: '#047857',
    borderColor: '#a7f3d0',
    dotColor: '#10b981',
    iconPath: 'M20 6L9 17l-5-5',
    animateDot: false,
  },
  error: {
    label: 'Ошибка',
    description: 'ЭТРАН вернул ошибку. Требуется исправление и повторная отправка.',
    bgColor: '#fef2f2',
    textColor: '#b91c1c',
    borderColor: '#fecaca',
    dotColor: '#ef4444',
    iconPath: 'M18 6L6 18M6 6l12 12',
    animateDot: false,
  },
}

export const ETRAN_STATUS_LIFECYCLE: EtranDocStatus[] = [
  'sent',
  'pending',
  'accepted',
]
