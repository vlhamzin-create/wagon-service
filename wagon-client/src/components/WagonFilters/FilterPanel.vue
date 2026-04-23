<template>
  <aside class="filter-panel">
    <div class="filter-panel__header">
      <span class="filter-panel__title">Фильтры</span>
      <button
        v-if="hasActiveFilters"
        class="filter-panel__reset"
        type="button"
        @click="resetFilters"
      >
        Сбросить всё
      </button>
    </div>

    <SyncWarning :sources="sources" />

    <FilterCounter :total="total" />

    <div v-if="filterOptionsLoading" class="filter-panel__loading">Загрузка…</div>
    <div v-else-if="filterOptionsError" class="filter-panel__error">Не удалось загрузить фильтры</div>
    <template v-else-if="filterOptions">
      <!-- Дорога назначения — мультивыбор с поиском -->
      <MultiSelectFilter
        label="Дорога назначения"
        :options="filterOptions.destination_railway"
        :model-value="pendingFilters.destination_railway"
        @update:model-value="(v) => setListFilter('destination_railway', v)"
      />

      <!-- Поставщик — мультивыбор с поиском -->
      <MultiSelectFilter
        label="Поставщик"
        :options="filterOptions.supplier_name"
        :model-value="pendingFilters.supplier_name"
        @update:model-value="(v) => setListFilter('supplier_name', v)"
      />

      <!-- Город — мультивыбор с поиском -->
      <MultiSelectFilter
        label="Текущий город"
        :options="filterOptions.current_city"
        :model-value="pendingFilters.current_city"
        @update:model-value="(v) => setListFilter('current_city', v)"
      />

      <!-- Тип собственности — мультивыбор с поиском -->
      <MultiSelectFilter
        label="Тип собственности"
        :options="filterOptions.owner_type"
        :model-value="pendingFilters.owner_type"
        @update:model-value="(v) => setListFilter('owner_type', v)"
      />

      <!-- Тип вагона — мультивыбор с поиском -->
      <MultiSelectFilter
        label="Тип вагона"
        :options="filterOptions.wagon_type"
        :model-value="pendingFilters.wagon_type"
        @update:model-value="(v) => setListFilter('wagon_type', v)"
      />

      <!-- Статус — мультивыбор с поиском -->
      <MultiSelectFilter
        label="Статус"
        :options="filterOptions.status"
        :model-value="pendingFilters.status"
        @update:model-value="(v) => setListFilter('status', v)"
      />

      <!-- Станция назначения — автодополнение -->
      <StationAutocomplete
        field-name="current_station_name"
        label="Станция назначения"
        :stations="stationNames"
        :model-value="currentStationSearch"
        @update:model-value="(v) => setSubstringFilter('current_station_name', v)"
      />
    </template>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useWagonFilters } from '@/composables/useWagonFilters'
import { useSyncStatus } from '@/composables/useSyncStatus'
import type { WagonFilters } from '@/types/wagon'
import MultiSelectFilter from './MultiSelectFilter.vue'
import StationAutocomplete from './StationAutocomplete.vue'
import FilterCounter from './FilterCounter.vue'
import SyncWarning from './SyncWarning.vue'

interface Props {
  total: number
}

defineProps<Props>()

const { pendingFilters, resetFilters, filterOptions, filterOptionsLoading, filterOptionsError } =
  useWagonFilters()

const { sources } = useSyncStatus()

type ActiveFilters = Omit<WagonFilters, 'mode' | 'search' | 'sort_by' | 'sort_dir'>

const hasActiveFilters = computed(() => {
  const f = pendingFilters.value
  return Object.values(f).some((v) =>
    Array.isArray(v) ? v.length > 0 : v !== undefined && v !== '',
  )
})

const stationNames = computed(() => {
  if (!filterOptions.value) return []
  const cityOptions = filterOptions.value.current_city
  return cityOptions ? cityOptions.map((o) => o.label) : []
})

const currentStationSearch = computed(() => {
  const val = pendingFilters.value.current_station_name
  return Array.isArray(val) && val.length > 0 ? val[0] : undefined
})

function setListFilter(field: keyof ActiveFilters, value: string[] | undefined): void {
  pendingFilters.value = {
    ...pendingFilters.value,
    [field]: value,
  }
}

function setSubstringFilter(field: keyof ActiveFilters, value: string | undefined): void {
  pendingFilters.value = {
    ...pendingFilters.value,
    [field]: value ? [value] : undefined,
  }
}
</script>

<style scoped>
.filter-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 16px;
  background: #f9f9f9;
  border-right: 1px solid #e0e0e0;
  min-width: 220px;
}

.filter-panel__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.filter-panel__title {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.filter-panel__reset {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 12px;
  color: #4a90e2;
  padding: 0;
}

.filter-panel__reset:hover {
  text-decoration: underline;
}

.filter-panel__loading,
.filter-panel__error {
  font-size: 13px;
  color: #999;
}

.filter-panel__error {
  color: #d9534f;
}
</style>
