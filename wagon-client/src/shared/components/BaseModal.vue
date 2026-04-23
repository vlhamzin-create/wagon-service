<script setup lang="ts">
defineProps<{ open: boolean; title: string }>()
const emit = defineEmits<{ (e: 'close'): void }>()
</script>

<template>
  <teleport to="body">
    <transition name="modal">
      <div v-if="open" class="base-modal__overlay" @click.self="emit('close')">
        <div class="base-modal" role="dialog" :aria-label="title">
          <header class="base-modal__header">
            <h3 class="base-modal__title">{{ title }}</h3>
            <button
              class="base-modal__close"
              type="button"
              aria-label="Закрыть"
              @click="emit('close')"
            >
              ✕
            </button>
          </header>
          <div class="base-modal__body">
            <slot />
          </div>
          <footer class="base-modal__footer">
            <slot name="footer" />
          </footer>
        </div>
      </div>
    </transition>
  </teleport>
</template>

<style scoped>
.base-modal__overlay {
  position: fixed;
  inset: 0;
  z-index: 1100;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
}

.base-modal {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.16);
  min-width: 360px;
  max-width: 520px;
  width: 100%;
}

.base-modal__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid #eee;
}

.base-modal__title {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: #333;
}

.base-modal__close {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 14px;
  color: #999;
  padding: 4px;
  line-height: 1;
}

.base-modal__close:hover {
  color: #333;
}

.base-modal__body {
  padding: 20px;
}

.base-modal__footer {
  padding: 12px 20px;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
</style>
