package middleware

import (
	"api-gateway/monitor"
	"api-gateway/redisclient"
	"api-gateway/utils"
	"fmt"
	"log"
	"net/http"
	"sync/atomic"
)

type Middleware func(http.Handler) http.Handler

func LoggingMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		fmt.Printf("Proxy: %s %s\n", r.Method, r.URL.Path)

		next.ServeHTTP(w, r)
	})
}

// Only checks cache hit, otherwise is always cached at the request level
func CachingMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		cacheKey := redisclient.CreateCacheKey(r)
		cachedResponse, isCached := redisclient.GetCacheResponse(cacheKey)
		if isCached {
			log.Printf("Cache hit for %s\n", r.URL.Path)
			w.WriteHeader(http.StatusOK)
			w.Write([]byte(cachedResponse))
			return
		}

		next.ServeHTTP(w, r)
	})
}

func CountRequestLoad(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		atomic.AddInt64(&monitor.RequestCount, 1)
		monitor.PrometheusRequestCount.WithLabelValues(r.URL.Path, r.Method).Inc()

		next.ServeHTTP(w, r)
	})
}

func ValidateJWTToken(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if utils.IsProtectedRoute(r.URL.Path) && utils.IsValidToken(r) {
			utils.WriteJSONResponse(w, http.StatusBadRequest, utils.JSON{"error": "The provided token was invalid."})
			return
		}

		next.ServeHTTP(w, r)
	})
}

func ChainMiddleware(handler http.Handler, middlewares ...Middleware) http.Handler {
	for _, m := range middlewares {
		handler = m(handler)
	}
	return handler
}
