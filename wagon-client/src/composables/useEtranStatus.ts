import { ref, computed, onUnmounted } from 'vue'
import { fetchEtranHistory, requestEtranRefresh } from '@/api/etran'
import type { EtranHistoryResponse, EtranDocStatus } from '@/types/etran'

const POLL_INTERVAL_ACTIVE = 30_000
const FINAL_STATUSES: EtranDocStatus[] = ['accepted', 'error']

/**
 * Polling статуса ЭТРАН для конкретного вагона.
 * Активен пока карточка открыта; для финальных статусов polling не запускается.
 */
export function useEtranStatus(wagonId: string) {
  const history = ref<EtranHistoryResponse | null>(null)
  const isLoading = ref(false)
  const isRefreshing = ref(false)
  const fetchError = ref<string | null>(null)

  let pollTimer: ReturnType<typeof setInterval> | undefined

  const currentStatus = computed(
    () => history.value?.summary.current_status ?? null,
  )

  const shouldPoll = computed(() => {
    if (!currentStatus.value) return false
    return !FINAL_STATUSES.includes(currentStatus.value)
  })

  async function load(): Promise<void> {
    isLoading.value = true
    fetchError.value = null
    try {
      history.value = await fetchEtranHistory(wagonId)
    } catch (e) {
      fetchError.value = 'Не удалось загрузить историю документов ЭТРАН'
    } finally {
      isLoading.value = false
    }
  }

  async function refresh(): Promise<void> {
    if (isRefreshing.value) return
    isRefreshing.value = true
    fetchError.value = null
    try {
      await requestEtranRefresh(wagonId)
      await new Promise((resolve) => setTimeout(resolve, 2_000))
      await load()
    } catch {
      fetchError.value = 'Не удалось обновить статус ЭТРАН'
    } finally {
      isRefreshing.value = false
    }
  }

  function startPolling(): void {
    void load()
    pollTimer = setInterval(() => {
      if (shouldPoll.value) {
        void load()
      }
    }, POLL_INTERVAL_ACTIVE)
  }

  function stopPolling(): void {
    clearInterval(pollTimer)
  }

  onUnmounted(() => stopPolling())

  return {
    history,
    isLoading,
    isRefreshing,
    fetchError,
    currentStatus,
    shouldPoll,
    load,
    refresh,
    startPolling,
    stopPolling,
  }
}
