<template>
  <div class="wagon-type-filter">
    <label class="wagon-type-filter__label" for="wagon-type-select">Тип вагона:</label>
    <select
      id="wagon-type-select"
      class="wagon-type-filter__select"
      :value="store.selectedWagonType ?? ''"
      @change="onChange"
    >
      <option value="">Все типы</option>
      <option v-for="wt in availableTypes" :key="wt" :value="wt">
        {{ wt }}
      </option>
    </select>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useDashboardStore } from '@/stores/dashboardStore'
import type { WagonTypeSummaryRow } from '@/api/dashboard'

const props = defineProps<{
  wagonTypes: WagonTypeSummaryRow[]
}>()

const store = useDashboardStore()

const availableTypes = computed(() => props.wagonTypes.map((row) => row.wagon_type))

function onChange(e: Event): void {
  const value = (e.target as HTMLSelectElement).value || null
  store.setWagonTypeFilter(value)
}
</script>

<style scoped>
.wagon-type-filter {
  display: flex;
  align-items: center;
  gap: 8px;
}

.wagon-type-filter__label {
  font-size: 14px;
  color: #333;
  white-space: nowrap;
}

.wagon-type-filter__select {
  padding: 6px 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 14px;
  color: #333;
  background: #fff;
  min-width: 180px;
}

.wagon-type-filter__select:focus {
  outline: none;
  border-color: #4a90e2;
}
</style>
