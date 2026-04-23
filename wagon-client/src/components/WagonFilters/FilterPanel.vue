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

    <div v-if="filterOptionsLoading" class="filter-panel__loading">Загрузка…</div>
    <div v-else-if="filterOptionsError" class="filter-panel__error">Не удалось загрузить фильтры</div>
    <template v-else-if="filterOptions">
      <!-- Дорога назначения — список (in) -->
      <FilterSelect
        field-name="destination_railway"
        label="Дорога назначения"
        :options="filterOptions.destination_railway"
        :multiple="true"
        :model-value="pendingFilters.destination_railway"
        @update:model-value="(v) => setListFilter('destination_railway', v as string[] | undefined)"
      />

      <!-- Поставщик — список (in) -->
      <FilterSelect
        field-name="supplier_name"
        label="Поставщик"
        :options="filterOptions.supplier_name"
        :multiple="true"
        :model-value="pendingFilters.supplier_name"
        @update:model-value="(v) => setListFilter('supplier_name', v as string[] | undefined)"
      />

      <!-- Город — список (in) -->
      <FilterSelect
        field-name="current_city"
        label="Текущий город"
        :options="filterOptions.current_city"
        :multiple="true"
        :model-value="pendingFilters.current_city"
        @update:model-value="(v) => setListFilter('current_city', v as string[] | undefined)"
      />

      <!-- Тип собственности — список (in) -->
      <FilterSelect
        field-name="owner_type"
        label="Тип собственности"
        :options="filterOptions.owner_type"
        :multiple="true"
        :model-value="pendingFilters.owner_type"
        @update:model-value="(v) => setListFilter('owner_type', v as string[] | undefined)"
      />

      <!-- Тип вагона — список (in) -->
      <FilterSelect
        field-name="wagon_type"
        label="Тип вагона"
        :options="filterOptions.wagon_type"
        :multiple="true"
        :model-value="pendingFilters.wagon_type"
        @update:model-value="(v) => setListFilter('wagon_type', v as string[] | undefined)"
      />

      <!-- Статус — список (in) -->
      <FilterSelect
        field-name="status"
        label="Статус"
        :options="filterOptions.status"
        :multiple="true"
        :model-value="pendingFilters.status"
        @update:model-value="(v) => setListFilter('status', v as string[] | undefined)"
      />

      <!-- Станция назначения — подстрока (substring) -->
      <FilterSearch
        field-name="destination_station_name"
        label="Станция назначения"
        placeholder="Подстрока..."
        :model-value="pendingFilters.current_station_name"
        @update:model-value="(v) => setSubstringFilter('current_station_name', v)"
      />
    </template>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useWagonFilters } from '@/composables/useWagonFilters'
import type { WagonFilters } from '@/types/wagon'
import FilterSelect from './FilterSelect.vue'
import FilterSearch from './FilterSearch.vue'

const { pendingFilters, resetFilters, filterOptions, filterOptionsLoading, filterOptionsError } =
  useWagonFilters()

type ActiveFilters = Omit<WagonFilters, 'mode' | 'search' | 'sort_by' | 'sort_dir'>

const hasActiveFilters = computed(() => {
  const f = pendingFilters.value
  return Object.values(f).some((v) =>
    Array.isArray(v) ? v.length > 0 : v !== undefined && v !== '',
  )
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
