<template>
  <div class="filter-search">
    <label class="filter-search__label" :for="inputId">{{ label }}</label>
    <div class="filter-search__wrap">
      <input
        :id="inputId"
        v-model="localValue"
        type="text"
        class="filter-search__input"
        :placeholder="placeholder"
      />
      <button
        v-if="localValue"
        class="filter-search__clear"
        type="button"
        aria-label="Сбросить"
        @click="clear"
      >
        ✕
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, watch } from 'vue'

interface Props {
  fieldName: string
  label: string
  placeholder?: string
  modelValue: string | undefined
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: 'Подстрока...',
  modelValue: undefined,
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: string | undefined): void
}>()

const inputId = computed(() => `filter-search-${props.fieldName}`)

// Локальный ref для мгновенного отклика v-model; родитель применяет debounce
import { ref } from 'vue'
const localValue = ref(props.modelValue ?? '')

watch(
  () => props.modelValue,
  (v) => {
    localValue.value = v ?? ''
  },
)

watch(localValue, (v) => {
  emit('update:modelValue', v || undefined)
})

function clear(): void {
  localValue.value = ''
}
</script>

<style scoped>
.filter-search {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.filter-search__label {
  font-size: 12px;
  color: #666;
  font-weight: 500;
}

.filter-search__wrap {
  position: relative;
  display: inline-flex;
  align-items: center;
}

.filter-search__input {
  border: 1px solid #ccc;
  border-radius: 4px;
  padding: 5px 28px 5px 8px;
  font-size: 13px;
  outline: none;
  min-width: 160px;
}

.filter-search__input:focus {
  border-color: #4a90e2;
  box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.2);
}

.filter-search__clear {
  position: absolute;
  right: 6px;
  background: none;
  border: none;
  cursor: pointer;
  color: #999;
  font-size: 11px;
  padding: 0;
  line-height: 1;
}

.filter-search__clear:hover {
  color: #333;
}
</style>
