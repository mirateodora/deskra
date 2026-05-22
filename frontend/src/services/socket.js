import { io } from "socket.io-client";

const socket = io("http://localhost:5000", {
  transports: ["websocket", "polling"],
});

socket.on("connect", () => {
  console.log("Connected to Flask-SocketIO:", socket.id);
});

socket.on("disconnect", () => {
  console.log("Disconnected from Flask-SocketIO");
});

socket.on("test_event", (data) => {
  console.log("Received test_event:", data);
});

export default socket;
