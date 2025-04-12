import React, { useEffect, useState, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { User, MicIcon, MicOffIcon, VideoIcon, VideoOffIcon, PhoneOffIcon, MessageSquare, ClipboardList, X, ChevronRight, ChevronLeft, PlusCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Card } from "@/components/ui/card";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useToast } from "@/hooks/use-toast";
import { cn } from "@/lib/utils";
import { AnimatePresence, motion } from "framer-motion";
import { VideoFeed } from "@/components/VideoFeed";
import { ChatMessage } from "@/components/ChatMessage";
import { ParticipantThumbnail } from "@/components/ParticipantThumbnail";
import { MedicalChatBot } from "@/components/MedicalChatBot";
import { useIsMobile } from "@/hooks/use-mobile";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useAudioWebSocket } from "@/hooks/use-audio-websocket";
import { useSessionRecording } from '@/hooks/use-session-recording';
import { uploadSessionData } from '@/utils/api';

// Mock participants data
const MOCK_PARTICIPANTS = [
  { id: 1, name: "You", role: "System Owner", avatar: "/user.jpg", isSpeaking: false },
  { id: 2, name: "AI Assistant", role: "Medical AI", avatar: "/ai.jpg", isSpeaking: false },
];

// Siri-inspired microphone button states
// 0: mic off, 1: user speaking, 2: AI speaking
const getMicButtonStyles = (status: number) => {
  if (status === 0) {
    return "bg-gray-200 border-gray-300 text-gray-600 hover:bg-gray-300";
  } else {
    return "bg-blue-500 text-white border-transparent";
  }
};

interface LanguageOption {
  value: 'english' | 'hindi';
  label: string;
}

interface GenderOption {
  value: 'male' | 'female';
  label: string;
}

const LANGUAGE_OPTIONS: LanguageOption[] = [
  { value: 'english', label: 'English' },
  { value: 'hindi', label: 'Hindi' },
];

const GENDER_OPTIONS: GenderOption[] = [
  { value: 'male', label: 'Male' },
  { value: 'female', label: 'Female' },
];

const Room = () => {
  const { roomId } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const isMobile = useIsMobile();
  
  const [isSidebarOpen, setIsSidebarOpen] = useState(!isMobile);
  const [isMuted, setIsMuted] = useState(true);
  const [isVideoOff, setIsVideoOff] = useState(true);
  const [isParticipantsOpen, setIsParticipantsOpen] = useState(false);
  const [participants, setParticipants] = useState(MOCK_PARTICIPANTS);
  const [isAISpeaking, setIsAISpeaking] = useState(false);
  const [isUserSpeaking, setIsUserSpeaking] = useState(false);
  const [selectedParticipant, setSelectedParticipant] = useState(MOCK_PARTICIPANTS[0]);
  const [joinedRoom, setJoinedRoom] = useState(false);
  const [hasAudioPermission, setHasAudioPermission] = useState<boolean>(false);
  const [hasCameraPermission, setHasCameraPermission] = useState<boolean>(false);
  const [localStream, setLocalStream] = useState<MediaStream | null>(null);
  const [selectedLanguage, setSelectedLanguage] = useState<string>('');
  const [selectedGender, setSelectedGender] = useState<string>('');
  const [isPreJoinScreen, setIsPreJoinScreen] = useState(true);
  const [currentUserInput, setCurrentUserInput] = useState<string>("");
  
  const {
    isRecording,
    startRecording,
    stopRecording,
    addConversationEntry,
    conversationData,
    addAIAudioToRecording,
  } = useSessionRecording();
  
  const { isConnected, startAudioInput, stopAudioInput, sessionId } = useAudioWebSocket({
    selectedLanguage,
    selectedGender,
    onAIResponse: (text, audioData) => {
      if (!text) return;
      
      // Add the conversation entry with the current user input and AI response
      addConversationEntry(currentUserInput, text);
      setCurrentUserInput(""); // Reset for next interaction

      // Add AI audio to the recording if available
      if (audioData) {
        addAIAudioToRecording(audioData);
      }
    }
  });
  
  // Determine the mic button state (0: off, 1: user speaking, 2: AI speaking)
  const getMicState = () => {
    if (isMuted) return 0;
    if (isAISpeaking) return 2;
    if (isUserSpeaking) return 1;
    return 0;
  };
  
  const micState = getMicState();
  
  // Reference for main video element
  const mainVideoRef = useRef<HTMLVideoElement>(null);
  
  // Simulate joining room
  useEffect(() => {
    if (!isPreJoinScreen && !joinedRoom) {
      const timer = setTimeout(() => {
        setJoinedRoom(true);
        toast({
          title: "Room joined successfully",
          description: `You've joined room ${roomId} (${selectedLanguage}, ${selectedGender})`,
        });
      }, 1000);
      
      return () => clearTimeout(timer);
    }
  }, [isPreJoinScreen, roomId, selectedLanguage, selectedGender, toast]);
  
  //Handle room exit
  const handleEndCall = async () => {
    if (isRecording) {
      try {
        const recordingData = await stopRecording();
        
        // Upload session data - without audioBlob but with sessionId
        await uploadSessionData(
          recordingData.videoBlob,
          recordingData.conversationData,
          sessionId
        );

        toast({
          title: "Session Saved",
          description: "Your conversation has been successfully recorded and saved.",
        });
      } catch (error) {
        console.error('Error saving session:', error);
        toast({
          title: "Error",
          description: "Failed to save session data",
          variant: "destructive",
        });
      }
    }

    navigate("/");
  };
  
  // Toggle microphone
  const toggleMute = async () => {
    if (isMuted) {
      try {
        await startAudioInput();
        setIsMuted(false);
        setIsUserSpeaking(true);
        
        // Start recording user's input
        const timestamp = new Date().toISOString();
        setCurrentUserInput(`User input at ${timestamp}`); // This will be updated with actual transcription if available
        
        toast({
          title: "Microphone activated",
          description: "Connected to AI Assistant",
        });
      } catch (err) {
        console.error("Microphone error:", err);
        setIsMuted(true);
        toast({
          title: "Error",
          description: "Failed to activate microphone",
          variant: "destructive",
        });
      }
    } else {
      stopAudioInput();
      setIsMuted(true);
      setIsUserSpeaking(false);
      
      toast({
        title: "Microphone muted",
        description: "Disconnected from AI Assistant",
      });
    }
  };
  
  // Toggle video
  const toggleVideo = async () => {
    if (isVideoOff) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ 
          video: { 
            width: { ideal: 1280 },
            height: { ideal: 720 }
          } 
        });
        setLocalStream(prevStream => {
          if (prevStream) {
            const videoTrack = stream.getVideoTracks()[0];
            prevStream.addTrack(videoTrack);
            return prevStream;
          }
          return stream;
        });
        setHasCameraPermission(true);
        setIsVideoOff(false);
        
        toast({
          title: "Camera activated",
          description: "Others can see you now",
        });
      } catch (err) {
        console.error("Camera permission denied:", err);
        setHasCameraPermission(false);
        setIsVideoOff(true);
        toast({
          title: "Permission Denied",
          description: "Please allow camera access to use this feature",
          variant: "destructive",
        });
      }
    } else {
      if (localStream) {
        localStream.getVideoTracks().forEach(track => {
          track.stop();
          track.enabled = false;
        });
      }
      setIsVideoOff(true);
      toast({
        title: "Camera turned off",
        description: "Others can't see you now",
      });
    }
  };
  
  // Clean up the media streams when component unmounts
  useEffect(() => {
    return () => {
      if (localStream) {
        localStream.getTracks().forEach(track => track.stop());
      }
    };
  }, [localStream]);
  
  const handleJoinRoom = async () => {
    if (!selectedLanguage || !selectedGender) {
      toast({
        title: "Selection Required",
        description: "Please select both language and gender to continue",
        variant: "destructive",
      });
      return;
    }

    try {
      // Get user media stream for recording with better video configuration
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: true,
        video: !isVideoOff ? { 
          width: { ideal: 1280 }, 
          height: { ideal: 720 } 
        } : false,
      });
      
      // Store the stream for VideoFeed component
      setLocalStream(stream);
      
      // Set permission flags
      setHasAudioPermission(true);
      if (!isVideoOff) {
        setHasCameraPermission(true);
      }

      // Start recording the session
      await startRecording(stream, selectedLanguage, selectedGender);
      setIsPreJoinScreen(false);
    } catch (error) {
      console.error('Error starting session:', error);
      toast({
        title: "Error",
        description: "Failed to start recording session",
        variant: "destructive",
      });
    }
  };

  const handleEndSession = async () => {
    try {
      const recordingData = await stopRecording();
      
      // Upload the session data - without audioBlob but with sessionId
      await uploadSessionData(
        recordingData.videoBlob,
        recordingData.conversationData,
        sessionId
      );

      toast({
        title: "Session Saved",
        description: "Your session has been successfully recorded and saved.",
      });

      // Navigate away or show end screen
      handleEndCall();
    } catch (error) {
      console.error('Error ending session:', error);
      toast({
        title: "Error",
        description: "Failed to save session data",
        variant: "destructive",
      });
    }
  };
  
  return (
    <div className="h-screen w-full flex flex-col bg-gray-50 overflow-hidden">
      <AnimatePresence mode="wait">
        {isPreJoinScreen ? (
          <motion.div
            key="prejoin"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="flex items-center justify-center h-full w-full"
          >
            <Card className="w-full max-w-3xl p-6">
              <h2 className="text-2xl font-semibold text-center mb-6">Medical Consultation Room</h2>
              
              <div className="flex items-center gap-4 justify-center">
                {/* Language Selection */}
                <div className="flex-1 max-w-[200px]">
                  <Select
                    value={selectedLanguage}
                    onValueChange={setSelectedLanguage}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select Language" />
                    </SelectTrigger>
                    <SelectContent>
                      {LANGUAGE_OPTIONS.map((option) => (
                        <SelectItem key={option.value} value={option.value}>
                          {option.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Gender Selection */}
                <div className="flex-1 max-w-[200px]">
                  <Select
                    value={selectedGender}
                    onValueChange={setSelectedGender}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select Gender" />
                    </SelectTrigger>
                    <SelectContent>
                      {GENDER_OPTIONS.map((option) => (
                        <SelectItem key={option.value} value={option.value}>
                          {option.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Create Room Button */}
                <Button
                  className="flex-1 max-w-[200px]"
                  onClick={handleJoinRoom}
                  disabled={!selectedLanguage || !selectedGender}
                >
                  Create Room
                </Button>
              </div>

              {/* Error message if selections are missing */}
              {(!selectedLanguage || !selectedGender) && (
                <p className="text-sm text-muted-foreground text-center mt-4">
                  Please select both language and gender to create the room
                </p>
              )}
            </Card>
          </motion.div>
        ) : !joinedRoom ? (
          <motion.div 
            key="loading"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="flex items-center justify-center h-full w-full"
          >
            <div className="text-center">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-gray-200 border-t-gray-800 mb-4"></div>
              <p className="text-gray-600">Joining secure medical room...</p>
            </div>
          </motion.div>
        ) : (
          <motion.div 
            key="room"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex flex-1 overflow-hidden"
          >
            {/* Main content area */}
            <div className="flex-1 flex flex-col h-full relative">
              {/* Main video feed */}
              <motion.div 
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.2 }}
                className="flex-1 relative"
              >
                <VideoFeed
                  ref={mainVideoRef}
                  participant={selectedParticipant}
                  isVideoOff={isVideoOff && selectedParticipant.id === 0}
                  className="h-full w-full"
                  stream={localStream}
                />
                
                {/* Participant name overlay */}
                <div className="absolute left-4 bottom-4 bg-black/30 backdrop-blur-md rounded-lg px-3 py-1 text-white text-sm">
                  {selectedParticipant.name}
                </div>
              </motion.div>
              
              {/* Controls bar */}
              <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
                className="h-20 bg-white border-t border-gray-200 flex items-center justify-between px-4 md:px-8"
              >
                {/* Room info */}
                <div className="hidden md:flex items-center space-x-2">
                  <span className="bg-green-100 text-green-800 text-xs font-medium px-2.5 py-0.5 rounded-full">LIVE</span>
                  <span className="text-gray-500 text-sm">Room: {roomId}</span>
                </div>
                
                {/* Call controls */}
                <div className="flex items-center space-x-3">
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Button
                          variant="outline"
                          size="icon"
                          className={cn(
                            "rounded-full w-12 h-12 border transition-all duration-200",
                            getMicButtonStyles(isMuted ? 0 : 1)
                          )}
                          onClick={toggleMute}
                        >
                          {isMuted ? (
                            <MicOffIcon className="h-5 w-5" />
                          ) : (
                            <MicIcon className="h-5 w-5" />
                          )}
                        </Button>
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>{isMuted ? "Unmute microphone" : "Mute microphone"}</p>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                  
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Button
                          variant="outline"
                          size="icon"
                          className={cn(
                            "rounded-full w-12 h-12 border transition-all duration-200",
                            isVideoOff ? "bg-red-50 border-red-200 text-red-500" : "bg-gray-50 hover:bg-gray-100"
                          )}
                          onClick={toggleVideo}
                        >
                          {isVideoOff ? <VideoOffIcon className="h-5 w-5" /> : <VideoIcon className="h-5 w-5" />}
                        </Button>
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>{isVideoOff ? "Turn on camera" : "Turn off camera"}</p>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                  
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Button
                          variant="destructive"
                          size="icon"
                          className="rounded-full w-12 h-12 bg-red-600 hover:bg-red-700"
                          onClick={handleEndCall}
                        >
                          <PhoneOffIcon className="h-5 w-5" />
                        </Button>
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>End call</p>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                </div>
                
                {/* Right side controls/info */}
                <div className="flex items-center">
                  {/* Sidebar toggle on mobile */}
                  {isMobile && (
                    <Button
                      variant="ghost"
                      onClick={() => setIsSidebarOpen(!isSidebarOpen)}
                      className="rounded-full p-2"
                    >
                      {isSidebarOpen ? <ChevronRight className="h-6 w-6" /> : <ChevronLeft className="h-6 w-6" />}
                    </Button>
                  )}
                  
                  {/* Participants toggle */}
                  <div className="ml-2 flex items-center space-x-1">
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-gray-600"
                      onClick={() => setIsParticipantsOpen(!isParticipantsOpen)}
                    >
                      <User className="h-4 w-4 mr-1" />
                      <span>{participants.length}</span>
                    </Button>
                  </div>
                </div>
              </motion.div>
              
              {/* Participant thumbnails */}
              <AnimatePresence>
                {isParticipantsOpen && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "100px" }}
                    exit={{ opacity: 0, height: 0 }}
                    className="bg-gray-900/10 backdrop-blur-md w-full overflow-x-auto"
                  >
                    <div className="flex items-center h-full py-3 px-4 space-x-3">
                      {participants.map((participant) => (
                        <ParticipantThumbnail
                          key={participant.id}
                          participant={participant}
                          isSelected={selectedParticipant.id === participant.id}
                          onClick={() => setSelectedParticipant(participant)}
                        />
                      ))}
                      <Button variant="ghost" className="h-16 w-16 rounded-lg border border-dashed border-gray-300 flex-shrink-0">
                        <PlusCircle className="h-5 w-5 text-gray-400" />
                      </Button>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
            
            {/* Sidebar */}
            <AnimatePresence>
              {isSidebarOpen && (
                <motion.div
                  initial={{ opacity: 0, x: 300 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 300 }}
                  transition={{ duration: 0.3 }}
                  className={cn(
                    "bg-white border-l border-gray-200 h-full",
                    isMobile ? "fixed right-0 top-0 z-50 w-full max-w-[320px]" : "w-96"
                  )}
                >
                  {isMobile && (
                    <div className="flex justify-end p-2">
                      <Button variant="ghost" size="icon" onClick={() => setIsSidebarOpen(false)}>
                        <X className="h-5 w-5" />
                      </Button>
                    </div>
                  )}
                  
                  <Tabs defaultValue="chat" className="h-full flex flex-col">
                    <TabsList className="justify-start mx-2 mb-0">
                      <TabsTrigger value="chat" className="flex items-center gap-1">
                        <MessageSquare className="h-4 w-4" />
                        <span>Medical Chat</span>
                      </TabsTrigger>
                      <TabsTrigger value="notes" className="flex items-center gap-1">
                        <ClipboardList className="h-4 w-4" />
                        <span>Session Summary</span>
                      </TabsTrigger>
                    </TabsList>
                    
                    <TabsContent value="chat" className="flex-1 px-4 pb-6 flex flex-col overflow-hidden">
                      <MedicalChatBot onAISpeaking={setIsAISpeaking} />
                    </TabsContent>
                    
                    <TabsContent value="notes" className="flex-1 p-4 pb-6 overflow-auto">
                      <div className="space-y-4">
                        <Card className="p-4 border border-gray-200 rounded-xl">
                          <h3 className="text-sm font-semibold mb-2">Session Summary</h3>
                          <div className="space-y-4">
                            <div className="text-sm text-gray-600">
                              <p className="mb-2">
                                Session started at: {new Date().toLocaleTimeString()}
                              </p>
                              <div className="space-y-2">
                                <h4 className="font-medium">Key Discussion Points:</h4>
                                <ul className="list-disc pl-4 space-y-1">
                                  <li>Initial consultation and symptom assessment</li>
                                  <li>Discussion of medical history</li>
                                  <li>Treatment options and recommendations</li>
                                </ul>
                              </div>
                              <div className="mt-4">
                                <h4 className="font-medium mb-2">AI Assistant Recommendations:</h4>
                                <p className="italic">
                                  "Based on our discussion, I recommend focusing on preventive measures 
                                  and lifestyle modifications. We should schedule a follow-up to monitor progress."
                                </p>
                              </div>
                            </div>
                          </div>
                        </Card>
                      </div>
                    </TabsContent>
                  </Tabs>
                </motion.div>
              )}
            </AnimatePresence>
            
            {/* Sidebar toggle button (for desktop) */}
            {!isMobile && (
              <div className={cn("absolute top-1/2 -translate-y-1/2 transition-all duration-300", 
                isSidebarOpen ? "right-96" : "right-0"
              )}>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8 rounded-l-full rounded-r-none bg-white border border-r-0 border-gray-200"
                  onClick={() => setIsSidebarOpen(!isSidebarOpen)}
                >
                  {isSidebarOpen ? (
                    <ChevronRight className="h-4 w-4" />
                  ) : (
                    <ChevronLeft className="h-4 w-4" />
                  )}
                </Button>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default Room;
