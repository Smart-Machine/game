package handlers

import "net/http"

func HandleVersion(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("D&D Game Hosting Table v1"))
}
