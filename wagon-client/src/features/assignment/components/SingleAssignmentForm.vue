<script setup lang="ts">
import BaseCombobox from '@/shared/components/BaseCombobox.vue'
import OverwriteWarningBanner from './OverwriteWarningBanner.vue'
import { useAssignmentStore } from '../stores/assignmentStore'
import { useStationSearch } from '../composables/useStationSearch'
import { useClientSearch } from '../composables/useClientSearch'
import { useOverwriteCheck } from '../composables/useOverwriteCheck'
import type { Station, Client } from '../types/assignment.types'

const store = useAssignmentStore()
const stationSearch = useStationSearch()
const clientSearch = useClientSearch()
const { showWarningBanner } = useOverwriteCheck()

defineEmits<{ (e: 'submit'): void }>()

function stationDisplay(s: Station): string {
  return `${s.name} (${s.code})`
}

function clientDisplay(c: Client): string {
  return c.name
}
</script>

<template>
  <div class="single-form">
    <div class="single-form__wagon-info">
      <span class="single-form__wagon-label">Вагон:</span>
      <strong>{{ store.wagons[0]?.wagonNumber }}</strong>
    </div>

    <OverwriteWarningBanner v-if="showWarningBanner" :count="1" />

    <BaseCombobox
      label="Станция назначения"
      placeholder="Код или название станции…"
      :items="stationSearch.suggestions.value"
      :model-value="store.formState.selectedStation"
      :loading="stationSearch.isLoading.value"
      :error="stationSearch.error.value"
      :display-fn="stationDisplay"
      @search="stationSearch.onInput"
      @update:model-value="store.setStation($event as Station | null)"
    >
      <template #option="{ item }">
        <div class="single-form__station-option">
          <span>{{ (item as Station).name }}</span>
          <span class="single-form__station-code">{{ (item as Station).code }}</span>
        </div>
      </template>
    </BaseCombobox>

    <BaseCombobox
      label="Клиент"
      placeholder="Название клиента…"
      :items="clientSearch.suggestions.value"
      :model-value="store.formState.selectedClient"
      :loading="clientSearch.isLoading.value"
      :error="clientSearch.error.value"
      :display-fn="clientDisplay"
      @search="clientSearch.onInput"
      @update:model-value="store.setClient($event as Client | null)"
    />

    <div class="single-form__comment">
      <label class="single-form__label">Комментарий</label>
      <textarea
        v-model="store.formState.comment"
        class="single-form__textarea"
        rows="3"
        placeholder="Необязательный комментарий…"
      />
    </div>

    <div class="single-form__actions">
      <button
        class="single-form__btn single-form__btn--save"
        :disabled="!store.canSave"
        @click="$emit('submit')"
      >
        Сохранить
      </button>
      <button class="single-form__btn" @click="store.close()">
        Отмена
      </button>
    </div>
  </div>
</template>

<style scoped>
.single-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.single-form__wagon-info {
  font-size: 14px;
  color: #333;
}

.single-form__wagon-label {
  color: #666;
  margin-right: 4px;
}

.single-form__station-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.single-form__station-code {
  font-size: 11px;
  color: #999;
  font-family: monospace;
}

.single-form__label {
  font-size: 12px;
  color: #666;
  font-weight: 500;
}

.single-form__comment {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.single-form__textarea {
  border: 1px solid #ccc;
  border-radius: 4px;
  padding: 8px;
  font-size: 13px;
  outline: none;
  resize: vertical;
  font-family: inherit;
}

.single-form__textarea:focus {
  border-color: #4a90e2;
  box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.2);
}

.single-form__actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
  padding-top: 8px;
}

.single-form__btn {
  padding: 6px 16px;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
  border: 1px solid #ccc;
  background: #fff;
  color: #333;
}

.single-form__btn:hover {
  background: #f5f5f5;
}

.single-form__btn--save {
  background: #4a90e2;
  color: #fff;
  border-color: #4a90e2;
}

.single-form__btn--save:hover {
  background: #357abd;
}

.single-form__btn--save:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
