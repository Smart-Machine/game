package handlers

import (
	"net/http"
	"time"
)

var (
	httpClient = &http.Client{
		Timeout: 10 * time.Second, // Adding timeout to requests
	}
)
