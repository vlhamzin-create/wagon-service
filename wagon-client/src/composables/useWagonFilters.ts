import { ref, watch } from 'vue'
import { useWagonsStore } from '@/stores/wagons'
import { debounce } from '@/utils/debounce'

const DEBOUNCE_MS = 300

/**
 * Связывает поле поиска с хранилищем через debounce.
 * Возвращает реактивный ref для v-model и метод сброса.
 */
export function useWagonFilters() {
  const store = useWagonsStore()
  const searchInput = ref(store.search)

  const _applySearch = debounce((value: string) => {
    store.setSearch(value)
  }, DEBOUNCE_MS)

  watch(searchInput, (v) => _applySearch(v))

  function resetSearch(): void {
    searchInput.value = ''
    store.setSearch('')
  }

  return { searchInput, resetSearch }
}
