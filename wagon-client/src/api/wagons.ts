import type { PaginatedWagons } from '@/types/api'
import type { FilterOptionsResponse, WagonDetail, WagonFilters } from '@/types/wagon'
import { apiClient } from './client'

const PAGE_SIZE = 100

function buildParams(filters: WagonFilters, offset: number): URLSearchParams {
  const params = new URLSearchParams()

  params.set('limit', String(PAGE_SIZE))
  params.set('offset', String(offset))
  params.set('mode', filters.mode)
  params.set('sort_by', filters.sort_by)
  params.set('sort_dir', filters.sort_dir)

  if (filters.search) params.set('search', filters.search)
  filters.owner_type?.forEach((v) => params.append('owner_type', v))
  filters.wagon_type?.forEach((v) => params.append('wagon_type', v))
  filters.status?.forEach((v) => params.append('status', v))
  filters.destination_railway?.forEach((v) => params.append('destination_railway', v))
  filters.supplier_name?.forEach((v) => params.append('supplier_name', v))
  filters.current_city?.forEach((v) => params.append('current_city', v))
  filters.current_station_name?.forEach((v) => params.append('current_station_name', v))

  return params
}

export function fetchWagons(filters: WagonFilters, offset: number): Promise<PaginatedWagons> {
  const params = buildParams(filters, offset)
  return apiClient.get<PaginatedWagons>(`/wagons?${params.toString()}`)
}

export function fetchWagonById(id: string): Promise<WagonDetail> {
  return apiClient.get<WagonDetail>(`/wagons/${id}`)
}

export function fetchFilterOptions(): Promise<FilterOptionsResponse> {
  return apiClient.get<FilterOptionsResponse>('/wagons/filter-options')
}

export { PAGE_SIZE }
