package redisclient

import (
	"context"
	"time"

	"github.com/go-redis/redis/v8"
)

var redisClient *redis.Client
var redisContext = context.Background()

const TTL = 60 * time.Second
