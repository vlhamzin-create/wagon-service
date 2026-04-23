import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { WagonFilters, WagonMode, SortDir } from '@/types/wagon'

export const useWagonsStore = defineStore('wagons', () => {
  const mode = ref<WagonMode>('all')
  const search = ref<string>('')
  const sortBy = ref<string>('current_city')
  const sortDir = ref<SortDir>('asc')

  const activeFilters = ref<Omit<WagonFilters, 'mode' | 'search' | 'sort_by' | 'sort_dir'>>({})

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
  }

  function setSearch(s: string): void {
    search.value = s
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
  }

  return {
    mode,
    search,
    sortBy,
    sortDir,
    activeFilters,
    getFilters,
    setMode,
    setSearch,
    setSortBy,
    toggleSortDir,
    setFilters,
  }
})
