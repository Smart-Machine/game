package handlers

import (
	"api-gateway/middleware"
	"api-gateway/redisclient"
	"net/http"
)

func handleHealth(w http.ResponseWriter, r *http.Request) {
	message := "healthy"

	cacheKey := redisclient.CreateCacheKey(r)
	redisclient.DoCacheResponse(cacheKey, message, redisclient.TTL)

	w.WriteHeader(http.StatusOK)
	w.Write([]byte(message))
}

var HandleHealth http.Handler = middleware.ChainMiddleware(http.HandlerFunc(handleHealth), middleware.CountRequestLoad, middleware.CachingMiddleware, middleware.LoggingMiddleware)
