package main

import (
	"bytes"
	"encoding/json"
	"io"
	"log"
	"net/http"

	"github.com/gorilla/websocket"
)

var upgrader = websocket.Upgrader{
	CheckOrigin: func(r *http.Request) bool {
		return true
	},
}

func websocketHandler(w http.ResponseWriter, r *http.Request) {
	conn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Println("Upgrade:", err)
		return
	}
	defer conn.Close()

	for {
		messageType, p, err := conn.ReadMessage()
		if err != nil {
			log.Println("Read:", err)
			break
		}
		log.Printf("Message received: %s", p)

		response := askLlm(string(p))

		err = conn.WriteMessage(messageType, []byte(response))
		if err != nil {
			log.Println("Write:", err)
			break
		}
	}
}

type RequestData struct {
	Question string `json:"question"`
}

type ResponseData struct {
	Response string `json:"response"`
}

func askLlm(question string) string {
	url := "http://localhost:8000/ask"

	requestData := RequestData{
		Question: question,
	}

	requestBody, err := json.Marshal(requestData)
	if err != nil {
		log.Fatalf("Error encoding request data: %v", err)
	}

	resp, err := http.Post(url, "application/json", bytes.NewBuffer(requestBody))
	if err != nil {
		log.Fatalf("Error making POST request: %v", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		log.Fatalf("Error reading response body: %v", err)
	}

	var responseData ResponseData
	err = json.Unmarshal(body, &responseData)
	if err != nil {
		log.Fatalf("Error decoding response data: %v", err)
	}

	return responseData.Response
}

func main() {
	http.HandleFunc("/ws", websocketHandler)
	log.Println("Server started at :8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}
