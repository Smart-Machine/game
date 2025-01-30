package handlers

import (
	"api-gateway/middleware"
	"api-gateway/redisclient"
	"api-gateway/utils"
	"io"
	"net/http"
)

// func getServiceName(path string) string {
// 	if strings.HasPrefix(path, "/session/") {
// 		return "session-service"
// 	} else {
// 		return "user-service"
// 	}
// }

func proxyRequest(r *http.Request, url string) (*http.Response, error) {
	// Switching to a bytes.Buffer got rid of the `chunked` transfer encoding
	// which was removing the `Content-Length` header
	reqBody, err := utils.ReadCloserToBuffer(r.Body)
	if err != nil {
		return nil, err
	}

	newreq, err := http.NewRequest(r.Method, url, reqBody)
	newreq.Header = r.Header.Clone() // haven't found a another way

	if err != nil {
		return nil, err
	}
	return httpClient.Do(newreq)
}

func proxyResponse(w http.ResponseWriter, resp *http.Response, cacheKey string) error {
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return err
	}

	redisclient.DoCacheResponse(cacheKey, string(body), redisclient.TTL)

	w.WriteHeader(resp.StatusCode)
	w.Write(body)

	return nil
}

func handleRequest(w http.ResponseWriter, r *http.Request) {
	// serviceName := getServiceName(r.URL.Path)
	cacheKey := redisclient.CreateCacheKey(r)

	resp, err := proxyRequest(r, "http://echo-server:6969/")
	if err != nil {
		utils.WriteJSONResponse(w, http.StatusNotFound, utils.JSON{
			"error": err,
		})
		return
	}
	defer resp.Body.Close()

	err = proxyResponse(w, resp, cacheKey)
	if err != nil {
		utils.WriteJSONResponse(w, http.StatusInternalServerError, utils.JSON{
			"error": err,
		})
	}
}

var HandleRequest http.Handler = middleware.ChainMiddleware(http.HandlerFunc(handleRequest), middleware.CountRequestLoad, middleware.CachingMiddleware, middleware.LoggingMiddleware)
