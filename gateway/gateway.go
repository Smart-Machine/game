package main

import (
	"api-gateway/handlers"
	"api-gateway/monitor"
	"api-gateway/redisclient"
	"log"
	"net/http"

	"github.com/prometheus/client_golang/prometheus/promhttp"
)

func main() {
	redisclient.InitRedis()
	monitor.InitPrometheus()

	monitor.MonitorServiceLoad("echo-server")
	http.Handle("/metrics", promhttp.Handler())

	http.Handle("/version", handlers.HandleVersion)
	http.Handle("/status", handlers.HandleHealth)
	http.Handle("/", handlers.HandleRequest)

	log.Println("API Gateway running on port 8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}
