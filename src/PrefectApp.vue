<template>
  <LogList />
</template>

<script>
  import UIkit from 'uikit'
  import Icons from 'uikit/dist/js/uikit-icons'
  import LogList from './components/LogList.vue'

  import "../node_modules/uikit/dist/css/uikit.min.css"

  UIkit.use(Icons)

  export default {
    name: 'PrefectApp',
    components: {
      LogList
    }
  }
</script>
