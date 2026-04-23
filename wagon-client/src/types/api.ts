import type { WagonListItem } from './wagon'

export interface PaginatedWagons {
  items: WagonListItem[]
  total: number
  limit: number
  offset: number
  has_more: boolean
}

export interface SourceStatus {
  source: string
  last_success_at: string | null
  last_status: string
  last_error: string | null
}

export interface SyncStatusResponse {
  sources: SourceStatus[]
}

export interface TriggerResponse {
  detail: string
}
