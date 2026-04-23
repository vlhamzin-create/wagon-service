<template>
  <DashboardLayout>
    <template #filter>
      <WagonTypeFilter :wagon-types="summaryByWagonType" />
    </template>

    <template #content>
      <ApiErrorBlock v-if="errorMessage" :message="errorMessage" />

      <template v-else>
        <StatusMetrics :rows="destinationRailways" :is-loading="isLoading" />
        <WagonTypeSummaryTable :rows="summaryByWagonType" />
      </template>
    </template>

    <template #footer>
      <UpdateTimestamp :calculated-at="calculatedAt" />
    </template>
  </DashboardLayout>
</template>

<script setup lang="ts">
import { useDashboard } from '@/composables/useDashboard'
import DashboardLayout from '@/components/dashboard/DashboardLayout.vue'
import WagonTypeFilter from '@/components/dashboard/WagonTypeFilter.vue'
import StatusMetrics from '@/components/dashboard/StatusMetrics.vue'
import WagonTypeSummaryTable from '@/components/dashboard/WagonTypeSummaryTable.vue'
import UpdateTimestamp from '@/components/dashboard/UpdateTimestamp.vue'
import ApiErrorBlock from '@/components/dashboard/ApiErrorBlock.vue'

const {
  isLoading,
  errorMessage,
  calculatedAt,
  destinationRailways,
  summaryByWagonType,
} = useDashboard()
</script>
