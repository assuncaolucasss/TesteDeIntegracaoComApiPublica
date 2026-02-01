import { createRouter, createWebHistory } from 'vue-router'
import Operadoras from '../views/Operadoras.vue'
import OperadoraDetalhe from '../views/OperadoraDetalhe.vue'
import Dashboard from '../views/Dashboard.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: Operadoras },
    { path: '/operadoras/:cnpj', component: OperadoraDetalhe },
    { path: '/dashboard', component: Dashboard },
  ],
})
