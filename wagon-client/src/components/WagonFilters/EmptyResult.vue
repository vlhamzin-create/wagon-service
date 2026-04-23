<template>
  <div class="empty-result">
    <p class="empty-result__text">{{ message }}</p>
    <button
      v-if="showReset"
      type="button"
      class="empty-result__reset"
      @click="$emit('reset')"
    >
      Сбросить фильтры
    </button>
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    message?: string
    showReset?: boolean
  }>(),
  {
    message: 'По выбранным фильтрам ничего не найдено',
    showReset: true,
  },
)

defineEmits<{
  (e: 'reset'): void
}>()
</script>

<style scoped>
.empty-result {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 32px 16px;
  color: #999;
}

.empty-result__text {
  font-size: 14px;
  margin: 0;
}

.empty-result__reset {
  background: none;
  border: 1px solid #4a90e2;
  border-radius: 4px;
  color: #4a90e2;
  padding: 6px 16px;
  font-size: 13px;
  cursor: pointer;
}

.empty-result__reset:hover {
  background: #f0f7ff;
}
</style>
