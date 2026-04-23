<script setup lang="ts">
import { ETRAN_STATUS_CONFIG, ETRAN_STATUS_LIFECYCLE } from '@/constants/etranStatusConfig'
import type { EtranDocStatus } from '@/types/etran'

defineProps<{
  currentStatus: EtranDocStatus | null
}>()

const steps = ETRAN_STATUS_LIFECYCLE.map((key) => ({
  key,
  ...ETRAN_STATUS_CONFIG[key],
}))

const errorConfig = ETRAN_STATUS_CONFIG.error
</script>

<template>
  <div class="etran-flow">
    <div class="etran-flow__steps">
      <template v-for="(step, i) in steps" :key="step.key">
        <div
          class="etran-flow__step"
          :class="{ 'etran-flow__step--active': currentStatus === step.key }"
        >
          <span
            class="etran-flow__dot"
            :style="{ background: currentStatus === step.key ? step.dotColor : '#d1d5db' }"
          />
          <span class="etran-flow__label">{{ step.label }}</span>
          <span class="etran-flow__desc">{{ step.description }}</span>
        </div>
        <span v-if="i < steps.length - 1" class="etran-flow__arrow">→</span>
      </template>
    </div>
    <div
      class="etran-flow__error"
      :class="{ 'etran-flow__step--active': currentStatus === 'error' }"
    >
      <span
        class="etran-flow__dot"
        :style="{ background: currentStatus === 'error' ? errorConfig.dotColor : '#d1d5db' }"
      />
      <span class="etran-flow__label">{{ errorConfig.label }}</span>
      <span class="etran-flow__desc">{{ errorConfig.description }}</span>
    </div>
  </div>
</template>

<style scoped>
.etran-flow {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.etran-flow__steps {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.etran-flow__step,
.etran-flow__error {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  flex: 1;
  text-align: center;
  opacity: 0.5;
}

.etran-flow__step--active {
  opacity: 1;
}

.etran-flow__dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.etran-flow__label {
  font-size: 13px;
  font-weight: 600;
  color: #333;
}

.etran-flow__desc {
  font-size: 11px;
  color: #888;
  line-height: 1.3;
}

.etran-flow__arrow {
  color: #bbb;
  font-size: 16px;
  margin-top: 2px;
  flex-shrink: 0;
}
</style>
