<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  current: number
  total: number
  label?: string
}>()

const percent = computed(() =>
  props.total > 0 ? Math.round((props.current / props.total) * 100) : 0,
)
</script>

<template>
  <div class="base-progress">
    <div class="base-progress__info">
      <span v-if="label" class="base-progress__label">{{ label }}</span>
      <span class="base-progress__count">{{ current }} / {{ total }}</span>
    </div>
    <div class="base-progress__track">
      <div class="base-progress__fill" :style="{ width: `${percent}%` }" />
    </div>
  </div>
</template>

<style scoped>
.base-progress {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.base-progress__info {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: #666;
}

.base-progress__label {
  font-weight: 500;
}

.base-progress__count {
  color: #999;
}

.base-progress__track {
  height: 6px;
  background: #e0e0e0;
  border-radius: 3px;
  overflow: hidden;
}

.base-progress__fill {
  height: 100%;
  background: #4a90e2;
  border-radius: 3px;
  transition: width 0.3s ease;
}
</style>
