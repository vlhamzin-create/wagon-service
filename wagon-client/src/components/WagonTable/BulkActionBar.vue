<script setup lang="ts">
import { useWagonSelectionStore } from '@/stores/wagonSelection'

const selection = useWagonSelectionStore()

defineEmits<{ (e: 'assign'): void }>()
</script>

<template>
  <div v-if="selection.hasSelection" class="bulk-bar">
    <span class="bulk-bar__count">
      Выбрано: <strong>{{ selection.count }}</strong>
    </span>
    <button class="bulk-bar__btn bulk-bar__btn--assign" @click="$emit('assign')">
      Назначить
    </button>
    <button class="bulk-bar__btn" @click="selection.clear()">
      Снять выбор
    </button>
  </div>
</template>

<style scoped>
.bulk-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  background: #e8f4fd;
  border: 1px solid #b3d7f2;
  border-radius: 4px;
  font-size: 13px;
  color: #333;
}

.bulk-bar__count {
  margin-right: auto;
}

.bulk-bar__btn {
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
  border: 1px solid #ccc;
  background: #fff;
  color: #333;
}

.bulk-bar__btn:hover {
  background: #f5f5f5;
}

.bulk-bar__btn--assign {
  background: #4a90e2;
  color: #fff;
  border-color: #4a90e2;
}

.bulk-bar__btn--assign:hover {
  background: #357abd;
}
</style>
