<script setup lang="ts">
import type { EtranDocStatus } from '@/types/etran'
import { ETRAN_STATUS_CONFIG } from '@/constants/etranStatusConfig'

const props = defineProps<{
  status: EtranDocStatus
}>()

const config = ETRAN_STATUS_CONFIG[props.status]
</script>

<template>
  <span
    class="etran-badge"
    :style="{
      background: config.bgColor,
      color: config.textColor,
      borderColor: config.borderColor,
    }"
  >
    <span
      class="etran-badge__dot"
      :class="{ 'etran-badge__dot--pulse': config.animateDot }"
      :style="{ background: config.dotColor }"
    />
    {{ config.label }}
  </span>
</template>

<style scoped>
.etran-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 2px 10px;
  border: 1px solid;
  border-radius: 12px;
  font-size: 0.82em;
  font-weight: 500;
  white-space: nowrap;
}

.etran-badge__dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}

.etran-badge__dot--pulse {
  animation: etran-pulse 1.5s ease-in-out infinite;
}

@keyframes etran-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}
</style>
