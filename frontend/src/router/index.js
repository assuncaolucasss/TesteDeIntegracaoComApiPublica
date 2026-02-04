import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Operadoras from '../views/Operadoras.vue'
import OperadoraDetalhe from '../views/OperadoraDetalhe.vue'
import Dashboard from '../views/Dashboard.vue'

export default createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', component: Home },
    { path: '/operadoras', component: Operadoras },
    { path: '/operadoras/:cnpj', component: OperadoraDetalhe },
    { path: '/dashboard', component: Dashboard },

    // opcional: redireciona qualquer rota inválida para Home
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
})
