<script setup lang="ts">
import { watch } from 'vue'

interface Props {
  open: boolean
  title: string
}

const props = defineProps<Props>()
const emit = defineEmits<{ (e: 'close'): void }>()

function onKeydown(event: KeyboardEvent): void {
  if (event.key === 'Escape') emit('close')
}

watch(
  () => props.open,
  (val) => {
    if (val) {
      document.addEventListener('keydown', onKeydown)
    } else {
      document.removeEventListener('keydown', onKeydown)
    }
  },
)
</script>

<template>
  <teleport to="body">
    <transition name="side-panel">
      <div v-if="open" class="side-panel__overlay" @click.self="emit('close')">
        <aside class="side-panel" role="dialog" :aria-label="title">
          <header class="side-panel__header">
            <h2 class="side-panel__title">{{ title }}</h2>
            <button
              class="side-panel__close"
              type="button"
              aria-label="Закрыть"
              @click="emit('close')"
            >
              ✕
            </button>
          </header>
          <div class="side-panel__body">
            <slot />
          </div>
        </aside>
      </div>
    </transition>
  </teleport>
</template>

<style scoped>
.side-panel__overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  justify-content: flex-end;
}

.side-panel {
  width: 480px;
  max-width: 100vw;
  height: 100%;
  background: #fff;
  box-shadow: -4px 0 24px rgba(0, 0, 0, 0.12);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.side-panel__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid #eee;
}

.side-panel__title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.side-panel__close {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
  color: #999;
  padding: 4px;
  line-height: 1;
}

.side-panel__close:hover {
  color: #333;
}

.side-panel__body {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

/* Анимация slide-in */
.side-panel-enter-active,
.side-panel-leave-active {
  transition: opacity 0.25s ease;
}

.side-panel-enter-active .side-panel,
.side-panel-leave-active .side-panel {
  transition: transform 0.25s ease;
}

.side-panel-enter-from {
  opacity: 0;
}

.side-panel-enter-from .side-panel {
  transform: translateX(100%);
}

.side-panel-leave-to {
  opacity: 0;
}

.side-panel-leave-to .side-panel {
  transform: translateX(100%);
}
</style>
