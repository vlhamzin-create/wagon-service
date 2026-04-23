<script setup lang="ts" generic="T extends { id: string }">
import { ref, computed, onMounted, onUnmounted } from 'vue'

interface Props {
  label: string
  placeholder?: string
  displayFn: (item: T) => string
  items: T[]
  modelValue: T | null
  loading?: boolean
  error?: string | null
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: 'Начните вводить…',
  loading: false,
  error: null,
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: T | null): void
  (e: 'search', query: string): void
}>()

const inputValue = ref('')
const isOpen = ref(false)
const containerRef = ref<HTMLElement | null>(null)

const displayValue = computed(() => {
  if (props.modelValue) return props.displayFn(props.modelValue)
  return inputValue.value
})

function onInputChange(event: Event): void {
  const value = (event.target as HTMLInputElement).value
  inputValue.value = value
  if (props.modelValue) {
    emit('update:modelValue', null)
  }
  emit('search', value)
  isOpen.value = true
}

function onFocus(): void {
  isOpen.value = true
}

function select(item: T): void {
  emit('update:modelValue', item)
  inputValue.value = ''
  isOpen.value = false
}

function clear(): void {
  inputValue.value = ''
  emit('update:modelValue', null)
  emit('search', '')
}

function onClickOutside(event: MouseEvent): void {
  if (containerRef.value && !containerRef.value.contains(event.target as Node)) {
    isOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', onClickOutside, true)
})

onUnmounted(() => {
  document.removeEventListener('click', onClickOutside, true)
})
</script>

<template>
  <div class="base-combobox">
    <label class="base-combobox__label">{{ label }}</label>
    <div ref="containerRef" class="base-combobox__wrap">
      <input
        type="text"
        class="base-combobox__input"
        :placeholder="placeholder"
        :value="displayValue"
        autocomplete="off"
        @input="onInputChange"
        @focus="onFocus"
        @keydown.esc="isOpen = false"
      />
      <span v-if="loading" class="base-combobox__spinner" />
      <button
        v-if="modelValue || inputValue"
        class="base-combobox__clear"
        type="button"
        aria-label="Сбросить"
        @click="clear"
      >
        ✕
      </button>

      <ul v-if="isOpen && items.length > 0" class="base-combobox__list">
        <li
          v-for="item in items"
          :key="item.id"
          class="base-combobox__option"
          @mousedown.prevent="select(item)"
        >
          <slot name="option" :item="item">
            {{ displayFn(item) }}
          </slot>
        </li>
      </ul>

      <div v-if="isOpen && !loading && items.length === 0 && inputValue.length >= 2" class="base-combobox__empty">
        Ничего не найдено
      </div>
    </div>
    <span v-if="error" class="base-combobox__error">{{ error }}</span>
  </div>
</template>

<style scoped>
.base-combobox {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.base-combobox__label {
  font-size: 12px;
  color: #666;
  font-weight: 500;
}

.base-combobox__wrap {
  position: relative;
  display: inline-flex;
  align-items: center;
}

.base-combobox__input {
  border: 1px solid #ccc;
  border-radius: 4px;
  padding: 5px 28px 5px 8px;
  font-size: 13px;
  outline: none;
  min-width: 160px;
  width: 100%;
}

.base-combobox__input:focus {
  border-color: #4a90e2;
  box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.2);
}

.base-combobox__clear {
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

.base-combobox__clear:hover {
  color: #333;
}

.base-combobox__spinner {
  position: absolute;
  right: 24px;
  width: 12px;
  height: 12px;
  border: 2px solid #ccc;
  border-top-color: #4a90e2;
  border-radius: 50%;
  animation: combobox-spin 0.6s linear infinite;
}

@keyframes combobox-spin {
  to { transform: rotate(360deg); }
}

.base-combobox__list {
  position: absolute;
  z-index: 100;
  top: calc(100% + 2px);
  left: 0;
  right: 0;
  list-style: none;
  margin: 0;
  padding: 0;
  background: #fff;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  max-height: 180px;
  overflow-y: auto;
}

.base-combobox__option {
  padding: 6px 8px;
  font-size: 13px;
  cursor: pointer;
}

.base-combobox__option:hover {
  background: #f0f7ff;
}

.base-combobox__empty {
  position: absolute;
  z-index: 100;
  top: calc(100% + 2px);
  left: 0;
  right: 0;
  padding: 8px;
  font-size: 13px;
  color: #999;
  background: #fff;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.base-combobox__error {
  font-size: 11px;
  color: #e53e3e;
}
</style>
