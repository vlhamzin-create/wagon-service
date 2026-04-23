<script setup lang="ts">
import BaseModal from '@/shared/components/BaseModal.vue'
import { ref } from 'vue'
import { useFilterPresets } from '../composables/useFilterPresets'
import type { FilterPreset } from '../types/filterPreset.types'

const props = defineProps<{
  open: boolean
  preset: FilterPreset | null
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'deleted'): void
}>()

const { deletePreset } = useFilterPresets()
const deleting = ref(false)
const errorMsg = ref<string | null>(null)

async function handleConfirm() {
  if (!props.preset) return
  deleting.value = true
  errorMsg.value = null
  try {
    await deletePreset(props.preset.id)
    emit('deleted')
    emit('close')
  } catch (err: unknown) {
    errorMsg.value = err instanceof Error ? err.message : 'Ошибка удаления'
  } finally {
    deleting.value = false
  }
}
</script>

<template>
  <BaseModal :open="open" title="Удаление пресета" @close="emit('close')">
    <p class="delete-confirm__text">
      Вы уверены, что хотите удалить пресет
      <strong>{{ preset?.name }}</strong>?
    </p>
    <p v-if="errorMsg" class="delete-confirm__error">{{ errorMsg }}</p>

    <template #footer>
      <button
        class="delete-confirm__btn delete-confirm__btn--secondary"
        type="button"
        @click="emit('close')"
      >
        Отмена
      </button>
      <button
        class="delete-confirm__btn delete-confirm__btn--danger"
        type="button"
        :disabled="deleting"
        @click="handleConfirm"
      >
        {{ deleting ? 'Удаление...' : 'Удалить' }}
      </button>
    </template>
  </BaseModal>
</template>

<style scoped>
.delete-confirm__text {
  margin: 0;
  font-size: 14px;
  color: #333;
}

.delete-confirm__error {
  margin: 8px 0 0;
  font-size: 12px;
  color: #d32f2f;
}

.delete-confirm__btn {
  padding: 7px 16px;
  font-size: 13px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  transition: background-color 0.15s;
}

.delete-confirm__btn--secondary {
  background: #f5f5f5;
  color: #555;
}

.delete-confirm__btn--secondary:hover {
  background: #e0e0e0;
}

.delete-confirm__btn--danger {
  background: #d32f2f;
  color: #fff;
}

.delete-confirm__btn--danger:hover:not(:disabled) {
  background: #c62828;
}

.delete-confirm__btn--danger:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
