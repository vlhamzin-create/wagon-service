import { computed } from 'vue'
import { useAssignmentStore } from '../stores/assignmentStore'

export function useOverwriteCheck() {
  const store = useAssignmentStore()

  const hasOverwriteTargets = computed(() => store.overwriteCount > 0)

  const showWarningBanner = computed(
    () => store.mode === 'single' && hasOverwriteTargets.value,
  )

  const needsConfirmation = computed(
    () =>
      store.mode === 'bulk' &&
      hasOverwriteTargets.value &&
      !store.formState.onlyEmpty,
  )

  return { hasOverwriteTargets, showWarningBanner, needsConfirmation }
}
