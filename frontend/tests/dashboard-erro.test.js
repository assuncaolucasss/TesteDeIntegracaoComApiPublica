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

describe('Dashboard.vue (erro)', () => {
  it('mostra mensagem de erro quando a API falha', async () => {
    apiGet.mockRejectedValueOnce(new Error('Falha total'))

    const wrapper = mount(Dashboard, {
      global: { stubs: { UFsBarChart: true } },
    })

    await flushPromises()

    expect(wrapper.text()).toContain('Erro ao carregar o dashboard')
    expect(wrapper.text()).toContain('Falha total')
  })
})
