<template>
  <span v-if="calculatedAt" class="update-timestamp">
    Данные рассчитаны: {{ formatted }}
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  calculatedAt: string | null
}>()

const formatted = computed(() => {
  if (!props.calculatedAt) return ''
  return new Date(props.calculatedAt).toLocaleString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
})
</script>

<style scoped>
.update-timestamp {
  font-size: 13px;
  color: #999;
}
</style>
