<template>
  <div class="station-autocomplete">
    <label class="station-autocomplete__label" :for="inputId">{{ label }}</label>
    <div ref="containerRef" class="station-autocomplete__wrap">
      <input
        :id="inputId"
        v-model="localValue"
        type="text"
        class="station-autocomplete__input"
        :placeholder="placeholder"
        autocomplete="off"
        @focus="onFocus"
        @keydown.esc="closeSuggestions"
      />
      <button
        v-if="localValue"
        class="station-autocomplete__clear"
        type="button"
        aria-label="Сбросить"
        @click="clear"
      >
        ✕
      </button>

      <ul v-if="showSuggestions && suggestions.length" class="station-autocomplete__suggestions">
        <li
          v-for="s in suggestions"
          :key="s"
          class="station-autocomplete__suggestion"
          @mousedown.prevent="selectSuggestion(s)"
        >
          {{ s }}
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'

interface Props {
  fieldName: string
  label: string
  placeholder?: string
  modelValue: string | undefined
  stations: string[]
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: 'Начните вводить…',
  modelValue: undefined,
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: string | undefined): void
}>()

const inputId = computed(() => `station-autocomplete-${props.fieldName}`)

const localValue = ref(props.modelValue ?? '')
const showSuggestions = ref(false)
const containerRef = ref<HTMLElement | null>(null)

const suggestions = computed(() => {
  if (!localValue.value || localValue.value.length < 2) return []
  const q = localValue.value.toLowerCase()
  return props.stations.filter((s) => s.toLowerCase().includes(q)).slice(0, 10)
})

watch(
  () => props.modelValue,
  (v) => {
    localValue.value = v ?? ''
  },
)

watch(localValue, (v) => {
  emit('update:modelValue', v || undefined)
  showSuggestions.value = true
})

function onFocus(): void {
  showSuggestions.value = true
}

function closeSuggestions(): void {
  showSuggestions.value = false
}

function selectSuggestion(value: string): void {
  localValue.value = value
  showSuggestions.value = false
}

function clear(): void {
  localValue.value = ''
}

function onClickOutside(event: MouseEvent): void {
  if (containerRef.value && !containerRef.value.contains(event.target as Node)) {
    closeSuggestions()
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
.station-autocomplete {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.station-autocomplete__label {
  font-size: 12px;
  color: #666;
  font-weight: 500;
}

.station-autocomplete__wrap {
  position: relative;
  display: inline-flex;
  align-items: center;
}

.station-autocomplete__input {
  border: 1px solid #ccc;
  border-radius: 4px;
  padding: 5px 28px 5px 8px;
  font-size: 13px;
  outline: none;
  min-width: 160px;
  width: 100%;
}

.station-autocomplete__input:focus {
  border-color: #4a90e2;
  box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.2);
}

.station-autocomplete__clear {
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

.station-autocomplete__clear:hover {
  color: #333;
}

.station-autocomplete__suggestions {
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

.station-autocomplete__suggestion {
  padding: 6px 8px;
  font-size: 13px;
  cursor: pointer;
}

.station-autocomplete__suggestion:hover {
  background: #f0f7ff;
}
</style>
