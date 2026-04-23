import { onMounted, onUnmounted, type Ref } from 'vue'

/**
 * Вызывает callback, когда целевой элемент пересекает viewport.
 * Используется для триггера подгрузки при бесконечном скролле.
 */
export function useIntersectionObserver(
  target: Ref<HTMLElement | null>,
  callback: () => void,
  options: IntersectionObserverInit = { threshold: 0.1 },
): void {
  let observer: IntersectionObserver | undefined

  onMounted(() => {
    if (!target.value) return

    observer = new IntersectionObserver((entries) => {
      const entry = entries[0]
      if (entry?.isIntersecting) {
        callback()
      }
    }, options)

    observer.observe(target.value)
  })

  onUnmounted(() => {
    observer?.disconnect()
  })
}
