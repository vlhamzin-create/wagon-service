<script setup lang="ts">
import { onMounted } from 'vue'
import { useEtranStatus } from '@/composables/useEtranStatus'
import EtranSyncIndicator from './EtranSyncIndicator.vue'
import EtranStatusFlow from './EtranStatusFlow.vue'
import EtranDocumentCard from './EtranDocumentCard.vue'

const props = defineProps<{
  wagonId: string
}>()

const {
  history,
  isLoading,
  isRefreshing,
  fetchError,
  currentStatus,
  refresh,
  startPolling,
} = useEtranStatus(props.wagonId)

onMounted(() => startPolling())
</script>

<template>
  <div class="etran-tab">
    <!-- Индикатор синхронизации -->
    <EtranSyncIndicator
      :last-updated-at="history?.summary.last_updated_at ?? null"
      :next-poll-at="history?.summary.next_poll_at ?? null"
      :is-refreshing="isRefreshing"
      @refresh="refresh"
    />

    <!-- Ошибка загрузки -->
    <div v-if="fetchError" class="etran-tab__error" role="alert">
      <span class="etran-tab__error-icon">⚠</span>
      {{ fetchError }}
    </div>

    <!-- Загрузка -->
    <div v-if="isLoading && !history" class="etran-tab__loading">
      Загрузка документов ЭТРАН…
    </div>

    <!-- Контент -->
    <template v-if="history">
      <!-- Легенда жизненного цикла -->
      <EtranStatusFlow :current-status="currentStatus" />

      <!-- Список документов -->
      <div v-if="history.documents.length" class="etran-tab__list">
        <h4 class="etran-tab__subtitle">
          Документы ({{ history.summary.documents_count }})
        </h4>
        <div class="etran-tab__cards">
          <EtranDocumentCard
            v-for="doc in history.documents"
            :key="doc.id"
            :document="doc"
          />
        </div>
      </div>
      <div v-else class="etran-tab__empty">
        Документы ЭТРАН по данному вагону отсутствуют.
      </div>
    </template>
  </div>
</template>

<style scoped>
.etran-tab {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.etran-tab__error {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 10px 12px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 4px;
  font-size: 13px;
  color: #b91c1c;
}

.etran-tab__error-icon {
  flex-shrink: 0;
}

.etran-tab__loading {
  text-align: center;
  padding: 32px 0;
  color: #888;
  font-size: 14px;
}

.etran-tab__subtitle {
  margin: 0 0 8px;
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.etran-tab__cards {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.etran-tab__empty {
  text-align: center;
  padding: 24px 0;
  color: #888;
  font-size: 13px;
}
</style>
