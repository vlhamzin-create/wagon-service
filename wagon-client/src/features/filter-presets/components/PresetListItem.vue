<script setup lang="ts">
import { ref } from 'vue'
import type { FilterPreset } from '../types/filterPreset.types'

const props = defineProps<{
  preset: FilterPreset
  isActive: boolean
}>()

const emit = defineEmits<{
  (e: 'apply', preset: FilterPreset): void
  (e: 'edit', preset: FilterPreset): void
  (e: 'delete', preset: FilterPreset): void
}>()

const showActions = ref(false)
</script>

<template>
  <li
    class="preset-item"
    :class="{ 'preset-item--active': isActive }"
    @mouseenter="showActions = true"
    @mouseleave="showActions = false"
  >
    <button
      class="preset-item__name"
      type="button"
      :title="props.preset.name"
      @click="emit('apply', props.preset)"
    >
      {{ props.preset.name }}
    </button>
    <div v-show="showActions" class="preset-item__actions">
      <button
        class="preset-item__action"
        type="button"
        title="Редактировать"
        @click.stop="emit('edit', props.preset)"
      >
        &#9998;
      </button>
      <button
        class="preset-item__action preset-item__action--danger"
        type="button"
        title="Удалить"
        @click.stop="emit('delete', props.preset)"
      >
        &#10005;
      </button>
    </div>
  </li>
</template>

<style scoped>
.preset-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 12px;
  border-radius: 4px;
  transition: background-color 0.15s;
}

.preset-item:hover {
  background: #f5f5f5;
}

.preset-item--active {
  background: #e8f0fe;
}

.preset-item__name {
  flex: 1;
  text-align: left;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 13px;
  color: #333;
  padding: 2px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.preset-item__actions {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
  margin-left: 8px;
}

.preset-item__action {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 12px;
  color: #888;
  padding: 2px 4px;
  border-radius: 3px;
  line-height: 1;
}

.preset-item__action:hover {
  color: #333;
  background: #e0e0e0;
}

.preset-item__action--danger:hover {
  color: #d32f2f;
  background: #fce4ec;
}
</style>
