
import React, { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { ChatMessage } from "./ChatMessage";
import { Send } from "lucide-react";

interface MedicalChatBotProps {
  onAISpeaking: (speaking: boolean) => void;
}

export const MedicalChatBot: React.FC<MedicalChatBotProps> = ({
  onAISpeaking,
}) => {
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState<Array<{
    id: string;
    content: string;
    sender: {
      id: string | number;
      name: string;
      isAI?: boolean;
    };
    timestamp: Date;
    status?: "sending" | "sent" | "delivered" | "read" | "error";
  }>>([
    {
      id: "welcome",
      content: "Hello! I'm your AI medical assistant. How can I help you today?",
      sender: { id: "ai", name: "AI Medical Assistant", isAI: true },
      timestamp: new Date(),
      status: "sent",
    },
  ]);

  const chatEndRef = useRef<HTMLDivElement>(null);
  
  // Scroll to bottom of chat when new messages are added
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSendMessage = () => {
    if (!input.trim()) return;
    
    // Add user message
    const userMessageId = `user-${Date.now()}`;
    setMessages((prev) => [
      ...prev,
      {
        id: userMessageId,
        content: input,
        sender: { id: "user", name: "You" },
        timestamp: new Date(),
        status: "sending",
      },
    ]);
    
    setInput("");
    setIsLoading(true);
    
    // Simulate AI response after a delay
    setTimeout(() => {
      // Mark user message as delivered
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === userMessageId ? { ...msg, status: "delivered" } : msg
        )
      );
      
      // AI is "thinking"
      onAISpeaking(true);
      
      // Simulate AI typing delay
      setTimeout(() => {
        // Get a mock response based on the user's message
        const aiResponse = getMockResponse(input);
        
        // Add AI response
        setMessages((prev) => [
          ...prev,
          {
            id: `ai-${Date.now()}`,
            content: aiResponse,
            sender: { id: "ai", name: "AI Medical Assistant", isAI: true },
            timestamp: new Date(),
            status: "sent",
          },
        ]);
        
        setIsLoading(false);
        
        // AI stops "speaking" after a short delay
        setTimeout(() => {
          onAISpeaking(false);
        }, 500);
      }, 1500);
    }, 1000);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Mock AI response generator
  const getMockResponse = (userMessage: string): string => {
    const userMessageLower = userMessage.toLowerCase();
    
    if (userMessageLower.includes("headache") || userMessageLower.includes("head pain")) {
      return "I understand you're experiencing headaches. How long have you been having them? Are they accompanied by any other symptoms like nausea, sensitivity to light, or visual disturbances? Knowing the duration and associated symptoms can help determine the possible causes.";
    } else if (userMessageLower.includes("fever") || userMessageLower.includes("temperature")) {
      return "Fever can be a sign that your body is fighting an infection. What's your temperature reading? Are you experiencing any other symptoms like cough, sore throat, or body aches? Remember to stay hydrated and consider taking acetaminophen if the fever is causing discomfort.";
    } else if (userMessageLower.includes("cough") || userMessageLower.includes("cold") || userMessageLower.includes("flu")) {
      return "Coughs and respiratory symptoms can have various causes. Is your cough dry or productive (producing mucus)? Have you noticed any patterns, like it worsening at night or after certain activities? Rest, staying hydrated, and over-the-counter cough suppressants might help, but if symptoms persist beyond a week, consider consulting your doctor.";
    } else if (userMessageLower.includes("pain") || userMessageLower.includes("hurt")) {
      return "I'm sorry to hear you're in pain. Could you describe the location, intensity, and nature of the pain? Is it sharp, dull, constant, or intermittent? Also, have you tried any remedies so far? This information will help better understand your situation.";
    } else if (userMessageLower.includes("medication") || userMessageLower.includes("medicine") || userMessageLower.includes("drug")) {
      return "When it comes to medications, it's important to take them as prescribed. If you're experiencing side effects or have concerns about your medication, I'd recommend discussing with your healthcare provider before making any changes. They can provide personalized advice based on your medical history.";
    } else if (userMessageLower.includes("diet") || userMessageLower.includes("food") || userMessageLower.includes("eat")) {
      return "Nutrition plays a crucial role in overall health. A balanced diet rich in fruits, vegetables, whole grains, lean proteins, and healthy fats is generally recommended. Are you looking for specific dietary advice for a particular health concern?";
    } else if (userMessageLower.includes("exercise") || userMessageLower.includes("workout") || userMessageLower.includes("active")) {
      return "Regular physical activity is beneficial for both physical and mental health. The general recommendation is at least 150 minutes of moderate-intensity exercise per week. Are you currently following any exercise routine, or do you have specific concerns about starting one?";
    } else if (userMessageLower.includes("sleep") || userMessageLower.includes("insomnia") || userMessageLower.includes("tired")) {
      return "Quality sleep is essential for health. Adults typically need 7-9 hours of sleep per night. If you're having trouble sleeping, consider establishing a regular sleep schedule, creating a relaxing bedtime routine, and ensuring your sleep environment is comfortable. Persistent sleep issues might warrant a discussion with your healthcare provider.";
    } else if (userMessageLower.includes("stress") || userMessageLower.includes("anxiety") || userMessageLower.includes("depression")) {
      return "Mental health is just as important as physical health. If you're experiencing stress, anxiety, or depression, there are various coping strategies including mindfulness, regular exercise, adequate sleep, and seeking support from loved ones. If these feelings are significantly affecting your daily life, consider speaking with a mental health professional.";
    } else if (userMessageLower.includes("thanks") || userMessageLower.includes("thank you")) {
      return "You're welcome! If you have any other health-related questions, feel free to ask. I'm here to provide information and support.";
    } else {
      return "Thank you for sharing that information. To provide better guidance, could you provide more details about your specific symptoms or concerns? Remember, while I can offer general health information, I'm not a substitute for professional medical advice.";
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-hidden mb-4">
        <ScrollArea className="h-full pr-4">
          <div className="space-y-4 pt-2">
            {messages.map((message) => (
              <ChatMessage
                key={message.id}
                id={message.id}
                content={message.content}
                sender={message.sender}
                timestamp={message.timestamp}
                status={message.status}
              />
            ))}
            <div ref={chatEndRef} />
          </div>
        </ScrollArea>
      </div>
      
      <div className="relative mt-auto">
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask the medical AI assistant..."
          className="pr-10 py-6 rounded-xl border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
          disabled={isLoading}
        />
        <Button
          size="icon"
          className="absolute right-2 top-1/2 -translate-y-1/2 h-9 w-9 rounded-full bg-blue-500 hover:bg-blue-600 transition-colors shadow-sm"
          onClick={handleSendMessage}
          disabled={isLoading || !input.trim()}
        >
          <Send className="h-4 w-4 text-white" />
        </Button>
      </div>
      {isLoading && (
        <div className="text-xs text-gray-500 mt-2 mb-1">AI assistant is typing...</div>
      )}
    </div>
  );
};
