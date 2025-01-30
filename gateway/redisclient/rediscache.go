package redisclient

import (
	"fmt"
	"log"
	"net/http"
	"time"

	"github.com/go-redis/redis/v8"
)

// Creates the cache key
func CreateCacheKey(r *http.Request) string {
	// Create a cache key based on the URL path
	cacheKey := fmt.Sprintf("cache:%s", r.URL.Path)
	if r.URL.RawQuery != "" {
		cacheKey = fmt.Sprintf("cache:%s?%s", r.URL.Path, r.URL.RawQuery)
	}

	return cacheKey
}

// Cache responses in Redis with a given expiration
func DoCacheResponse(key string, value string, expiration time.Duration) {
	err := redisClient.Set(redisContext, key, value, expiration).Err()
	if err != nil {
		log.Printf("Failed to cache response: %v\n", err)
	}
}

// Get cached response from Redis
func GetCacheResponse(key string) (string, bool) {
	val, err := redisClient.Get(redisContext, key).Result()
	if err == redis.Nil {
		return "", false // Cache miss
	} else if err != nil {
		log.Printf("Failed to get cache: %v\n", err)
		return "", false
	}
	return val, true // Cache hit
}
