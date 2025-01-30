package redisclient

import "github.com/go-redis/redis/v8"

func InitRedis() {
	if redisClient != nil {
		return
	}

	redisClient = redis.NewClient(&redis.Options{
		Addr: "redis:6379",
	})
}
