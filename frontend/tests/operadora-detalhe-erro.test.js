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

describe('OperadoraDetalhe.vue (erro)', () => {
  it('mostra mensagem de erro quando a API falha', async () => {
    apiGet.mockRejectedValueOnce(new Error('Falha ao buscar dados'))

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

    expect(wrapper.text()).toContain('Erro ao carregar detalhes')
    expect(wrapper.text()).toContain('Falha ao buscar dados')
  })
})
