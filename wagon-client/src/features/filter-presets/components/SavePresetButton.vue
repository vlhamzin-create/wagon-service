<script setup lang="ts">
defineEmits<{ (e: 'click'): void }>()
</script>

<template>
  <button class="save-preset-btn" type="button" @click="$emit('click')">
    Сохранить как пресет
  </button>
</template>

<style scoped>
.save-preset-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  font-size: 13px;
  color: #1976d2;
  background: #fff;
  border: 1px solid #1976d2;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.15s, color 0.15s;
}

.save-preset-btn:hover {
  background: #1976d2;
  color: #fff;
}
</style>
