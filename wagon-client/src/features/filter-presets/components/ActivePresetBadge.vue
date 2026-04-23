<script setup lang="ts">
import { useFilterPresetsStore } from '../store/filterPresetsStore'
import { storeToRefs } from 'pinia'

const store = useFilterPresetsStore()
const { activePreset } = storeToRefs(store)

function clear() {
  store.clearActivePreset()
}
</script>

<template>
  <span v-if="activePreset" class="active-badge">
    <span class="active-badge__label">{{ activePreset.name }}</span>
    <button class="active-badge__clear" type="button" title="Сбросить" @click="clear">
      &#10005;
    </button>
  </span>
</template>

<style scoped>
.active-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 8px;
  font-size: 12px;
  color: #1976d2;
  background: #e3f2fd;
  border-radius: 12px;
}

.active-badge__label {
  max-width: 160px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.active-badge__clear {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 10px;
  color: #1976d2;
  padding: 0 2px;
  line-height: 1;
}

.active-badge__clear:hover {
  color: #d32f2f;
}
</style>
