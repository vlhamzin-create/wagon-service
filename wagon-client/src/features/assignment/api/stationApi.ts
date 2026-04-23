import { apiClient } from '@/api/client'
import type { StationsResponse, Station } from '../types/assignment.types'

export async function searchStations(query: string, limit = 20): Promise<Station[]> {
  const params = new URLSearchParams()
  if (query) params.set('q', query)
  params.set('limit', String(limit))

  const response = await apiClient.get<StationsResponse>(`/stations?${params}`)
  return response.items
}
