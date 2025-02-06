package handlers

import (
	"net/http"
	"time"
)

var (
	httpClient = &http.Client{
		Timeout: 10 * time.Second, // Adding timeout to requests
	}
	sessionServices = []string{
		"http://session-service-1:8001",
		"http://session-service-2:8002",
		"http://session-service-3:8003",
	}
	userServices = []string{
		"http://user-service-1:8004",
		"http://user-service-2:8005",
		"http://user-service-3:8006",
	}
)
