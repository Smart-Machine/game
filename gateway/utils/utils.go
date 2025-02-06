package utils

import (
	"bytes"
	"encoding/json"
	"io"
	"io/ioutil"
	"log"
	"net/http"
	"strings"
)

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
	var protectedRoute bool
	var exceptionRoute bool

	for _, p := range []string{
		"/session",
		"/user",
	} {
		if strings.HasPrefix(path, p) {
			protectedRoute = true
		}
	}

	for _, e := range []string{
		"/session/docs",
		"/user/docs",
		"/session/openapi.json",
		"/user/openapi.json",
		"/session/status",
		"/user/status",
	} {
		if strings.HasPrefix(path, e) {
			exceptionRoute = true
		}
	}

	return protectedRoute && !exceptionRoute
}

// TODO: Dynamic ports for replicas
func IsValidToken(r *http.Request) bool {
	// Request /validate from users
	url := "http://user-service-1:8004/validate"
	token_raw := strings.Split(r.Header.Get("Authorization"), " ")
	token := ""
	if len(token_raw) > 1 {
		token = token_raw[1]
	}
	postData := JSON{
		"user_token": token,
	}
	jsonData, err := json.Marshal(postData)
	if err != nil {
		log.Println("1")
		log.Println(err)
		return false
	}

	resp, err := http.Post(url, "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		log.Println("2")
		log.Println(err)
		return false
	}
	defer resp.Body.Close()

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		log.Println("3")
		log.Println(err)
		return false
	}

	var response struct {
		Message string `json:"message"`
	}
	err = json.Unmarshal(body, &response)
	if err != nil {
		log.Println("4")
		log.Println(err)
		return false
	}

	if strings.EqualFold(response.Message, "Token is invalid.") {
		return false
	}

	return true
}
