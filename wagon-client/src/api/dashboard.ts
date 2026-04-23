import { apiClient } from './client'

export interface CategoryCounts {
  under_loading: number
  going_to_loading: number
  under_unloading: number
  going_to_unloading: number
  without_assignment: number
  without_assignment_in_transit: number
}

export interface DestinationRailwayRow extends CategoryCounts {
  destination_railway: string
}

export interface WagonTypeSummaryRow extends CategoryCounts {
  wagon_type: string
}

export interface OwnerTypeSummaryRow extends CategoryCounts {
  owner_type: string
}

export interface Totals {
  in_work: number
  requires_assignment: number
}

export interface DashboardBasicResponse {
  calculated_at: string
  destination_railways: DestinationRailwayRow[]
  summary_by_wagon_type: WagonTypeSummaryRow[]
  summary_by_owner_type: OwnerTypeSummaryRow[]
  totals: Totals
}

export interface DashboardBasicParams {
  wagon_type?: string
}

export function fetchDashboardBasic(
  params: DashboardBasicParams = {},
): Promise<DashboardBasicResponse> {
  const query = params.wagon_type
    ? `?wagon_type=${encodeURIComponent(params.wagon_type)}`
    : ''
  return apiClient.get<DashboardBasicResponse>(`/dashboard/basic${query}`)
}
