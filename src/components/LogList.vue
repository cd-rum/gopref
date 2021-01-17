<template>
  <div id='main'>
    <div uk-grid>
      <div class="uk-width-expand@m">

        <pre>producing {{ formatProduction(stats.Queue) }}</pre>
        <pre v-for='stat in stats.Processes' :key='stat.Pid'>{{ stat.Name }} ({{ stat.PID }}): cpu: {{ formatPercent(stat.CPU) }}% / memory: {{ formatPercent(stat.Memory) }}%</pre>

        <hr />

        <table class="uk-table">
          <thead>
            <tr>
              <th width="120">ID</th>
              <th>Time</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody v-for="log in logs" :key="log.ID">
            <tr>
              <td>{{ formatID(log.ID) }}</td>
              <td>{{ formatDate(log.ModTime) }}</td>
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
  import dayjs from 'dayjs'
  import * as customParseFormat from 'dayjs/plugin/customParseFormat'
  import * as relativeTime from 'dayjs/plugin/relativeTime'
  import 'dayjs/locale/en'

  dayjs.extend(customParseFormat)
  dayjs.extend(relativeTime)
  dayjs.locale('en')

  export default {
    name: 'LogList',
    data () {
      return {
        document: {},
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
          if (res.data) this.logs = res.data.reverse()
          else this.logs = []
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
      formatDate (str) {
        const stamp = dayjs(str)
        return stamp.fromNow()
      },
      formatID (str) {
        return str.split('/')[2].split('.')[0]
      },
      formatOutput (str) {
        return str
      },
      formatProduction (arr) {
        if (arr && arr.length > 0) return arr.join(', ')
        else return `nothing`
      },
      formatPercent (num) {
        return Number((num).toFixed(2))
      }
    }
  }
</script>

<style scoped>
  #main { padding-top: 2em; }
</style>
