import { apiClient } from '@/api/client'
import type { ClientsResponse, Client } from '../types/assignment.types'

export async function searchClients(query: string, limit = 20): Promise<Client[]> {
  const params = new URLSearchParams()
  if (query) params.set('q', query)
  params.set('limit', String(limit))

  const response = await apiClient.get<ClientsResponse>(`/clients?${params}`)
  return response.items
}
