import { useRef, useState } from 'react';

interface RecordingData {
  videoBlob: Blob | null;
  conversationData: ConversationData;
}

interface ConversationEntry {
  userInput: string;
  systemResponse: string;
  timestamp: string;
}

interface ConversationData {
  questions: ConversationEntry[];
  metadata: {
    startTime: string;
    endTime: string;
    language: string;
    gender: string;
    videoPath?: string;
  };
}

export const useSessionRecording = () => {
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const destinationNodeRef = useRef<MediaStreamAudioDestinationNode | null>(null);
  const videoChunksRef = useRef<Blob[]>([]);
  const [isRecording, setIsRecording] = useState(false);
  const [conversationData, setConversationData] = useState<ConversationData>({
    questions: [],
    metadata: {
      startTime: '',
      endTime: '',
      language: '',
      gender: '',
    },
  });

  const startRecording = async (stream: MediaStream, language: string, gender: string) => {
    try {
      // Create audio context and destination node for mixing audio
      audioContextRef.current = new AudioContext({ sampleRate: 16000 });
      destinationNodeRef.current = audioContextRef.current.createMediaStreamDestination();

      // Connect user's audio to the destination node if available
      const userAudioTrack = stream.getAudioTracks()[0];
      if (userAudioTrack) {
        const userAudioSource = audioContextRef.current.createMediaStreamSource(stream);
        userAudioSource.connect(destinationNodeRef.current);
      }

      // Create a new MediaStream with just the video track
      // The audio is handled by the server via WebSocket
      const videoTrack = stream.getVideoTracks()[0];
      const videoOnlyStream = videoTrack ? new MediaStream([videoTrack]) : null;
      
      if (videoOnlyStream) {
        // Create MediaRecorder with video-only stream
        const mediaRecorder = new MediaRecorder(videoOnlyStream, {
          mimeType: 'video/webm;codecs=vp8'
        });

        // Handle data available event
        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            videoChunksRef.current.push(event.data);
          }
        };

        // Start recording with 1-second chunks
        mediaRecorder.start(1000);
        mediaRecorderRef.current = mediaRecorder;
      }

      // Initialize conversation data
      setConversationData({
        questions: [],
        metadata: {
          startTime: new Date().toISOString(),
          endTime: '',
          language,
          gender,
        },
      });

      setIsRecording(true);
    } catch (error) {
      console.error('Error starting recording:', error);
      throw error;
    }
  };

  const addAIAudioToRecording = async (base64Audio: string) => {
    if (!audioContextRef.current || !destinationNodeRef.current) return;

    try {
      // Convert base64 to ArrayBuffer
      const binaryString = window.atob(base64Audio);
      const bytes = new Uint8Array(binaryString.length);
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }

      // Create audio buffer from the AI response and play it
      // The actual recording of this audio is handled by the server
      const audioBuffer = await audioContextRef.current.decodeAudioData(bytes.buffer);
      const source = audioContextRef.current.createBufferSource();
      source.buffer = audioBuffer;
      source.connect(audioContextRef.current.destination);
      source.start();
    } catch (error) {
      console.error('Error processing AI audio:', error);
    }
  };

  const addConversationEntry = (userInput: string, systemResponse: string) => {
    setConversationData(prev => ({
      ...prev,
      questions: [
        ...prev.questions,
        {
          userInput,
          systemResponse,
          timestamp: new Date().toISOString()
        }
      ]
    }));
  };

  const stopRecording = async (): Promise<RecordingData> => {
    return new Promise((resolve) => {
      if (!mediaRecorderRef.current) {
        resolve({
          videoBlob: null,
          conversationData,
        });
        return;
      }

      mediaRecorderRef.current.onstop = () => {
        // Create final video blob
        const videoBlob = videoChunksRef.current.length > 0 
          ? new Blob(videoChunksRef.current, { type: 'video/webm;codecs=vp8' }) 
          : null;

        // Clean up audio context
        if (audioContextRef.current) {
          audioContextRef.current.close();
        }

        // Update conversation data with end time
        const updatedConversationData = {
          ...conversationData,
          metadata: {
            ...conversationData.metadata,
            endTime: new Date().toISOString(),
          },
        };

        setConversationData(updatedConversationData);
        setIsRecording(false);

        resolve({
          videoBlob,
          conversationData: updatedConversationData,
        });
      };

      mediaRecorderRef.current.stop();
    });
  };

  return {
    isRecording,
    startRecording,
    stopRecording,
    addConversationEntry,
    addAIAudioToRecording,
    conversationData,
  };
}; 