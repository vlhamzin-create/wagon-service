<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useFilterPresets } from '../composables/useFilterPresets'
import PresetListItem from './PresetListItem.vue'
import type { FilterPreset } from '../types/filterPreset.types'

const emit = defineEmits<{
  (e: 'edit', preset: FilterPreset): void
  (e: 'delete', preset: FilterPreset): void
}>()

const { presets, activePresetId, loading, error, applyPreset, fetchPresets } = useFilterPresets()

const isOpen = ref(false)
const panelRef = ref<HTMLElement | null>(null)

function toggle() {
  isOpen.value = !isOpen.value
}

function handleClickOutside(event: MouseEvent) {
  if (panelRef.value && !panelRef.value.contains(event.target as Node)) {
    isOpen.value = false
  }
}

function handleApply(preset: FilterPreset) {
  applyPreset(preset)
  isOpen.value = false
}

onMounted(() => {
  fetchPresets()
  document.addEventListener('click', handleClickOutside, true)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside, true)
})
</script>

<template>
  <div ref="panelRef" class="preset-list">
    <button class="preset-list__trigger" type="button" @click="toggle">
      Пресеты фильтров
      <span class="preset-list__count" v-if="presets.length">({{ presets.length }})</span>
    </button>

    <div v-if="isOpen" class="preset-list__dropdown">
      <div v-if="loading" class="preset-list__status">Загрузка...</div>
      <div v-else-if="error" class="preset-list__status preset-list__status--error">
        {{ error }}
      </div>
      <div v-else-if="!presets.length" class="preset-list__status">
        Нет сохранённых пресетов
      </div>
      <ul v-else class="preset-list__items">
        <PresetListItem
          v-for="preset in presets"
          :key="preset.id"
          :preset="preset"
          :is-active="preset.id === activePresetId"
          @apply="handleApply"
          @edit="emit('edit', $event)"
          @delete="emit('delete', $event)"
        />
      </ul>
    </div>
  </div>
</template>

<style scoped>
.preset-list {
  position: relative;
  display: inline-block;
}

.preset-list__trigger {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  font-size: 13px;
  color: #555;
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 6px;
  cursor: pointer;
  transition: border-color 0.15s;
}

.preset-list__trigger:hover {
  border-color: #aaa;
}

.preset-list__count {
  color: #888;
  font-size: 12px;
}

.preset-list__dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  z-index: 1000;
  margin-top: 4px;
  min-width: 240px;
  max-height: 320px;
  overflow-y: auto;
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  padding: 6px;
}

.preset-list__items {
  list-style: none;
  margin: 0;
  padding: 0;
}

.preset-list__status {
  padding: 12px;
  text-align: center;
  font-size: 13px;
  color: #888;
}

.preset-list__status--error {
  color: #d32f2f;
}
</style>
