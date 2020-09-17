<template>
  <div id='main'>
    <div uk-grid>
      <div class="uk-width-expand@m">
        <table class="uk-table">
          <thead>
            <tr>
              <th width="220">ID</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody v-for="log in logs" :key="log.ID">
            <tr>
              <td>{{ formatID(log.ID) }}</td>
              <td>{{ formatOutput(log.Output) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
  import axios from 'axios'

  export default {
    name: 'LogList',
    data () {
      return {
        logs: []
      }
    },
    mounted () {
      this.getLogList()
    },
    methods: {
      getLogList () {
        axios.get('/api/logs')
        .then(res => {
          this.logs = res.data
        })
        .catch(err => {
          console.log(err)
        })
      },
      formatID (str) {
        return str.split('/')[2].split('.')[0]
      },
      formatOutput (str) {
        if (str.includes('[pdf]')) return str.split('[pdf]')[1]
        else return str
      }
    }
  }
</script>

<style scoped>
  #main { padding-top: 2em; }
</style>
