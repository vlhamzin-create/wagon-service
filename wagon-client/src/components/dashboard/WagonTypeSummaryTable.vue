<template>
  <section class="wts-table">
    <h2 class="wts-table__title">Сводка по типам вагонов</h2>
    <div class="wts-table__wrap">
      <table class="wts-table__table">
        <thead>
          <tr>
            <th class="wts-th">Тип вагона</th>
            <th class="wts-th wts-th--num">Под погрузкой</th>
            <th class="wts-th wts-th--num">Едут под погрузку</th>
            <th class="wts-th wts-th--num">Под выгрузкой</th>
            <th class="wts-th wts-th--num">Едут под выгрузку</th>
            <th class="wts-th wts-th--num">Без назначения</th>
            <th class="wts-th wts-th--num">Без назначения в пути</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in rows" :key="row.wagon_type" class="wts-row">
            <td class="wts-td">{{ row.wagon_type }}</td>
            <td class="wts-td wts-td--num">{{ row.under_loading.toLocaleString('ru-RU') }}</td>
            <td class="wts-td wts-td--num">{{ row.going_to_loading.toLocaleString('ru-RU') }}</td>
            <td class="wts-td wts-td--num">{{ row.under_unloading.toLocaleString('ru-RU') }}</td>
            <td class="wts-td wts-td--num">{{ row.going_to_unloading.toLocaleString('ru-RU') }}</td>
            <td class="wts-td wts-td--num">{{ row.without_assignment.toLocaleString('ru-RU') }}</td>
            <td class="wts-td wts-td--num">{{ row.without_assignment_in_transit.toLocaleString('ru-RU') }}</td>
          </tr>
          <tr v-if="rows.length === 0">
            <td class="wts-td wts-td--empty" colspan="7">Нет данных</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<script setup lang="ts">
import type { WagonTypeSummaryRow } from '@/api/dashboard'

defineProps<{
  rows: WagonTypeSummaryRow[]
}>()
</script>

<style scoped>
.wts-table__title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0 0 12px;
}

.wts-table__wrap {
  overflow-x: auto;
}

.wts-table__table {
  width: 100%;
  border-collapse: collapse;
}

.wts-th {
  padding: 8px 12px;
  text-align: left;
  font-size: 13px;
  font-weight: 600;
  color: #666;
  border-bottom: 2px solid #e0e0e0;
  white-space: nowrap;
}

.wts-th--num {
  text-align: right;
}

.wts-row:hover {
  background: #f0f7ff;
}

.wts-td {
  padding: 8px 12px;
  font-size: 14px;
  color: #333;
  border-bottom: 1px solid #eee;
}

.wts-td--num {
  text-align: right;
  font-variant-numeric: tabular-nums;
}

.wts-td--empty {
  text-align: center;
  color: #999;
  padding: 24px;
}
</style>
