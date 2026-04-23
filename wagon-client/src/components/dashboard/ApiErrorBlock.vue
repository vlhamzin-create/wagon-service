<template>
  <div class="api-error-block">
    <span class="api-error-block__icon">!</span>
    <span class="api-error-block__message">{{ message }}</span>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  message: string
}>()
</script>

<style scoped>
.api-error-block {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 16px;
  background: #fdf2f2;
  border: 1px solid #f5c6cb;
  border-radius: 6px;
}

.api-error-block__icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #d9534f;
  color: #fff;
  font-weight: 700;
  font-size: 14px;
  flex-shrink: 0;
}

.api-error-block__message {
  font-size: 14px;
  color: #a94442;
}
</style>
