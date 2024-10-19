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
		jsonResponse, err := json.Marshal(response)
		if err != nil {
			log.Fatalf("Error encoding response data: %v", err)
		}

		err = conn.WriteMessage(messageType, jsonResponse)
		if err != nil {
			log.Println("Write:", err)
			break
		}
	}
}

type RequestData struct {
	Question string `json:"question"`
}

type Reference struct {
    Title string `json:"title"`
    H2    string `json:"h2,omitempty"`
    H3    string `json:"h3,omitempty"`
    H4    string `json:"h4,omitempty"`
}

type Answer struct {
    Text       string      `json:"text"`
    References []Reference `json:"references"`
}

type ResponseData struct {
    Question string `json:"question"`
    Answer   Answer `json:"answer"`
}

func askLlm(question string) ResponseData {
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

	return responseData
}

func main() {
	http.HandleFunc("/ws", websocketHandler)
	log.Println("Server started at :8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}
