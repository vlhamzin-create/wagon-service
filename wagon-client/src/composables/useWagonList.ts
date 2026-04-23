import { computed } from 'vue'
import { useInfiniteQuery } from '@tanstack/vue-query'
import { fetchWagons, PAGE_SIZE } from '@/api/wagons'
import type { WagonFilters } from '@/types/wagon'
import type { PaginatedWagons } from '@/types/api'

/**
 * Бесконечный скролл поверх GET /wagons.
 * Каждая «страница» = 100 записей (PAGE_SIZE).
 */
export function useWagonList(filters: () => WagonFilters) {
  const queryKey = computed(() => ['wagons', filters()] as const)

  const query = useInfiniteQuery({
    queryKey,
    queryFn: ({ pageParam }) =>
      fetchWagons(filters(), pageParam as number),
    initialPageParam: 0,
    getNextPageParam: (lastPage: PaginatedWagons): number | undefined => {
      if (!lastPage.has_more) return undefined
      return lastPage.offset + PAGE_SIZE
    },
    staleTime: 60_000,
  })

  const allItems = computed(() =>
    query.data.value?.pages.flatMap((p) => p.items) ?? [],
  )

  const total = computed(() => query.data.value?.pages[0]?.total ?? 0)

  return {
    ...query,
    allItems,
    total,
  }
}
