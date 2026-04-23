import { apiClient } from '@/api/client'
import type { AssignRoutePayload, AssignRouteResponse } from '../types/assignment.types'

export async function assignRoute(payload: AssignRoutePayload): Promise<AssignRouteResponse> {
  return apiClient.post<AssignRouteResponse>('/wagons/assign-route', payload)
}
