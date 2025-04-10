import { useEffect, useRef, useState } from "react";
import socket from "./socket";
import "./styles.css";

function App() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [emotionData, setEmotionData] = useState({
    emotion: "Detecting...",
    confidence: 0,
    sleepy: false,
    nervous: false,
  });

  useEffect(() => {
    // Setup webcam
    navigator.mediaDevices.getUserMedia({ video: true }).then((stream) => {
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.onloadedmetadata = () => {
          videoRef.current.play().catch((err) => {
            console.warn("Video play interrupted:", err);
          });
        };
      }
    });
    

    // Frame sending loop
    const interval = setInterval(() => {
      if (
        !videoRef.current ||
        !canvasRef.current ||
        socket.readyState !== WebSocket.OPEN
      )
        return;
    
      const ctx = canvasRef.current.getContext("2d");
      ctx.drawImage(videoRef.current, 0, 0, 224, 224);
      const dataURL = canvasRef.current.toDataURL("image/jpeg");
      if (socket.readyState === WebSocket.OPEN) {
        socket.send(dataURL);
      }
      
    }, 700);
     // send every 0.7 sec

    // WebSocket listener
    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setEmotionData(data);
    };
    socket.onclose = () => {
      console.warn("WebSocket is closed");
    };
    
    socket.onerror = (error) => {
      console.error("WebSocket error", error);
    };
    

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="container">
      <h1>Real-time Emotion Detector</h1>
      <video ref={videoRef} className="video" width="400" height="300" />
      <canvas ref={canvasRef} width={224} height={224} style={{ display: "none" }} />
      <div className="emotion-box">
        <p>Emotion: <strong>{emotionData.emotion}</strong></p>
        <p>Confidence: {Math.round(emotionData.confidence * 100)}%</p>
        <p>Sleepy: {emotionData.sleepy ? "😴 Yes" : "✅ No"}</p>
        <p>Nervous: {emotionData.nervous ? "😬 Yes" : "✅ No"}</p>
      </div>
    </div>
  );
}

export default App;
