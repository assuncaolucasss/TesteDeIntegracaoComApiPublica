import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import OperadoraDetalhe from '../src/views/OperadoraDetalhe.vue'

vi.mock('../src/api.js', () => ({
  apiGet: vi.fn(),
}))

import { apiGet } from '../src/api.js'

beforeEach(() => {
  vi.clearAllMocks()
})

function makeRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [{ path: '/operadoras/:cnpj', component: OperadoraDetalhe }],
  })
}

describe('OperadoraDetalhe.vue (filtro)', () => {
  it('filtra despesas por ano ao alterar o select', async () => {
    apiGet.mockImplementation(async (url) => {
      if (url === '/api/operadoras/123') {
        return { cnpj: '123', razao_social: 'Operadora X', uf: 'PA', modalidade: 'Y' }
      }
      if (url === '/api/operadoras/123/despesas') {
        return [
          { ano: 2024, trimestre: 4, valor_despesas: 40 },
          { ano: 2023, trimestre: 1, valor_despesas: 10 },
        ]
      }
      throw new Error('URL inesperada: ' + url)
    })

    const router = makeRouter()
    await router.push('/operadoras/123')
    await router.isReady()

    const wrapper = mount(OperadoraDetalhe, {
      global: {
        plugins: [router],
        stubs: { DespesasBarChart: true },
      },
    })

    await flushPromises()

    // Antes do filtro: a tabela deve ter 2 linhas (2024 e 2023)
    let rows = wrapper.findAll('tbody tr')
    expect(rows.length).toBe(2)

    // Aplica filtro do ano
    await wrapper.get('#yearFilter').setValue('2024')
    await flushPromises()

    // Confirma que o select realmente mudou (sanity check)
    expect(wrapper.get('#yearFilter').element.value).toBe('2024')

    // Depois do filtro: 1 linha e ela é do ano 2024
    rows = wrapper.findAll('tbody tr')
    expect(rows.length).toBe(1)
    expect(rows[0].text()).toContain('2024')

    // E opcionalmente: garante que a linha não é do ano antigo
    expect(rows[0].text()).not.toContain('2023')
  })
})
