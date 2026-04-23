import { describe, it, expect } from 'vitest'
import { buildParams } from '@/api/wagons'
import type { WagonFilters } from '@/types/wagon'

function makeFilters(overrides: Partial<WagonFilters> = {}): WagonFilters {
  return {
    mode: 'all',
    sort_by: 'destination_railway',
    sort_dir: 'desc',
    ...overrides,
  }
}

describe('buildParams', () => {
  it('возвращает базовые параметры при пустых фильтрах', () => {
    const params = buildParams(makeFilters(), 0)
    expect(params.get('limit')).toBe('100')
    expect(params.get('offset')).toBe('0')
    expect(params.get('mode')).toBe('all')
    expect(params.get('sort_by')).toBe('destination_railway')
    expect(params.get('sort_dir')).toBe('desc')
  })

  it('сериализует массив destination_railway как repeated params', () => {
    const params = buildParams(makeFilters({ destination_railway: ['РЖД', 'ФГК'] }), 0)
    expect(params.getAll('destination_railway')).toEqual(['РЖД', 'ФГК'])
  })

  it('сериализует client_name с ключом filter[client_name]', () => {
    const params = buildParams(makeFilters({ client_name: ['ТрансНефть', 'ЛукОйл'] }), 0)
    expect(params.getAll('filter[client_name]')).toEqual(['ТрансНефть', 'ЛукОйл'])
    // Не должно быть plain-ключа client_name
    expect(params.getAll('client_name')).toEqual([])
  })

  it('не включает фильтры с undefined значениями', () => {
    const params = buildParams(makeFilters({ destination_railway: undefined }), 0)
    expect(params.has('destination_railway')).toBe(false)
  })

  it('сериализует supplier_name как repeated params', () => {
    const params = buildParams(makeFilters({ supplier_name: ['ПоставщикА'] }), 0)
    expect(params.getAll('supplier_name')).toEqual(['ПоставщикА'])
  })

  it('передаёт search как одиночный параметр', () => {
    const params = buildParams(makeFilters({ search: 'вагон' }), 0)
    expect(params.get('search')).toBe('вагон')
  })

  it('рассчитывает offset корректно', () => {
    const params = buildParams(makeFilters(), 200)
    expect(params.get('offset')).toBe('200')
  })
})
