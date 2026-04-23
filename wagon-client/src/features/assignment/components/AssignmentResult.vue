<script setup lang="ts">
import { computed } from 'vue'
import { useAssignmentStore } from '../stores/assignmentStore'

const store = useAssignmentStore()

const result = computed(() => store.result)
const hasFailed = computed(() => (result.value?.failed ?? 0) > 0)

function statusLabel(status: string): string {
  switch (status) {
    case 'ok': return 'Успешно'
    case 'skipped': return 'Пропущен'
    case 'error': return 'Ошибка'
    default: return status
  }
}

function findWagonNumber(wagonId: string): string {
  return store.wagons.find((w) => w.wagonId === wagonId)?.wagonNumber ?? wagonId
}
</script>

<template>
  <div v-if="result" class="assignment-result">
    <div class="assignment-result__summary">
      <span class="assignment-result__stat assignment-result__stat--ok">
        Успешно: {{ result.succeeded }}
      </span>
      <span v-if="result.skipped > 0" class="assignment-result__stat assignment-result__stat--skip">
        Пропущено: {{ result.skipped }}
      </span>
      <span v-if="result.failed > 0" class="assignment-result__stat assignment-result__stat--err">
        Ошибок: {{ result.failed }}
      </span>
    </div>

    <table class="assignment-result__table">
      <thead>
        <tr>
          <th class="assignment-result__th">Вагон</th>
          <th class="assignment-result__th">Статус</th>
          <th class="assignment-result__th">Причина</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="r in result.results" :key="r.wagon_id" class="assignment-result__row">
          <td class="assignment-result__td">{{ findWagonNumber(r.wagon_id) }}</td>
          <td class="assignment-result__td">
            <span :class="['assignment-result__badge', `assignment-result__badge--${r.status}`]">
              {{ statusLabel(r.status) }}
            </span>
          </td>
          <td class="assignment-result__td">{{ r.reason ?? '—' }}</td>
        </tr>
      </tbody>
    </table>

    <div class="assignment-result__actions">
      <button
        v-if="hasFailed"
        class="assignment-result__btn assignment-result__btn--retry"
        @click="store.retryFailed()"
      >
        Повторить ошибочные
      </button>
      <button class="assignment-result__btn" @click="store.close()">
        Закрыть
      </button>
    </div>
  </div>
</template>

<style scoped>
.assignment-result {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.assignment-result__summary {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.assignment-result__stat {
  font-size: 14px;
  font-weight: 600;
}

.assignment-result__stat--ok {
  color: #38a169;
}

.assignment-result__stat--skip {
  color: #d69e2e;
}

.assignment-result__stat--err {
  color: #e53e3e;
}

.assignment-result__table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.assignment-result__th {
  text-align: left;
  padding: 6px 8px;
  border-bottom: 2px solid #eee;
  color: #666;
  font-weight: 500;
}

.assignment-result__td {
  padding: 6px 8px;
  border-bottom: 1px solid #eee;
  vertical-align: middle;
}

.assignment-result__badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.82em;
}

.assignment-result__badge--ok {
  background: #c6f6d5;
  color: #276749;
}

.assignment-result__badge--skipped {
  background: #fefcbf;
  color: #975a16;
}

.assignment-result__badge--error {
  background: #fed7d7;
  color: #9b2c2c;
}

.assignment-result__actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.assignment-result__btn {
  padding: 6px 16px;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
  border: 1px solid #ccc;
  background: #fff;
  color: #333;
}

.assignment-result__btn:hover {
  background: #f5f5f5;
}

.assignment-result__btn--retry {
  background: #4a90e2;
  color: #fff;
  border-color: #4a90e2;
}

.assignment-result__btn--retry:hover {
  background: #357abd;
}
</style>
