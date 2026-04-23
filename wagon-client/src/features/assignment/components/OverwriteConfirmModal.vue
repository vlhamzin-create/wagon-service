<script setup lang="ts">
import BaseModal from '@/shared/components/BaseModal.vue'

defineProps<{ open: boolean; count: number }>()
const emit = defineEmits<{
  (e: 'confirm'): void
  (e: 'cancel'): void
}>()
</script>

<template>
  <BaseModal :open="open" title="Подтверждение перезаписи" @close="emit('cancel')">
    <p class="overwrite-modal__text">
      У <strong>{{ count }}</strong> вагонов уже заполнены данные назначения.
      Продолжить и перезаписать существующие значения?
    </p>

    <template #footer>
      <button class="overwrite-modal__btn overwrite-modal__btn--cancel" @click="emit('cancel')">
        Отмена
      </button>
      <button class="overwrite-modal__btn overwrite-modal__btn--confirm" @click="emit('confirm')">
        Перезаписать
      </button>
    </template>
  </BaseModal>
</template>

<style scoped>
.overwrite-modal__text {
  margin: 0;
  font-size: 14px;
  color: #333;
  line-height: 1.5;
}

.overwrite-modal__btn {
  padding: 6px 16px;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
  border: 1px solid #ccc;
  background: #fff;
  color: #333;
}

.overwrite-modal__btn:hover {
  background: #f5f5f5;
}

.overwrite-modal__btn--confirm {
  background: #e53e3e;
  color: #fff;
  border-color: #e53e3e;
}

.overwrite-modal__btn--confirm:hover {
  background: #c53030;
}

.overwrite-modal__btn--cancel {
  background: #fff;
}
</style>
