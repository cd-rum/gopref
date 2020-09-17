<template>
  <div id='main'>
    <div uk-grid>
      <div class="uk-width-expand@m">

        <pre>pdf routines: {{ stats.PDFRoutines }}</pre>
        <pre>total routines: {{ stats.TotalRoutines }}</pre>
        <pre>allocated: {{ stats.Alloc }}mb / total allocated: {{ stats.TotalAlloc }}mb / system: {{ stats.Sys }}mb</pre>

        <hr />

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
        logs: [],
        stats: {}
      }
    },
    mounted () {
      setInterval(() => {
        this.getLogList()
        this.getStats()
      }, 1000)
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
      getStats () {
        axios.get('/api/stats')
        .then(res => {
          this.stats = res.data
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
        else if (str.includes('(most recent call last):')) return str.split('(most recent call last):')[1]
        else return str
      }
    }
  }
</script>

<style scoped>
  #main { padding-top: 2em; }
</style>
