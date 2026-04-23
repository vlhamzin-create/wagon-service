import { ref, computed } from 'vue'
import { useWagonsStore } from '@/stores/wagons'
import type { FilterPreset } from '../types/filterPreset.types'

interface PresetFormState {
  name: string
  description: string
}

interface ValidationErrors {
  name?: string
  filters?: string
}

export function usePresetForm(editTarget?: FilterPreset) {
  const wagonsStore = useWagonsStore()

  const form = ref<PresetFormState>({
    name: editTarget?.name ?? '',
    description: editTarget?.description ?? '',
  })

  const errors = ref<ValidationErrors>({})

  function validate(): boolean {
    errors.value = {}

    const name = form.value.name.trim()
    if (!name) {
      errors.value.name = 'Название обязательно'
    } else if (name.length > 255) {
      errors.value.name = 'Не более 255 символов'
    }

    if (!editTarget) {
      const filters = wagonsStore.activeFilters
      const hasAnyFilter = Object.values(filters).some((v) => {
        if (Array.isArray(v)) return v.length > 0
        return v !== undefined && v !== null && v !== ''
      })

      if (!hasAnyFilter) {
        errors.value.filters = 'Необходимо задать хотя бы одно условие фильтра'
      }
    }

    return Object.keys(errors.value).length === 0
  }

  const isValid = computed(() => Object.keys(errors.value).length === 0)

  function reset() {
    form.value = { name: '', description: '' }
    errors.value = {}
  }

  return { form, errors, isValid, validate, reset }
}
