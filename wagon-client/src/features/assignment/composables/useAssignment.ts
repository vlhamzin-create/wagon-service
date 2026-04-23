import { ref } from 'vue'
import { useAssignmentStore } from '../stores/assignmentStore'
import { useOverwriteCheck } from './useOverwriteCheck'
import { assignRoute } from '../api/assignmentApi'
import type { AssignRoutePayload } from '../types/assignment.types'

export function useAssignment() {
  const store = useAssignmentStore()
  const { needsConfirmation } = useOverwriteCheck()
  const showOverwriteModal = ref(false)
  const isSubmitting = ref(false)

  async function handleSubmit(): Promise<void> {
    if (needsConfirmation.value) {
      showOverwriteModal.value = true
      return
    }
    await executeAssignment()
  }

  async function confirmOverwrite(): Promise<void> {
    showOverwriteModal.value = false
    await executeAssignment()
  }

  function cancelOverwrite(): void {
    showOverwriteModal.value = false
  }

  async function executeAssignment(): Promise<void> {
    const { formState, wagons } = store

    const effectiveWagons = formState.onlyEmpty
      ? wagons.filter((w) => !w.hasExistingData)
      : wagons

    if (effectiveWagons.length === 0) return

    const payload: AssignRoutePayload = {
      wagon_ids: effectiveWagons.map((w) => w.wagonId),
      station_code: formState.selectedStation?.code ?? null,
      client_id: formState.selectedClient?.id ?? null,
      overwrite: !formState.onlyEmpty,
    }

    isSubmitting.value = true
    store.setProgress(0, effectiveWagons[0]?.wagonNumber ?? '')

    // Прогресс эмулируется, т.к. BE обрабатывает всё в одном запросе
    let progressStep = 0
    const progressInterval = setInterval(() => {
      progressStep = Math.min(progressStep + 1, effectiveWagons.length - 1)
      store.setProgress(progressStep, effectiveWagons[progressStep]?.wagonNumber ?? '')
    }, 200)

    try {
      const response = await assignRoute(payload)
      clearInterval(progressInterval)
      store.setResult(response)
    } catch {
      clearInterval(progressInterval)
      // Сетевая ошибка — формируем результат с ошибкой для всех вагонов
      store.setResult({
        total: effectiveWagons.length,
        succeeded: 0,
        skipped: 0,
        failed: effectiveWagons.length,
        results: effectiveWagons.map((w) => ({
          wagon_id: w.wagonId,
          status: 'error' as const,
          reason: 'Ошибка сети или сервера',
        })),
      })
    } finally {
      isSubmitting.value = false
    }
  }

  return {
    showOverwriteModal,
    isSubmitting,
    handleSubmit,
    confirmOverwrite,
    cancelOverwrite,
  }
}
