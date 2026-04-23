<template>
  <div class="global-search">
    <input
      v-model="searchInput"
      type="search"
      class="global-search__input"
      placeholder="Поиск по всем полям..."
      aria-label="Глобальный поиск"
    />
    <button
      v-if="searchInput"
      class="global-search__clear"
      type="button"
      aria-label="Сбросить поиск"
      @click="resetSearch"
    >
      ✕
    </button>
  </div>
</template>

<script setup lang="ts">
import { useWagonFilters } from '@/composables/useWagonFilters'

const { searchInput, resetSearch } = useWagonFilters()
</script>

<style scoped>
.global-search {
  position: relative;
  display: inline-flex;
  align-items: center;
}

.global-search__input {
  width: 280px;
  padding: 6px 32px 6px 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 14px;
  outline: none;
}

.global-search__input:focus {
  border-color: #4a90e2;
  box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.2);
}

.global-search__clear {
  position: absolute;
  right: 8px;
  background: none;
  border: none;
  cursor: pointer;
  color: #999;
  font-size: 12px;
  padding: 0;
  line-height: 1;
}

.global-search__clear:hover {
  color: #333;
}
</style>
