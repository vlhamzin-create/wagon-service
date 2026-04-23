<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { WagonListItem } from '@/types/wagon'

const { t } = useI18n()

defineProps<{ wagon: WagonListItem }>()
const emit = defineEmits<{ (e: 'click', wagon: WagonListItem): void }>()

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
  <tr class="wt-row" @click="emit('click', wagon)">
    <td class="wt-td">{{ wagon.number }}</td>
    <td class="wt-td">{{ wagon.owner_type }}</td>
    <td class="wt-td">{{ wagon.wagon_type }}</td>
    <td class="wt-td">{{ wagon.current_city ?? '—' }}</td>
    <td class="wt-td">{{ wagon.current_station_name ?? '—' }}</td>
    <td class="wt-td">{{ wagon.current_country ?? '—' }}</td>
    <td class="wt-td">
      <span :class="['wt-badge', `wt-badge--${wagon.status}`]">{{ wagon.status }}</span>
    </td>
    <td class="wt-td">
      {{ wagon.requires_assignment ? t('table.yes') : t('table.no') }}
    </td>
    <td class="wt-td">{{ wagon.source }}</td>
    <td class="wt-td wt-td--nowrap">{{ formatDate(wagon.updated_at) }}</td>
  </tr>
</template>

<style scoped>
.wt-row {
  cursor: pointer;
  transition: background 0.15s;
}

.wt-row:hover {
  background: #f0f7ff;
}

.wt-td {
  padding: 8px 12px;
  border-bottom: 1px solid #eeeeee;
  vertical-align: middle;
}

.wt-td--nowrap {
  white-space: nowrap;
}

.wt-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.82em;
  background: #e0e0e0;
}
</style>
