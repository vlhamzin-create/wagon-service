import type { EtranHistoryResponse } from '@/types/etran'
import { apiClient } from './client'

export function fetchEtranHistory(wagonId: string): Promise<EtranHistoryResponse> {
  return apiClient.get<EtranHistoryResponse>(`/wagons/${wagonId}/etran-history`)
}

export function requestEtranRefresh(wagonId: string): Promise<void> {
  return apiClient.post<void>(`/wagons/${wagonId}/etran-refresh`)
}
