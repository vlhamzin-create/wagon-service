<template>
  <div class="metric-card" :class="{ 'metric-card--loading': isLoading }">
    <span class="metric-card__label">{{ label }}</span>
    <span class="metric-card__value">
      <template v-if="isLoading">—</template>
      <template v-else>{{ value.toLocaleString('ru-RU') }}</template>
    </span>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  label: string
  value: number
  isLoading: boolean
}>()
</script>

<style scoped>
.metric-card {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 16px;
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  min-width: 140px;
}

.metric-card--loading {
  opacity: 0.5;
}

.metric-card__label {
  font-size: 13px;
  color: #666;
}

.metric-card__value {
  font-size: 24px;
  font-weight: 600;
  color: #333;
}
</style>
