<script setup lang="ts">
import type { EtranDocument } from '@/types/etran'
import EtranStatusBadge from './EtranStatusBadge.vue'

defineProps<{
  document: EtranDocument
}>()

function formatDate(iso: string): string {
  return new Date(iso).toLocaleString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}
</script>

<template>
  <div class="etran-doc">
    <div class="etran-doc__header">
      <div class="etran-doc__title">
        <span class="etran-doc__number">{{ document.doc_number }}</span>
        <span class="etran-doc__type">{{ document.doc_type }}</span>
      </div>
      <EtranStatusBadge :status="document.status" />
    </div>
    <div class="etran-doc__body">
      <div class="etran-doc__row">
        <span class="etran-doc__label">Операция</span>
        <span class="etran-doc__value">{{ document.operation_type }}</span>
      </div>
      <div class="etran-doc__row">
        <span class="etran-doc__label">Отправлено</span>
        <span class="etran-doc__value">{{ formatDate(document.sent_at) }}</span>
      </div>
      <div class="etran-doc__row">
        <span class="etran-doc__label">Обновлено</span>
        <span class="etran-doc__value">{{ formatDate(document.updated_at) }}</span>
      </div>
    </div>
    <div v-if="document.comment" class="etran-doc__error">
      {{ document.comment }}
    </div>
  </div>
</template>

<style scoped>
.etran-doc {
  border: 1px solid #eee;
  border-radius: 6px;
  padding: 12px 16px;
  background: #fff;
}

.etran-doc__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 8px;
}

.etran-doc__title {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.etran-doc__number {
  font-weight: 600;
  font-size: 14px;
  color: #333;
}

.etran-doc__type {
  font-size: 12px;
  color: #888;
}

.etran-doc__body {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.etran-doc__row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.etran-doc__label {
  color: #888;
  min-width: 90px;
  flex-shrink: 0;
}

.etran-doc__value {
  color: #333;
}

.etran-doc__error {
  margin-top: 8px;
  padding: 8px 10px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 4px;
  font-size: 12px;
  color: #b91c1c;
  line-height: 1.4;
}
</style>
