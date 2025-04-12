
import React from "react";
import { cn } from "@/lib/utils";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { motion } from "framer-motion";

export interface ChatMessageProps {
  id: string | number;
  content: string;
  sender: {
    id: string | number;
    name: string;
    avatar?: string;
    isAI?: boolean;
  };
  timestamp: Date;
  status?: "sending" | "sent" | "delivered" | "read" | "error";
}

export const ChatMessage: React.FC<ChatMessageProps> = ({
  content,
  sender,
  timestamp,
  status = "sent",
}) => {
  const isAI = sender.isAI;
  const formattedTime = new Intl.DateTimeFormat("en-US", {
    hour: "numeric",
    minute: "numeric",
  }).format(timestamp);
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn(
        "flex items-start gap-3 group mb-4",
        isAI ? "justify-start" : "justify-end"
      )}
    >
      {isAI && (
        <Avatar className="h-8 w-8 mt-1">
          <AvatarImage src="/ai-avatar.png" alt="AI Assistant" />
          <AvatarFallback className="bg-gradient-to-br from-blue-400 to-cyan-300 text-white text-xs">
            AI
          </AvatarFallback>
        </Avatar>
      )}
      
      <div className={cn("max-w-[75%] flex flex-col", isAI ? "items-start" : "items-end")}>
        <div className="flex items-center gap-2 mb-1">
          <span className="text-xs text-gray-500">{isAI ? "AI Medical Assistant" : "You"}</span>
          <span className="text-xs text-gray-400">{formattedTime}</span>
        </div>
        
        <div
          className={cn(
            "px-4 py-2.5 rounded-2xl text-sm",
            isAI ? "bg-gray-100 text-gray-800 rounded-tl-none" : "bg-blue-500 text-white rounded-tr-none"
          )}
        >
          {content}
        </div>
        
        {!isAI && status === "error" && (
          <span className="text-xs text-red-500 mt-1">Failed to send. Tap to retry.</span>
        )}
      </div>
      
      {!isAI && (
        <Avatar className="h-8 w-8 mt-1">
          <AvatarImage src="/user-avatar.png" alt="User" />
          <AvatarFallback className="bg-blue-500 text-white text-xs">You</AvatarFallback>
        </Avatar>
      )}
    </motion.div>
  );
};
