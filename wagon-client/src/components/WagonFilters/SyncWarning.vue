<template>
  <div v-if="hasError" class="sync-warning" role="alert">
    <span class="sync-warning__icon">⚠</span>
    <span class="sync-warning__text">
      Ошибка синхронизации RWL.
      <template v-if="errorMessage"> {{ errorMessage }}</template>
      Данные могут быть неактуальны.
    </span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { SourceStatus } from '@/types/api'

const props = defineProps<{
  sources: SourceStatus[]
}>()

const failedSources = computed(() =>
  props.sources.filter((s) => s.last_status === 'error'),
)

const hasError = computed(() => failedSources.value.length > 0)

const errorMessage = computed(() => {
  const errors = failedSources.value
    .map((s) => s.last_error)
    .filter(Boolean)
  return errors.length ? errors.join('; ') : ''
})
</script>

<style scoped>
.sync-warning {
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

.sync-warning__icon {
  flex-shrink: 0;
  font-size: 14px;
}

.sync-warning__text {
  line-height: 1.4;
}
</style>
