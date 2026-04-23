export interface WagonListItem {
  id: string
  number: string
  owner_type: string
  wagon_type: string
  current_country: string | null
  current_station_code: string | null
  current_station_name: string | null
  current_city: string | null
  destination_station_name: string | null
  destination_railway: string | null
  next_destination_station_name: string | null
  days_without_movement: number | null
  supplier_name: string | null
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
  last_movement_at: string | null
  created_at: string
}

export type WagonMode = 'all' | 'requires_assignment'

export type SortDir = 'asc' | 'desc'

export interface WagonFilters {
  mode: WagonMode
  owner_type?: string[]
  wagon_type?: string[]
  status?: string[]
  destination_railway?: string[]
  supplier_name?: string[]
  current_city?: string[]
  current_station_name?: string[]
  search?: string
  sort_by: string
  sort_dir: SortDir
}

export interface FilterOption {
  value: string
  label: string
}

export interface FilterOptionsResponse {
  destination_railway: FilterOption[]
  supplier_name: FilterOption[]
  current_city: FilterOption[]
  owner_type: FilterOption[]
  wagon_type: FilterOption[]
  status: FilterOption[]
}
