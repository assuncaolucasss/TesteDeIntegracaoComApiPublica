import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import Dashboard from '../src/views/Dashboard.vue'

vi.mock('../src/api.js', () => ({
  apiGet: vi.fn(),
}))

import { apiGet } from '../src/api.js'

beforeEach(() => {
  vi.clearAllMocks()
})

describe('Dashboard.vue (vazio)', () => {
  it('mostra estados vazios quando não há dados', async () => {
    apiGet.mockImplementation(async (url) => {
      if (url === '/api/estatisticas') {
        return {
          total_despesas: 0,
          media_despesas: 0,
          top5_operadoras: [],
        }
      }
      if (url === '/api/estatisticas/uf') return []
      throw new Error('URL inesperada: ' + url)
    })

    const wrapper = mount(Dashboard, {
      global: { stubs: { UFsBarChart: true } },
    })

    await flushPromises()

    
    expect(wrapper.text()).toContain('Ranking de operadoras')
    expect(wrapper.text()).toContain('Sem dados para exibir.')

  })
})
