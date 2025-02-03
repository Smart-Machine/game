package utils

import (
	"bytes"
	"encoding/json"
	"io"
	"net/http"
	"strings"
)

var ProtectedRoutes = []string{
	"/session",
	"/user",
}

type JSON map[string]interface{}

func ReadCloserToBuffer(rc io.ReadCloser) (*bytes.Buffer, error) {
	defer rc.Close()

	data, err := io.ReadAll(rc)
	if err != nil {
		return nil, err
	}

	return bytes.NewBuffer(data), nil
}

func WriteJSONResponse(w http.ResponseWriter, statusCode int, response interface{}) {
	w.WriteHeader(statusCode)
	err := json.NewEncoder(w).Encode(response)
	if err != nil {
		http.Error(w, "Invalid given json for the response", http.StatusInternalServerError)
	}
}

func IsProtectedRoute(path string) bool {
	for _, p := range ProtectedRoutes {
		if strings.HasPrefix(path, p) {
			return true
		}
	}

	return false
}

func IsValidToken(r *http.Request) bool {
	// Request /validate from users
	return true
}
