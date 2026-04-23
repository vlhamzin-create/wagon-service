import { ref, computed } from 'vue'
import { fetchSyncStatus, triggerSync } from '@/api/sync'
import type { SourceStatus } from '@/types/api'

const POLL_INTERVAL_MS = 60_000

/**
 * Polling статуса синхронизации + ручной триггер.
 * Опрос раз в POLL_INTERVAL_MS; при triggerRefresh — немедленный перезапрос.
 */
export function useSyncStatus() {
  const sources = ref<SourceStatus[]>([])
  const isRefreshing = ref(false)
  const error = ref<string | null>(null)

  let pollTimer: ReturnType<typeof setInterval> | undefined

  async function _fetch(): Promise<void> {
    try {
      const data = await fetchSyncStatus()
      sources.value = data.sources
      error.value = null
    } catch (e) {
      error.value = e instanceof Error ? e.message : String(e)
    }
  }

  function startPolling(): void {
    void _fetch()
    pollTimer = setInterval(() => void _fetch(), POLL_INTERVAL_MS)
  }

  function stopPolling(): void {
    clearInterval(pollTimer)
  }

  async function triggerRefresh(): Promise<void> {
    if (isRefreshing.value) return
    isRefreshing.value = true
    try {
      await triggerSync()
      // Даём бэкенду немного времени записать статус, затем обновляем
      await new Promise((resolve) => setTimeout(resolve, 1500))
      await _fetch()
    } catch (e) {
      error.value = e instanceof Error ? e.message : String(e)
    } finally {
      isRefreshing.value = false
    }
  }

  const showWarning = computed(() => sources.value.some((s) => s.last_status === 'error'))

  return { sources, isRefreshing, error, showWarning, startPolling, stopPolling, triggerRefresh }
}
