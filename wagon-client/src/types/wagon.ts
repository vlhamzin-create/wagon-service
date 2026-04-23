export interface WagonListItem {
  id: string
  number: string
  owner_type: string
  wagon_type: string
  current_country: string | null
  current_station_code: string | null
  current_station_name: string | null
  current_city: string | null
  status: string
  requires_assignment: boolean
  source: string
  updated_at: string
}

export interface WagonDetail extends WagonListItem {
  external_id_rwl: string
  model: string | null
  capacity_tons: number | null
  volume_m3: number | null
  created_at: string
}

export type WagonMode = 'all' | 'requires_assignment'

export type SortDir = 'asc' | 'desc'

export interface WagonFilters {
  mode: WagonMode
  owner_type?: string[]
  wagon_type?: string[]
  status?: string[]
  current_city?: string[]
  current_station_name?: string[]
  search?: string
  sort_by: string
  sort_dir: SortDir
}
