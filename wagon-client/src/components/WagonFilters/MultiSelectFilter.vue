<template>
  <div class="multi-select" :class="{ 'multi-select--open': isOpen }">
    <label class="multi-select__label" @click="toggle">{{ label }}</label>
    <div ref="containerRef" class="multi-select__container">
      <button
        type="button"
        class="multi-select__trigger"
        :aria-expanded="isOpen"
        @click="toggle"
      >
        <span v-if="!selected.length" class="multi-select__placeholder">— Все —</span>
        <span v-else class="multi-select__summary">{{ selected.length }} выбрано</span>
        <span class="multi-select__arrow">▾</span>
      </button>

      <div v-if="isOpen" class="multi-select__dropdown">
        <input
          ref="searchRef"
          v-model="searchQuery"
          type="text"
          class="multi-select__search"
          placeholder="Поиск…"
          @keydown.esc="close"
        />
        <ul class="multi-select__list">
          <li
            v-for="opt in filteredOptions"
            :key="opt.value"
            class="multi-select__item"
            @click="toggleOption(opt.value)"
          >
            <input
              type="checkbox"
              :checked="selected.includes(opt.value)"
              class="multi-select__checkbox"
              tabindex="-1"
            />
            <span class="multi-select__item-label">{{ opt.label }}</span>
          </li>
          <li v-if="!filteredOptions.length" class="multi-select__empty">Ничего не найдено</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import type { FilterOption } from '@/types/wagon'

interface Props {
  label: string
  options: FilterOption[]
  modelValue: string[] | undefined
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: undefined,
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: string[] | undefined): void
}>()

const isOpen = ref(false)
const searchQuery = ref('')
const searchRef = ref<HTMLInputElement | null>(null)
const containerRef = ref<HTMLElement | null>(null)

const selected = computed(() => props.modelValue ?? [])

const filteredOptions = computed(() => {
  if (!searchQuery.value) return props.options
  const q = searchQuery.value.toLowerCase()
  return props.options.filter((o) => o.label.toLowerCase().includes(q))
})

function toggle(): void {
  isOpen.value = !isOpen.value
  if (isOpen.value) {
    searchQuery.value = ''
    nextTick(() => searchRef.value?.focus())
  }
}

function close(): void {
  isOpen.value = false
}

function toggleOption(value: string): void {
  const current = [...selected.value]
  const idx = current.indexOf(value)
  if (idx >= 0) {
    current.splice(idx, 1)
  } else {
    current.push(value)
  }
  emit('update:modelValue', current.length ? current : undefined)
}

function onClickOutside(event: MouseEvent): void {
  if (containerRef.value && !containerRef.value.contains(event.target as Node)) {
    close()
  }
}

onMounted(() => {
  document.addEventListener('click', onClickOutside, true)
})

onUnmounted(() => {
  document.removeEventListener('click', onClickOutside, true)
})
</script>

<style scoped>
.multi-select {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.multi-select__label {
  font-size: 12px;
  color: #666;
  font-weight: 500;
  cursor: pointer;
}

.multi-select__container {
  position: relative;
}

.multi-select__trigger {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  min-width: 160px;
  padding: 5px 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  background: #fff;
  font-size: 13px;
  cursor: pointer;
  outline: none;
}

.multi-select__trigger:focus {
  border-color: #4a90e2;
  box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.2);
}

.multi-select__placeholder {
  color: #999;
}

.multi-select__summary {
  color: #333;
}

.multi-select__arrow {
  margin-left: 4px;
  font-size: 11px;
  color: #999;
}

.multi-select__dropdown {
  position: absolute;
  z-index: 100;
  top: calc(100% + 2px);
  left: 0;
  right: 0;
  background: #fff;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  max-height: 240px;
  display: flex;
  flex-direction: column;
}

.multi-select__search {
  padding: 6px 8px;
  border: none;
  border-bottom: 1px solid #eee;
  font-size: 13px;
  outline: none;
}

.multi-select__list {
  list-style: none;
  margin: 0;
  padding: 0;
  overflow-y: auto;
  flex: 1;
}

.multi-select__item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 5px 8px;
  cursor: pointer;
  font-size: 13px;
}

.multi-select__item:hover {
  background: #f0f7ff;
}

.multi-select__checkbox {
  pointer-events: none;
}

.multi-select__item-label {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.multi-select__empty {
  padding: 8px;
  font-size: 13px;
  color: #999;
  text-align: center;
}
</style>
