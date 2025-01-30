package handlers

import (
	"api-gateway/middleware"
	"api-gateway/redisclient"
	"net/http"
)

func handleVersion(w http.ResponseWriter, r *http.Request) {
	message := "D&D Game Hosting Table v1"

	cacheKey := redisclient.CreateCacheKey(r)
	redisclient.DoCacheResponse(cacheKey, message, redisclient.TTL)

	w.WriteHeader(http.StatusOK)
	w.Write([]byte(message))
}

var HandleVersion http.Handler = middleware.ChainMiddleware(http.HandlerFunc(handleVersion), middleware.CountRequestLoad, middleware.CachingMiddleware, middleware.LoggingMiddleware)
