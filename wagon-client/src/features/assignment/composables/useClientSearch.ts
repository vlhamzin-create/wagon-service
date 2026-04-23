import { ref } from 'vue'
import { debounce } from '@/utils/debounce'
import { searchClients } from '../api/clientApi'
import type { Client } from '../types/assignment.types'

export function useClientSearch() {
  const query = ref('')
  const suggestions = ref<Client[]>([])
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
      suggestions.value = await searchClients(value)
    } catch {
      error.value = 'Ошибка загрузки справочника клиентов'
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
