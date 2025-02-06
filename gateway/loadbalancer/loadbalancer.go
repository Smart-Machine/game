package loadbalancer

import "sync/atomic"

var index uint64

func GetNextService(services []string) string {
	nextIndex := atomic.AddUint64(&index, 1)
	return services[nextIndex%uint64(len(services))]
}
