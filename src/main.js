import Vue from 'vue'
import PrefectApp from './PrefectApp.vue'

Vue.config.productionTip = false

new Vue({
  render: h => h(PrefectApp),
}).$mount('#app')
