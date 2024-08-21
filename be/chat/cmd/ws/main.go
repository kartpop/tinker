package main

import (
	"github.com/gorilla/websocket"
	"log"
	"net/http"
)

var upgrader = websocket.Upgrader{
	CheckOrigin: func(r *http.Request) bool {
		return true
	},
}

func handler(w http.ResponseWriter, r *http.Request) {
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

		err = conn.WriteMessage(messageType, []byte("Hello back from go server! Message received: "+string(p)))
		if err != nil {
			log.Println("Write:", err)
			break
		}
	}
}

func main() {
	http.HandleFunc("/ws", handler)
	log.Println("Server started at :8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}
