import { apiClient } from '@/api/client'
import type { FilterPreset, CreatePresetDto, UpdatePresetDto } from '../types/filterPreset.types'

export const filterPresetsApi = {
  async getAll(scope: string = 'wagon_list'): Promise<FilterPreset[]> {
    return apiClient.get<FilterPreset[]>(`/filter-presets?scope=${encodeURIComponent(scope)}`)
  },

  async create(dto: CreatePresetDto): Promise<FilterPreset> {
    return apiClient.post<FilterPreset>('/filter-presets', dto)
  },

  async update(id: string, dto: UpdatePresetDto): Promise<FilterPreset> {
    return apiClient.put<FilterPreset>(`/filter-presets/${id}`, dto)
  },

  async remove(id: string): Promise<void> {
    await apiClient.delete(`/filter-presets/${id}`)
  },
}
