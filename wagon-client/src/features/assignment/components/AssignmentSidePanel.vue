<script setup lang="ts">
import { computed } from 'vue'
import BaseSidePanel from '@/shared/components/BaseSidePanel.vue'
import SingleAssignmentForm from './SingleAssignmentForm.vue'
import BulkAssignmentForm from './BulkAssignmentForm.vue'
import AssignmentProgress from './AssignmentProgress.vue'
import AssignmentResult from './AssignmentResult.vue'
import OverwriteConfirmModal from './OverwriteConfirmModal.vue'
import { useAssignmentStore } from '../stores/assignmentStore'
import { useAssignment } from '../composables/useAssignment'

const store = useAssignmentStore()
const {
  showOverwriteModal,
  handleSubmit,
  confirmOverwrite,
  cancelOverwrite,
} = useAssignment()

const panelTitle = computed(() => {
  if (store.phase === 'result') return 'Результат назначения'
  if (store.phase === 'progress') return 'Назначение…'
  return store.mode === 'single' ? 'Назначение вагона' : 'Массовое назначение'
})
</script>

<template>
  <BaseSidePanel :open="store.isOpen" :title="panelTitle" @close="store.close()">
    <template v-if="store.phase === 'form'">
      <SingleAssignmentForm v-if="store.mode === 'single'" @submit="handleSubmit" />
      <BulkAssignmentForm v-else @submit="handleSubmit" />
    </template>

    <AssignmentProgress v-else-if="store.phase === 'progress'" />

    <AssignmentResult v-else-if="store.phase === 'result'" />
  </BaseSidePanel>

  <OverwriteConfirmModal
    :open="showOverwriteModal"
    :count="store.overwriteCount"
    @confirm="confirmOverwrite"
    @cancel="cancelOverwrite"
  />
</template>
