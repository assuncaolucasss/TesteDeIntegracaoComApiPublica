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

describe('OperadoraDetalhe.vue (filtro trimestre)', () => {
  it('filtra por trimestre mesmo com "Todos os anos"', async () => {
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

    // Garantia inicial: "Todos os anos" e "Todos os trimestres"
    expect(wrapper.get('#yearFilter').element.value).toBe('0')
    expect(wrapper.get('#triFilter').element.value).toBe('0')

    // Antes: 2 registros
    let rows = wrapper.findAll('tbody tr')
    expect(rows.length).toBe(2)

    // Seleciona T4
    await wrapper.get('#triFilter').setValue('4')
    await flushPromises()

    // Depois: deve sobrar só o registro do T4 (2024/T4)
    rows = wrapper.findAll('tbody tr')
    expect(rows.length).toBe(1)
    expect(rows[0].text()).toContain('2024')
    expect(rows[0].text()).toContain('T4')
  })
})
