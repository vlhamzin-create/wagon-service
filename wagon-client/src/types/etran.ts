export type EtranDocStatus = 'sent' | 'pending' | 'accepted' | 'error'

export type EtranDocType =
  | 'Накладная'
  | 'Заявка ГУ-12'
  | 'Уведомление о подаче'
  | 'Уведомление о прибытии'
  | 'Акт общей формы'

export type EtranOperationType = 'Отправка' | 'Получение' | 'Повтор' | 'Запрос'

export interface EtranDocument {
  id: string
  doc_number: string
  doc_type: EtranDocType
  operation_type: EtranOperationType
  status: EtranDocStatus
  comment: string | null
  sent_at: string
  updated_at: string
}

export interface EtranStatusSummary {
  wagon_id: string
  current_status: EtranDocStatus
  last_doc_number: string | null
  last_updated_at: string | null
  documents_count: number
  next_poll_at: string | null
}

export interface EtranHistoryResponse {
  wagon_id: string
  documents: EtranDocument[]
  summary: EtranStatusSummary
}
