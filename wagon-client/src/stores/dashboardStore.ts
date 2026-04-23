import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useDashboardStore = defineStore('dashboard', () => {
  const selectedWagonType = ref<string | null>(null)

  function setWagonTypeFilter(type: string | null): void {
    selectedWagonType.value = type
  }

  return { selectedWagonType, setWagonTypeFilter }
})
