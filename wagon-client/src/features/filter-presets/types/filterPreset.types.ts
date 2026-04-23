export interface PresetFilters {
  owner_type?: string[]
  wagon_type?: string[]
  status?: string[]
  destination_railway?: string[]
  supplier_name?: string[]
  current_city?: string[]
  current_station_name?: string[]
  [key: string]: unknown
}

export interface FilterPreset {
  id: string
  name: string
  description?: string
  scope: 'wagon_list'
  filters: PresetFilters
  created_at: string
  updated_at: string
}

export type CreatePresetDto = {
  name: string
  description?: string
  scope: 'wagon_list'
  filters: PresetFilters
}

export type UpdatePresetDto = Partial<Pick<CreatePresetDto, 'name' | 'description' | 'filters'>>
