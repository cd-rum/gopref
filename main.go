package main

import (
  "bufio"
  "encoding/json"
  "fmt"
  "io/ioutil"
  "log"
  "net/http"
  "os"
  "os/exec"
  "regexp"
  "runtime"
  "strings"
  "time"

  "github.com/cheshir/go-mq"
  "github.com/shirou/gopsutil/process"
  "gopkg.in/yaml.v1"
)

// Font is just a string
type Font struct {
  Name           string
}

// LogFile represents an attempt
type LogFile struct {
  ID             string
  ModTime        time.Time
  Output         string
}

// Proc to marshal JSON
type Proc struct {
  PID            int32
  Name           string
  CPU            float64
  Memory         float32
}

// Stats holds all the server info
type Stats struct {
  Processes      []*Proc
  Queue          []string
}

func panic(msg string, err error) {
  if err != nil {
    log.Fatalf("%s: %s", msg, err)
  }
}

var externalConfig = `
dsn: "amqp://guest:guest@10.1.0.100:5672/"
reconnect_delay: 5s
exchanges:
  - name: "gopref_env"
    type: "direct"
    options:
      durable: true
queues:
  - name: "log"
    exchange: "gopref_env"
    routing_key: "key"
    options:
      durable: true
  - name: "pdf"
    exchange: "gopref_env"
    routing_key: "key"
    options:
      durable: true
producers:
  - name: "sync_producer"
    exchange: "gopref_env"
    routing_key: "key"
    sync: true
    options:
      content_type: "text/plain"
      delivery_mode: 2
consumers:
  - name: "cmd_call"
    queue: "pdf"
    workers: 1
`

func writeFontsIndex() {
  cmd := exec.Command("xvfb-run", "-a", "scribus-ng", "-g", "-ns", "-py", "/app/python/fonts.py")

  out, err := cmd.CombinedOutput()
  if err != nil {
    fmt.Println(fmt.Sprint(err) + ": " + string(out))
    return
  }

  data := []byte(out)
  rcomma := regexp.MustCompile(`', '`)
  rstart := regexp.MustCompile(`\['`)
  rend := regexp.MustCompile(`'\]`)
  cd := rcomma.ReplaceAll(data, []byte("\n"))
  sd := rstart.ReplaceAll(cd, []byte(""))
  se := rend.ReplaceAll(sd, []byte(""))

  err = ioutil.WriteFile("tmp/fonts", se, 0)
  panic("Output error", err)

  err = os.Chmod("tmp/fonts", 0666)
  panic("Chmod err", err)
}

func writeLog(path string, output string) {
  _, err := os.OpenFile(path, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
  panic("Write err", err)

  err = ioutil.WriteFile(path, []byte(output), 0)
  panic("Output error", err)
}

func remove(s []string, r string) []string {
  for i, v := range s {
    if v == r {
      return append(s[:i], s[i+1:]...)
    }
  }
  return s
}

func main() {
  log.SetOutput(os.Stdout)
  log.Println("Gopref up bb")

  writeFontsIndex()

  var config mq.Config
  queue := []string{}

  err := yaml.Unmarshal([]byte(externalConfig), &config)
  panic("Failed to read config", err)

  messageQueue, err := mq.New(config)
  panic("Failed to initialize message queue manager", err)
  defer messageQueue.Close()

  go func() {
    for err := range messageQueue.Error() {
      log.Fatal("Caught error from message queue: ", err)
    }
  }()

  err = messageQueue.SetConsumerHandler("cmd_call", func(message mq.Message) {
    s := string(message.Body())
    log.Println(s)

    queue = append(queue, s)
    cmd := exec.Command("xvfb-run", "-a", "scribus-ng", "-ns", "-py", "/app/python/export.py", s)

    out, err := cmd.CombinedOutput()
    if err != nil {
      log.Println(fmt.Sprint(err) + ": " + string(out))
      return
    }

    log.Println("processing")
    log.Println(string(out))
    logfile := fmt.Sprintf("tmp/log/%s.log", s)
    writeLog(logfile, string(out))

    queue = remove(queue, s)
    message.Ack(false)
  })

  panic("Failed to set handler to consumer", err)
  mux := http.NewServeMux()

  // documents
  mux.HandleFunc("/api/documents", func(w http.ResponseWriter, r *http.Request) {
    err := r.ParseForm()
    if err != nil {
      return
    }

    id := r.Form["id"][0]
    producer, err := messageQueue.SyncProducer("sync_producer")
    panic("Failed to get sync producer: ", err)

    err = producer.Produce([]byte(id))
    panic("Failed to send message from sync producer: ", err)

    time.Sleep(time.Second)
    fmt.Fprintln(w, id)
  })

  // logs
  mux.HandleFunc("/api/logs", func(w http.ResponseWriter, r *http.Request) {
    files, err := ioutil.ReadDir("tmp/log")
    panic("Can't read log dir", err)

    var logs []*LogFile
    for _, file := range files {
      filepath := fmt.Sprintf("tmp/log/%s", file.Name())
      file, err := os.Open(filepath)
      panic("No log file", err)

      defer file.Close()

      fileStat, err := os.Stat(filepath)
      panic("No time", err)

      modTime := fileStat.ModTime()
      str, err := ioutil.ReadFile(filepath)
      panic("Can't read log file", err)

      logs = append(logs, &LogFile{ID: file.Name(), ModTime: modTime, Output: string(str)})
    }

    js, err := json.Marshal(logs)
    if err != nil {
      http.Error(w, err.Error(), http.StatusInternalServerError)
      return
    }

    w.Header().Set("Access-Control-Allow-Origin", "*")
    w.Header().Set("Content-Type", "application/json")
    w.Write(js)
  })

  // fonts
  mux.HandleFunc("/api/fonts", func(w http.ResponseWriter, r *http.Request) {
    file, err := os.Open("tmp/fonts")
    panic("No fonts", err)

    defer file.Close()

    var fonts []*Font
    scanner := bufio.NewScanner(file)
    for scanner.Scan() {
      fonts = append(fonts, &Font{Name: scanner.Text()})
    }

    js, err := json.Marshal(fonts)
    if err != nil {
      http.Error(w, err.Error(), http.StatusInternalServerError)
      return
    }

    w.Header().Set("Access-Control-Allow-Origin", "*")
    w.Header().Set("Content-Type", "application/json")
    w.Write(js)
  })

  // stats
  mux.HandleFunc("/api/stats", func(w http.ResponseWriter, r *http.Request) {
    var m runtime.MemStats
    ps := []*Proc{}
    procs, _ := process.Processes()

    for _, p := range procs {
      name, _ := p.Name()

      if strings.Contains(name, "gopref") || strings.Contains(name, "scribus") {
        cpu, _ := p.CPUPercent()    // of system total
        mem, _ := p.MemoryPercent() // of system total
        ps = append(ps, &Proc{PID: p.Pid, Name: name, CPU: cpu, Memory: mem})
      }
    }

    runtime.ReadMemStats(&m)
    stats := Stats{Processes: ps, Queue: queue}

    js, err := json.Marshal(stats)
    if err != nil {
      http.Error(w, err.Error(), http.StatusInternalServerError)
      return
    }

    w.Header().Set("Access-Control-Allow-Origin", "*")
    w.Header().Set("Content-Type", "application/json")
    w.Write(js)
  })
  http.ListenAndServe(":4000", mux)
}



