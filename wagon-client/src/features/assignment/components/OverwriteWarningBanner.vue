<script setup lang="ts">
defineProps<{ count: number }>()
</script>

<template>
  <div class="overwrite-banner">
    <span class="overwrite-banner__icon">⚠</span>
    <span class="overwrite-banner__text">
      У {{ count === 1 ? 'этого вагона' : `${count} вагонов` }} уже заполнены данные назначения.
      Текущие значения будут перезаписаны.
    </span>
  </div>
</template>

<style scoped>
.overwrite-banner {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 10px 12px;
  background: #fff3cd;
  border: 1px solid #ffc107;
  border-radius: 4px;
  font-size: 13px;
  color: #856404;
}

.overwrite-banner__icon {
  flex-shrink: 0;
  font-size: 14px;
}
</style>
