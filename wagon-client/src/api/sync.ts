import type { SyncStatusResponse, TriggerResponse } from '@/types/api'
import { apiClient } from './client'

export function fetchSyncStatus(): Promise<SyncStatusResponse> {
  return apiClient.get<SyncStatusResponse>('/sync-status')
}

export function triggerSync(): Promise<TriggerResponse> {
  return apiClient.post<TriggerResponse>('/sync/trigger')
}
