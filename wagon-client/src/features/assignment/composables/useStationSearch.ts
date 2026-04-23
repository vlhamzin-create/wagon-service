import { ref } from 'vue'
import { debounce } from '@/utils/debounce'
import { searchStations } from '../api/stationApi'
import type { Station } from '../types/assignment.types'

export function useStationSearch() {
  const query = ref('')
  const suggestions = ref<Station[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  async function doSearch(value: string): Promise<void> {
    if (value.length < 2) {
      suggestions.value = []
      return
    }
    isLoading.value = true
    error.value = null
    try {
      suggestions.value = await searchStations(value)
    } catch {
      error.value = 'Ошибка загрузки справочника станций'
      suggestions.value = []
    } finally {
      isLoading.value = false
    }
  }

  const debouncedSearch = debounce(doSearch, 300)

  function onInput(value: string): void {
    query.value = value
    debouncedSearch(value)
  }

  function clear(): void {
    query.value = ''
    suggestions.value = []
  }

  return { query, suggestions, isLoading, error, onInput, clear }
}
