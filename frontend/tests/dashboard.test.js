import { describe, it, expect, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import Dashboard from '../src/views/Dashboard.vue'

vi.mock('../src/api.js', () => ({
  apiGet: vi.fn(),
}))

import { apiGet } from '../src/api.js'

describe('Dashboard.vue', () => {
  it('renderiza dados após carregar', async () => {
    apiGet.mockImplementation(async (url) => {
      if (url === '/api/estatisticas') {
        return {
          total_despesas: 100,
          media_despesas: 10,
          top5_operadoras: [
            { cnpj: '1', razao_social: 'Operadora A', uf: 'PA', modalidade: 'X', total_despesas: 50 },
          ],
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
    expect(wrapper.text()).toContain('Operadora A')
  })
})
