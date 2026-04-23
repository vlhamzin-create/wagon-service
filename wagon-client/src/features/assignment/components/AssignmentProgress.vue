<script setup lang="ts">
import BaseProgressBar from '@/shared/components/BaseProgressBar.vue'
import { useAssignmentStore } from '../stores/assignmentStore'

const store = useAssignmentStore()
</script>

<template>
  <div class="assignment-progress">
    <p class="assignment-progress__title">Выполняется назначение…</p>
    <BaseProgressBar
      :current="store.progress.current"
      :total="store.progress.total"
      :label="store.progress.currentWagonNumber"
    />
  </div>
</template>

<style scoped>
.assignment-progress {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 20px 0;
}

.assignment-progress__title {
  margin: 0;
  font-size: 14px;
  font-weight: 500;
  color: #333;
}
</style>
