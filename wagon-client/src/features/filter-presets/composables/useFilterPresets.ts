import { storeToRefs } from 'pinia'
import { useFilterPresetsStore } from '../store/filterPresetsStore'
import { useWagonsStore } from '@/stores/wagons'
import type { FilterPreset, PresetFilters, UpdatePresetDto } from '../types/filterPreset.types'

export function useFilterPresets() {
  const presetsStore = useFilterPresetsStore()
  const wagonsStore = useWagonsStore()
  const { sortedPresets, activePreset, activePresetId, loading, saving, error } =
    storeToRefs(presetsStore)

  function applyPreset(preset: FilterPreset): void {
    const { mode, search, sort_by, sort_dir, ...filterFields } = preset.filters as Record<string, unknown>
    wagonsStore.setFilters(filterFields as PresetFilters)
    presetsStore.setActivePreset(preset.id)
  }

  async function saveCurrentFiltersAsPreset(
    name: string,
    description?: string,
  ): Promise<FilterPreset> {
    const currentFilters = { ...wagonsStore.activeFilters }
    return presetsStore.createPreset({
      name,
      description,
      scope: 'wagon_list',
      filters: currentFilters,
    })
  }

  async function updatePreset(
    id: string,
    patch: { name?: string; description?: string; updateFilters?: boolean },
  ): Promise<FilterPreset> {
    const dto: UpdatePresetDto = {}
    if (patch.name !== undefined) dto.name = patch.name
    if (patch.description !== undefined) dto.description = patch.description
    if (patch.updateFilters) dto.filters = { ...wagonsStore.activeFilters }
    return presetsStore.updatePreset(id, dto)
  }

  async function deletePreset(id: string): Promise<void> {
    await presetsStore.deletePreset(id)
  }

  return {
    presets: sortedPresets,
    activePreset,
    activePresetId,
    loading,
    saving,
    error,
    applyPreset,
    saveCurrentFiltersAsPreset,
    updatePreset,
    deletePreset,
    fetchPresets: presetsStore.fetchPresets,
  }
}
