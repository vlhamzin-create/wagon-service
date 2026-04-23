import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { WagonFilters, WagonMode, SortDir } from '@/types/wagon'

export const useWagonsStore = defineStore('wagons', () => {
  const mode = ref<WagonMode>('all')
  const search = ref<string>('')
  const sortBy = ref<string>('destination_railway')
  const sortDir = ref<SortDir>('desc')

  const activeFilters = ref<Omit<WagonFilters, 'mode' | 'search' | 'sort_by' | 'sort_dir'>>({})

  // Счётчик сброса: при его изменении useWagonList перезапрашивает с offset=0.
  // Инкрементируется при любом изменении фильтров/поиска.
  const resetCounter = ref<number>(0)

  function getFilters(): WagonFilters {
    return {
      mode: mode.value,
      search: search.value || undefined,
      sort_by: sortBy.value,
      sort_dir: sortDir.value,
      ...activeFilters.value,
    }
  }

  function setMode(m: WagonMode): void {
    mode.value = m
    _resetPagination()
  }

  function setSearch(s: string): void {
    search.value = s
    _resetPagination()
  }

  function toggleSortDir(): void {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  }

  function setSortBy(field: string): void {
    if (sortBy.value === field) {
      toggleSortDir()
    } else {
      sortBy.value = field
      sortDir.value = 'asc'
    }
  }

  function setFilters(f: Omit<WagonFilters, 'mode' | 'search' | 'sort_by' | 'sort_dir'>): void {
    activeFilters.value = f
    _resetPagination()
  }

  /** Сбрасывает пагинацию — вызывается при любом изменении фильтров/поиска. */
  function _resetPagination(): void {
    resetCounter.value += 1
  }

  return {
    mode,
    search,
    sortBy,
    sortDir,
    activeFilters,
    resetCounter,
    getFilters,
    setMode,
    setSearch,
    setSortBy,
    toggleSortDir,
    setFilters,
  }
})
