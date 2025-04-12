import { useState, useEffect, useRef } from 'react';

interface AudioWebSocketProps {
  selectedLanguage: string;
  selectedGender: string;
  onAIResponse: (text: string, audioData?: string) => void;
}

export const useAudioWebSocket = ({ selectedLanguage, selectedGender, onAIResponse }: AudioWebSocketProps) => {
  const [isConnected, setIsConnected] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const webSocketRef = useRef<WebSocket | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const processorRef = useRef<ScriptProcessorNode | null>(null);
  const workletNodeRef = useRef<AudioWorkletNode | null>(null);
  const pcmDataRef = useRef<number[]>([]);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const [initialized, setInitialized] = useState(false);

  const URL = "ws://localhost:9083";

  class Response {
    text: string | null;
    audioData: string | null;
    endOfTurn: boolean | null;
    sessionId?: string | null;

    constructor(data: any) {
      this.text = data.text || null;
      this.audioData = data.audio || null;
      this.endOfTurn = data.endOfTurn || null;
      this.sessionId = data.sessionId || null;
    }
  }

  const initializeAudioContext = async () => {
    if (initialized) return;
    const ctx = new (window.AudioContext || (window as any).webkitAudioContext)({ sampleRate: 24000 });
    await ctx.audioWorklet.addModule("/pcm-processor.js");
    const workletNode = new AudioWorkletNode(ctx, "pcm-processor");
    workletNode.connect(ctx.destination);
    workletNodeRef.current = workletNode;
    setInitialized(true);
  };

  const connect = () => {
    console.log("connecting:", URL);
    const ws = new WebSocket(URL);
    
    ws.onclose = (event) => {
      console.log("websocket closed:", event);
      setIsConnected(false);
    };

    ws.onerror = (event) => {
      console.log("websocket error:", event);
    };

    ws.onopen = (event) => {
      console.log("websocket open:", event);
      setIsConnected(true);
      // Generate a unique session ID if server doesn't provide one
      const generatedSessionId = "session_" + Math.random().toString(36).substring(2, 11);
      setSessionId(generatedSessionId);
    };

    ws.onmessage = (event) => {
      const messageData = JSON.parse(event.data);
      const response = new Response(messageData);
      
      // Update session ID if provided by server
      if (response.sessionId) {
        setSessionId(response.sessionId);
      }
      
      if (response.text) {
        onAIResponse(response.text, response.audioData || undefined);
      }
      if (response.audioData) {
        ingestAudioChunkToPlay(response.audioData);
      }
    };

    webSocketRef.current = ws;
  };

  const sendInitialSetupMessage = () => {
    if (!webSocketRef.current) return;
    
    const setup_client_message = {
      setup: {
        generation_config: { response_modalities: ["AUDIO"] },
      },
      language: selectedLanguage,
      gender: selectedGender,
      sessionId: sessionId // Include session ID in setup
    };
    webSocketRef.current.send(JSON.stringify(setup_client_message));
  };

  const sendVoiceMessage = (b64PCM: string) => {
    if (!webSocketRef.current) return;
    
    const payload = {
      realtime_input: {
        media_chunks: [{
          mime_type: "audio/pcm",
          data: b64PCM,
        }]
      },
    };
    webSocketRef.current.send(JSON.stringify(payload));
  };

  const base64ToArrayBuffer = (base64: string) => {
    const binaryString = window.atob(base64);
    const bytes = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }
    return bytes.buffer;
  };

  const convertPCM16LEToFloat32 = (pcmData: ArrayBuffer) => {
    const inputArray = new Int16Array(pcmData);
    const float32Array = new Float32Array(inputArray.length);
    for (let i = 0; i < inputArray.length; i++) {
      float32Array[i] = inputArray[i] / 32768;
    }
    return float32Array;
  };

  const ingestAudioChunkToPlay = async (base64AudioChunk: string) => {
    try {
      if (!workletNodeRef.current) return;
      
      const arrayBuffer = base64ToArrayBuffer(base64AudioChunk);
      const float32Data = convertPCM16LEToFloat32(arrayBuffer);
      workletNodeRef.current.port.postMessage(float32Data);
    } catch (error) {
      console.error("Error processing audio chunk:", error);
    }
  };

  const recordChunk = () => {
    const buffer = new ArrayBuffer(pcmDataRef.current.length * 2);
    const view = new DataView(buffer);
    pcmDataRef.current.forEach((value, index) => {
      view.setInt16(index * 2, value, true);
    });
    const base64 = btoa(String.fromCharCode.apply(null, new Uint8Array(buffer)));
    sendVoiceMessage(base64);
    pcmDataRef.current = [];
  };

  const startAudioInput = async () => {
    try {
      if (webSocketRef.current?.readyState === WebSocket.OPEN) {
        sendInitialSetupMessage();
        
        audioContextRef.current = new AudioContext({ sampleRate: 16000 });
        const stream = await navigator.mediaDevices.getUserMedia({
          audio: { channelCount: 1, sampleRate: 16000 },
        });
        
        const source = audioContextRef.current.createMediaStreamSource(stream);
        processorRef.current = audioContextRef.current.createScriptProcessor(4096, 1, 1);
        
        processorRef.current.onaudioprocess = (e) => {
          const inputData = e.inputBuffer.getChannelData(0);
          const pcm16 = new Int16Array(inputData.length);
          for (let i = 0; i < inputData.length; i++) {
            pcm16[i] = inputData[i] * 0x7fff;
          }
          pcmDataRef.current.push(...Array.from(pcm16));
        };
        
        source.connect(processorRef.current);
        processorRef.current.connect(audioContextRef.current.destination);
        intervalRef.current = setInterval(recordChunk, 3000);
      }
    } catch (error) {
      console.error("Error starting audio:", error);
    }
  };

  const stopAudioInput = () => {
    if (processorRef.current) {
      processorRef.current.disconnect();
    }
    if (audioContextRef.current) {
      audioContextRef.current.close();
    }
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }
  };

  useEffect(() => {
    initializeAudioContext();
    connect();

    return () => {
      stopAudioInput();
      webSocketRef.current?.close();
    };
  }, []);

  return {
    isConnected,
    startAudioInput,
    stopAudioInput,
    sessionId
  };
}; 