<template>
  <div class="filter-select">
    <label class="filter-select__label" :for="inputId">{{ label }}</label>
    <select
      :id="inputId"
      :multiple="multiple"
      :value="modelValue"
      class="filter-select__select"
      @change="onChange"
    >
      <option value="">— Все —</option>
      <option v-for="opt in options" :key="opt.value" :value="opt.value">
        {{ opt.label }}
      </option>
    </select>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { FilterOption } from '@/types/wagon'

interface Props {
  /** Идентификатор поля (используется в for/id). */
  fieldName: string
  label: string
  options: FilterOption[]
  /** Одиночный выбор (exact) или множественный (in). */
  multiple?: boolean
  /** v-model: строка для exact, массив строк для in. */
  modelValue: string | string[] | undefined
}

const props = withDefaults(defineProps<Props>(), {
  multiple: false,
  modelValue: undefined,
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: string | string[] | undefined): void
}>()

const inputId = computed(() => `filter-select-${props.fieldName}`)

function onChange(event: Event): void {
  const select = event.target as HTMLSelectElement
  if (props.multiple) {
    const selected = Array.from(select.selectedOptions)
      .map((o) => o.value)
      .filter(Boolean)
    emit('update:modelValue', selected.length ? selected : undefined)
  } else {
    const val = select.value
    emit('update:modelValue', val || undefined)
  }
}
</script>

<style scoped>
.filter-select {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.filter-select__label {
  font-size: 12px;
  color: #666;
  font-weight: 500;
}

.filter-select__select {
  border: 1px solid #ccc;
  border-radius: 4px;
  padding: 5px 8px;
  font-size: 13px;
  background: #fff;
  outline: none;
  min-width: 160px;
}

.filter-select__select:focus {
  border-color: #4a90e2;
  box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.2);
}

.filter-select__select[multiple] {
  min-height: 80px;
}
</style>
