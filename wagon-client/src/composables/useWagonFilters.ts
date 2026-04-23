import { ref, watch } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { useWagonsStore } from '@/stores/wagons'
import { fetchFilterOptions } from '@/api/wagons'
import { debounce } from '@/utils/debounce'
import type { FilterOptionsResponse, WagonFilters } from '@/types/wagon'
import { FILTER_DEBOUNCE_MS } from '@/constants/filters'

/**
 * Связывает поле глобального поиска и панель фильтров с хранилищем через debounce.
 * Также предоставляет данные для дропдаунов (filter-options).
 */
export function useWagonFilters() {
  const store = useWagonsStore()

  // --- Глобальный поиск ---
  const searchInput = ref(store.search)

  const _applySearch = debounce((value: string) => {
    store.setSearch(value)
  }, FILTER_DEBOUNCE_MS)

  watch(searchInput, (v) => _applySearch(v))

  function resetSearch(): void {
    searchInput.value = ''
    store.setSearch('')
  }

  // --- Панель фильтров ---
  // Локальная копия для v-model в компонентах; применяется с debounce
  const pendingFilters = ref<Omit<WagonFilters, 'mode' | 'search' | 'sort_by' | 'sort_dir'>>(
    { ...store.activeFilters },
  )

  const _applyFilters = debounce(
    (f: Omit<WagonFilters, 'mode' | 'search' | 'sort_by' | 'sort_dir'>) => {
      store.setFilters(f)
    },
    FILTER_DEBOUNCE_MS,
  )

  watch(pendingFilters, (f) => _applyFilters({ ...f }), { deep: true })

  function resetFilters(): void {
    pendingFilters.value = {}
    store.setFilters({})
  }

  // --- Filter-options (данные для дропдаунов) ---
  const {
    data: filterOptions,
    isLoading: filterOptionsLoading,
    isError: filterOptionsError,
  } = useQuery<FilterOptionsResponse>({
    queryKey: ['wagons', 'filter-options'],
    queryFn: fetchFilterOptions,
    staleTime: 5 * 60_000, // 5 минут: справочные данные меняются редко
  })

  return {
    searchInput,
    resetSearch,
    pendingFilters,
    resetFilters,
    filterOptions,
    filterOptionsLoading,
    filterOptionsError,
  }
}
