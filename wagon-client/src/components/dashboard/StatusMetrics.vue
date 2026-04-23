<template>
  <section class="status-metrics">
    <h2 class="status-metrics__title">Показатели состояния вагонов</h2>
    <div class="status-metrics__grid">
      <MetricCard
        v-for="metric in metrics"
        :key="metric.key"
        :label="metric.label"
        :value="metric.value"
        :is-loading="isLoading"
      />
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import MetricCard from './MetricCard.vue'
import type { CategoryCounts, DestinationRailwayRow } from '@/api/dashboard'

const props = defineProps<{
  rows: DestinationRailwayRow[]
  isLoading: boolean
}>()

const totals = computed<CategoryCounts>(() => {
  const zero: CategoryCounts = {
    under_loading: 0,
    going_to_loading: 0,
    under_unloading: 0,
    going_to_unloading: 0,
    without_assignment: 0,
    without_assignment_in_transit: 0,
  }
  return props.rows.reduce((acc, row) => {
    ;(Object.keys(acc) as (keyof CategoryCounts)[]).forEach((k) => {
      acc[k] += row[k]
    })
    return acc
  }, { ...zero })
})

const metrics = computed(() => [
  { key: 'under_loading', label: 'Под погрузкой', value: totals.value.under_loading },
  { key: 'going_to_loading', label: 'Едут под погрузку', value: totals.value.going_to_loading },
  { key: 'under_unloading', label: 'Под выгрузкой', value: totals.value.under_unloading },
  { key: 'going_to_unloading', label: 'Едут под выгрузку', value: totals.value.going_to_unloading },
  { key: 'without_assignment', label: 'Без назначения', value: totals.value.without_assignment },
  { key: 'without_assignment_in_transit', label: 'Без назначения в пути', value: totals.value.without_assignment_in_transit },
])
</script>

<style scoped>
.status-metrics__title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0 0 12px;
}

.status-metrics__grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 12px;
}
</style>
