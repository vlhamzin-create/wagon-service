<script setup lang="ts">
import { computed } from 'vue'
import BaseModal from '@/shared/components/BaseModal.vue'
import { usePresetForm } from '../composables/usePresetForm'
import { useFilterPresets } from '../composables/useFilterPresets'
import type { FilterPreset } from '../types/filterPreset.types'

const props = defineProps<{
  open: boolean
  editTarget?: FilterPreset
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'saved'): void
}>()

const title = computed(() => (props.editTarget ? 'Редактировать пресет' : 'Сохранить пресет'))

const { form, errors, validate, reset } = usePresetForm(props.editTarget)
const { saveCurrentFiltersAsPreset, updatePreset, saving } = useFilterPresets()

async function handleSubmit() {
  if (!validate()) return

  try {
    if (props.editTarget) {
      await updatePreset(props.editTarget.id, {
        name: form.value.name.trim(),
        description: form.value.description.trim() || undefined,
      })
    } else {
      await saveCurrentFiltersAsPreset(
        form.value.name.trim(),
        form.value.description.trim() || undefined,
      )
    }
    reset()
    emit('saved')
    emit('close')
  } catch (err: unknown) {
    if (err instanceof Error) {
      errors.value = { name: err.message }
    }
  }
}

function handleClose() {
  reset()
  emit('close')
}
</script>

<template>
  <BaseModal :open="open" :title="title" @close="handleClose">
    <form class="preset-form" @submit.prevent="handleSubmit">
      <div class="preset-form__field">
        <label class="preset-form__label" for="preset-name">Название</label>
        <input
          id="preset-name"
          v-model="form.name"
          class="preset-form__input"
          :class="{ 'preset-form__input--error': errors.name }"
          type="text"
          maxlength="255"
          placeholder="Например: Мои вагоны на ЖД Запад"
        />
        <span v-if="errors.name" class="preset-form__error">{{ errors.name }}</span>
      </div>
      <div class="preset-form__field">
        <label class="preset-form__label" for="preset-desc">Описание (необязательно)</label>
        <textarea
          id="preset-desc"
          v-model="form.description"
          class="preset-form__textarea"
          maxlength="512"
          rows="2"
          placeholder="Краткое описание набора фильтров"
        />
      </div>
      <span v-if="errors.filters" class="preset-form__error">{{ errors.filters }}</span>
    </form>

    <template #footer>
      <button class="preset-form__btn preset-form__btn--secondary" type="button" @click="handleClose">
        Отмена
      </button>
      <button
        class="preset-form__btn preset-form__btn--primary"
        type="button"
        :disabled="saving"
        @click="handleSubmit"
      >
        {{ saving ? 'Сохранение...' : 'Сохранить' }}
      </button>
    </template>
  </BaseModal>
</template>

<style scoped>
.preset-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.preset-form__field {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.preset-form__label {
  font-size: 13px;
  font-weight: 500;
  color: #555;
}

.preset-form__input,
.preset-form__textarea {
  padding: 8px 10px;
  font-size: 13px;
  border: 1px solid #ddd;
  border-radius: 6px;
  outline: none;
  transition: border-color 0.15s;
}

.preset-form__input:focus,
.preset-form__textarea:focus {
  border-color: #1976d2;
}

.preset-form__input--error {
  border-color: #d32f2f;
}

.preset-form__textarea {
  resize: vertical;
}

.preset-form__error {
  font-size: 12px;
  color: #d32f2f;
}

.preset-form__btn {
  padding: 7px 16px;
  font-size: 13px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  transition: background-color 0.15s;
}

.preset-form__btn--primary {
  background: #1976d2;
  color: #fff;
}

.preset-form__btn--primary:hover:not(:disabled) {
  background: #1565c0;
}

.preset-form__btn--primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.preset-form__btn--secondary {
  background: #f5f5f5;
  color: #555;
}

.preset-form__btn--secondary:hover {
  background: #e0e0e0;
}
</style>
