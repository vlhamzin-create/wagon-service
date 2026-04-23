// Справочники — соответствуют ответам BE /api/v1/stations и /api/v1/clients
export interface Station {
  id: string
  code: string
  name: string
  country: string | null
}

export interface Client {
  id: string
  name: string
  external_id_1c: string | null
}

export interface StationsResponse {
  items: Station[]
  total: number
}

export interface ClientsResponse {
  items: Client[]
  total: number
}

// Состояние вагона в контексте назначения
export interface WagonAssignmentState {
  wagonId: string
  wagonNumber: string
  currentStationCode: string | null
  currentStationName: string | null
  currentClientId: string | null
  currentClientName: string | null
  hasExistingData: boolean
}

// Payload для POST /api/v1/wagons/assign-route
export interface AssignRoutePayload {
  wagon_ids: string[]
  station_code: string | null
  client_id: string | null
  overwrite: boolean
}

// Результат по одному вагону
export type WagonResultStatus = 'ok' | 'skipped' | 'error'

export interface WagonAssignResult {
  wagon_id: string
  status: WagonResultStatus
  reason: string | null
}

// Ответ API
export interface AssignRouteResponse {
  total: number
  succeeded: number
  skipped: number
  failed: number
  results: WagonAssignResult[]
}

// Режим панели
export type PanelMode = 'single' | 'bulk'

// Фаза панели
export type PanelPhase = 'form' | 'progress' | 'result'

// Внутреннее состояние формы
export interface AssignmentFormState {
  selectedStation: Station | null
  selectedClient: Client | null
  comment: string
  onlyEmpty: boolean
}
