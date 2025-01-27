package main

import (
	"api-gateway/handlers"
	"log"
	"net/http"
)

func main() {
	http.HandleFunc("/version", handlers.HandleVersion)
	http.HandleFunc("/health", handlers.HandleHealth)
	http.HandleFunc("/", handlers.HandleRequest)

	log.Println("API Gateway running on port 8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}
