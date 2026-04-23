import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  PanelMode,
  PanelPhase,
  WagonAssignmentState,
  AssignRouteResponse,
  AssignmentFormState,
  Station,
  Client,
} from '../types/assignment.types'

export const useAssignmentStore = defineStore('assignment', () => {
  const isOpen = ref(false)
  const mode = ref<PanelMode>('single')
  const phase = ref<PanelPhase>('form')
  const wagons = ref<WagonAssignmentState[]>([])

  const formState = ref<AssignmentFormState>({
    selectedStation: null,
    selectedClient: null,
    comment: '',
    onlyEmpty: false,
  })

  const progress = ref({ current: 0, total: 0, currentWagonNumber: '' })
  const result = ref<AssignRouteResponse | null>(null)

  // Геттеры
  const wagonsWithExistingData = computed(() =>
    wagons.value.filter((w) => w.hasExistingData),
  )

  const overwriteCount = computed(() => wagonsWithExistingData.value.length)

  const effectiveWagonCount = computed(() =>
    formState.value.onlyEmpty
      ? wagons.value.filter((w) => !w.hasExistingData).length
      : wagons.value.length,
  )

  const canSave = computed(
    () =>
      formState.value.selectedStation !== null ||
      formState.value.selectedClient !== null,
  )

  // Действия
  function _resetForm(): void {
    formState.value = {
      selectedStation: null,
      selectedClient: null,
      comment: '',
      onlyEmpty: false,
    }
  }

  function openForSingle(wagon: WagonAssignmentState): void {
    wagons.value = [wagon]
    mode.value = 'single'
    phase.value = 'form'
    result.value = null
    _resetForm()
    isOpen.value = true
  }

  function openForBulk(items: WagonAssignmentState[]): void {
    wagons.value = items
    mode.value = 'bulk'
    phase.value = 'form'
    result.value = null
    _resetForm()
    isOpen.value = true
  }

  function setProgress(current: number, currentWagonNumber: string): void {
    progress.value = { current, total: wagons.value.length, currentWagonNumber }
    phase.value = 'progress'
  }

  function setResult(response: AssignRouteResponse): void {
    result.value = response
    phase.value = 'result'
  }

  function close(): void {
    isOpen.value = false
  }

  function retryFailed(): void {
    if (!result.value) return
    const failedIds = result.value.results
      .filter((r) => r.status === 'error')
      .map((r) => r.wagon_id)
    const failedWagons = wagons.value.filter((w) =>
      failedIds.includes(w.wagonId),
    )
    openForBulk(failedWagons)
  }

  function setStation(station: Station | null): void {
    formState.value.selectedStation = station
  }

  function setClient(client: Client | null): void {
    formState.value.selectedClient = client
  }

  return {
    isOpen,
    mode,
    phase,
    wagons,
    formState,
    progress,
    result,
    wagonsWithExistingData,
    overwriteCount,
    effectiveWagonCount,
    canSave,
    openForSingle,
    openForBulk,
    setProgress,
    setResult,
    close,
    retryFailed,
    setStation,
    setClient,
  }
})
