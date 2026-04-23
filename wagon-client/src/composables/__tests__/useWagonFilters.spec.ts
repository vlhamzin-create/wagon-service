import { describe, it, expect, vi, beforeEach } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { FILTER_DEBOUNCE_MS } from '@/constants/filters'

vi.mock('@/api/wagons', () => ({
  fetchFilterOptions: vi.fn().mockResolvedValue({
    destination_railway: [],
    supplier_name: [],
    current_city: [],
    owner_type: [],
    wagon_type: [],
    status: [],
  }),
}))

vi.mock('@tanstack/vue-query', () => ({
  useQuery: vi.fn(() => ({
    data: { value: null },
    isLoading: { value: false },
    isError: { value: false },
  })),
}))

describe('useWagonFilters', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.useFakeTimers()
  })

  it('FILTER_DEBOUNCE_MS равен 300', () => {
    expect(FILTER_DEBOUNCE_MS).toBe(300)
  })

  it('debounce применяет поиск после FILTER_DEBOUNCE_MS', async () => {
    const { useWagonFilters } = await import('../useWagonFilters')
    const { useWagonsStore } = await import('@/stores/wagons')

    const { searchInput } = useWagonFilters()
    const store = useWagonsStore()
    const spy = vi.spyOn(store, 'setSearch')

    searchInput.value = 'тест'

    // До истечения debounce — не вызван
    vi.advanceTimersByTime(FILTER_DEBOUNCE_MS - 50)
    expect(spy).not.toHaveBeenCalled()

    // После истечения debounce — вызван
    vi.advanceTimersByTime(100)
    expect(spy).toHaveBeenCalledWith('тест')
  })

  it('debounce применяет фильтры после FILTER_DEBOUNCE_MS', async () => {
    const { useWagonFilters } = await import('../useWagonFilters')
    const { useWagonsStore } = await import('@/stores/wagons')

    const { pendingFilters } = useWagonFilters()
    const store = useWagonsStore()
    const spy = vi.spyOn(store, 'setFilters')

    pendingFilters.value = { destination_railway: ['РЖД'] }

    vi.advanceTimersByTime(FILTER_DEBOUNCE_MS - 50)
    expect(spy).not.toHaveBeenCalled()

    vi.advanceTimersByTime(100)
    expect(spy).toHaveBeenCalledWith({ destination_railway: ['РЖД'] })
  })

  it('resetFilters применяется немедленно без debounce', async () => {
    const { useWagonFilters } = await import('../useWagonFilters')
    const { useWagonsStore } = await import('@/stores/wagons')

    const { resetFilters } = useWagonFilters()
    const store = useWagonsStore()
    const spy = vi.spyOn(store, 'setFilters')

    resetFilters()
    expect(spy).toHaveBeenCalledWith({})
  })
})
