<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { useWagonsStore } from '@/stores/wagons'

const { t } = useI18n()
const store = useWagonsStore()

interface Column {
  key: string
  label: string
  sortable: boolean
}

const COLUMNS: Column[] = [
  { key: 'number', label: t('table.number'), sortable: true },
  { key: 'owner_type', label: t('table.owner_type'), sortable: true },
  { key: 'wagon_type', label: t('table.wagon_type'), sortable: true },
  { key: 'current_city', label: t('table.current_city'), sortable: true },
  { key: 'current_station_name', label: t('table.current_station_name'), sortable: true },
  { key: 'current_country', label: t('table.current_country'), sortable: false },
  { key: 'status', label: t('table.status'), sortable: true },
  { key: 'requires_assignment', label: t('table.requires_assignment'), sortable: false },
  { key: 'source', label: t('table.source'), sortable: false },
  { key: 'updated_at', label: t('table.updated_at'), sortable: true },
]

defineExpose({ COLUMNS })
</script>

<template>
  <thead>
    <tr>
      <th
        v-for="col in COLUMNS"
        :key="col.key"
        :class="['wt-th', col.sortable ? 'wt-th--sortable' : '']"
        :aria-sort="
          store.sortBy === col.key
            ? store.sortDir === 'asc'
              ? 'ascending'
              : 'descending'
            : undefined
        "
        @click="col.sortable ? store.setSortBy(col.key) : undefined"
      >
        {{ col.label }}
        <span v-if="col.sortable && store.sortBy === col.key" class="wt-th__icon">
          {{ store.sortDir === 'asc' ? '↑' : '↓' }}
        </span>
      </th>
    </tr>
  </thead>
</template>

<style scoped>
.wt-th {
  padding: 10px 12px;
  text-align: left;
  background: #f5f5f5;
  border-bottom: 2px solid #e0e0e0;
  white-space: nowrap;
  user-select: none;
}

.wt-th--sortable {
  cursor: pointer;
}

.wt-th--sortable:hover {
  background: #ebebeb;
}

.wt-th__icon {
  margin-left: 4px;
  font-size: 0.8em;
}
</style>
