import { computed } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { useDashboardStore } from '@/stores/dashboardStore'
import { fetchDashboardBasic } from '@/api/dashboard'
import type { DashboardBasicResponse } from '@/api/dashboard'

const POLLING_INTERVAL_MS = 60_000

export function useDashboard() {
  const store = useDashboardStore()

  const queryKey = computed(() => ['dashboard', 'basic', store.selectedWagonType] as const)

  const {
    data,
    isLoading,
    isError,
    error,
  } = useQuery<DashboardBasicResponse>({
    queryKey,
    queryFn: () =>
      fetchDashboardBasic(
        store.selectedWagonType ? { wagon_type: store.selectedWagonType } : {},
      ),
    refetchInterval: POLLING_INTERVAL_MS,
  })

  const calculatedAt = computed(() => data.value?.calculated_at ?? null)
  const destinationRailways = computed(() => data.value?.destination_railways ?? [])
  const summaryByWagonType = computed(() => data.value?.summary_by_wagon_type ?? [])
  const summaryByOwnerType = computed(() => data.value?.summary_by_owner_type ?? [])
  const totals = computed(() => data.value?.totals ?? null)

  const errorMessage = computed(() => {
    if (!isError.value || !error.value) return null
    const msg = (error.value as Error).message ?? ''
    if (msg.includes('403')) return 'Недостаточно прав для просмотра дашборда.'
    if (msg.includes('500')) return 'Ошибка сервера. Попробуйте позже.'
    return `Ошибка загрузки данных.`
  })

  return {
    store,
    data,
    isLoading,
    isError,
    errorMessage,
    calculatedAt,
    destinationRailways,
    summaryByWagonType,
    summaryByOwnerType,
    totals,
  }
}
