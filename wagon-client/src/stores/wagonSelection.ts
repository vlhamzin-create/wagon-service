import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useWagonSelectionStore = defineStore('wagonSelection', () => {
  const selectedIds = ref<Set<string>>(new Set())

  const count = computed(() => selectedIds.value.size)
  const hasSelection = computed(() => count.value > 0)

  function toggle(id: string): void {
    const next = new Set(selectedIds.value)
    if (next.has(id)) {
      next.delete(id)
    } else {
      next.add(id)
    }
    selectedIds.value = next
  }

  function selectAll(ids: string[]): void {
    selectedIds.value = new Set(ids)
  }

  function clear(): void {
    selectedIds.value = new Set()
  }

  function isSelected(id: string): boolean {
    return selectedIds.value.has(id)
  }

  return { selectedIds, count, hasSelection, toggle, selectAll, clear, isSelected }
})
