<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  lastUpdatedAt: string | null
  nextPollAt: string | null
  isRefreshing: boolean
}>()

const emit = defineEmits<{ (e: 'refresh'): void }>()

function formatDate(iso: string): string {
  return new Date(iso).toLocaleString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const lastUpdatedLabel = computed(() =>
  props.lastUpdatedAt ? formatDate(props.lastUpdatedAt) : '—',
)

const nextPollLabel = computed(() =>
  props.nextPollAt ? formatDate(props.nextPollAt) : null,
)
</script>

<template>
  <div class="etran-sync">
    <div class="etran-sync__info">
      <span class="etran-sync__label">Последнее обновление ЭТРАН:</span>
      <span class="etran-sync__value">{{ lastUpdatedLabel }}</span>
    </div>
    <div v-if="nextPollLabel" class="etran-sync__info">
      <span class="etran-sync__label">Следующий опрос:</span>
      <span class="etran-sync__value">{{ nextPollLabel }}</span>
    </div>
    <button
      class="etran-sync__btn"
      type="button"
      :disabled="isRefreshing"
      @click="emit('refresh')"
    >
      <span v-if="isRefreshing" class="etran-sync__spinner" />
      {{ isRefreshing ? 'Обновление…' : 'Обновить' }}
    </button>
  </div>
</template>

<style scoped>
.etran-sync {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 8px 12px;
  background: #f9fafb;
  border: 1px solid #eee;
  border-radius: 6px;
  font-size: 13px;
}

.etran-sync__info {
  display: flex;
  align-items: center;
  gap: 4px;
}

.etran-sync__label {
  color: #888;
}

.etran-sync__value {
  color: #333;
  font-weight: 500;
}

.etran-sync__btn {
  margin-left: auto;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  background: #fff;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 13px;
  color: #333;
  cursor: pointer;
  transition: background 0.15s;
}

.etran-sync__btn:hover:not(:disabled) {
  background: #f3f4f6;
}

.etran-sync__btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.etran-sync__spinner {
  width: 14px;
  height: 14px;
  border: 2px solid #d1d5db;
  border-top-color: #333;
  border-radius: 50%;
  animation: etran-spin 0.6s linear infinite;
}

@keyframes etran-spin {
  to { transform: rotate(360deg); }
}
</style>
