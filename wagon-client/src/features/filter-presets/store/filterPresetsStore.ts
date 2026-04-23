import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { filterPresetsApi } from '../api/filterPresetsApi'
import type { FilterPreset, CreatePresetDto, UpdatePresetDto } from '../types/filterPreset.types'

export const useFilterPresetsStore = defineStore('filterPresets', () => {
  const presets = ref<FilterPreset[]>([])
  const activePresetId = ref<string | null>(null)
  const loading = ref(false)
  const saving = ref(false)
  const error = ref<string | null>(null)

  const activePreset = computed(() =>
    presets.value.find((p) => p.id === activePresetId.value) ?? null,
  )

  const sortedPresets = computed(() =>
    [...presets.value].sort(
      (a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime(),
    ),
  )

  async function fetchPresets() {
    loading.value = true
    error.value = null
    try {
      presets.value = await filterPresetsApi.getAll('wagon_list')
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Неизвестная ошибка'
    } finally {
      loading.value = false
    }
  }

  async function createPreset(dto: CreatePresetDto): Promise<FilterPreset> {
    saving.value = true
    try {
      const created = await filterPresetsApi.create(dto)
      presets.value = [created, ...presets.value]
      return created
    } finally {
      saving.value = false
    }
  }

  async function updatePreset(id: string, dto: UpdatePresetDto): Promise<FilterPreset> {
    saving.value = true
    try {
      const updated = await filterPresetsApi.update(id, dto)
      const idx = presets.value.findIndex((p) => p.id === id)
      if (idx !== -1) presets.value[idx] = updated
      return updated
    } finally {
      saving.value = false
    }
  }

  async function deletePreset(id: string): Promise<void> {
    await filterPresetsApi.remove(id)
    presets.value = presets.value.filter((p) => p.id !== id)
    if (activePresetId.value === id) {
      activePresetId.value = null
    }
  }

  function setActivePreset(id: string | null) {
    activePresetId.value = id
  }

  function clearActivePreset() {
    activePresetId.value = null
  }

  return {
    presets,
    sortedPresets,
    activePreset,
    activePresetId,
    loading,
    saving,
    error,
    fetchPresets,
    createPreset,
    updatePreset,
    deletePreset,
    setActivePreset,
    clearActivePreset,
  }
})
