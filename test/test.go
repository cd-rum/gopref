package test

import (
  "fmt"
  "time"

  vegeta "github.com/tsenart/vegeta/v12/lib"
)

func main() {
  rate := vegeta.Rate{Freq: 100, Per: time.Second}
  duration := 4 * time.Second
  targeter := vegeta.NewStaticTargeter(vegeta.Target{
    Method: "GET",
    URL:    "http://localhost:4200/",
  })
  attacker := vegeta.NewAttacker()

  var metrics vegeta.Metrics
  for res := range attacker.Attack(targeter, rate, duration, "Big Bang!") {
    metrics.Add(res)
  }
  metrics.Close()

  fmt.Printf("99th percentile: %s\n", metrics.Latencies.P99)
}
