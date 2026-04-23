<template>
  <div class="filter-counter">
    <span class="filter-counter__text">
      Найдено: <strong>{{ total }}</strong>
    </span>
  </div>
</template>

<script setup lang="ts">
defineProps<{ total: number }>()
</script>

<style scoped>
.filter-counter {
  padding: 8px 0;
}

.filter-counter__text {
  font-size: 13px;
  color: #666;
}

.filter-counter__text strong {
  color: #333;
}
</style>
