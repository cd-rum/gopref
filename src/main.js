import Vue from 'vue'
import PrefectApp from './PrefectApp.vue'

process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0'

Vue.config.productionTip = false

new Vue({
  render: h => h(PrefectApp),
}).$mount('#app')
