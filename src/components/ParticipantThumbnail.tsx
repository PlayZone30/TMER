
import React from "react";
import { cn } from "@/lib/utils";
import { User, MicOff } from "lucide-react";

interface Participant {
  id: number;
  name: string;
  avatar?: string;
  role?: string;
  isSpeaking?: boolean;
  isMuted?: boolean;
}

interface ParticipantThumbnailProps {
  participant: Participant;
  isSelected?: boolean;
  onClick?: () => void;
}

export const ParticipantThumbnail: React.FC<ParticipantThumbnailProps> = ({
  participant,
  isSelected = false,
  onClick,
}) => {
  return (
    <div 
      className={cn(
        "relative w-16 h-16 rounded-lg overflow-hidden cursor-pointer flex-shrink-0 transition-all duration-200",
        isSelected ? "ring-2 ring-blue-500 ring-offset-1" : "hover:ring-1 hover:ring-gray-300",
      )}
      onClick={onClick}
    >
      {/* Video thumbnail (would be a real video in production) */}
      <div className="absolute inset-0 bg-gray-200">
        {participant.avatar ? (
          <img 
            src={participant.avatar} 
            alt={participant.name}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <User className="h-8 w-8 text-gray-400" />
          </div>
        )}
      </div>
      
      {/* Speaking indicator */}
      {participant.isSpeaking && (
        <div className="absolute inset-0 border-2 border-green-500 rounded-lg animate-pulse"></div>
      )}
      
      {/* Muted indicator */}
      {participant.isMuted && (
        <div className="absolute bottom-0.5 right-0.5 bg-gray-800/70 rounded-full p-0.5">
          <MicOff className="h-3 w-3 text-white" />
        </div>
      )}
      
      {/* Name label */}
      <div className="absolute bottom-0 left-0 right-0 bg-black/40 backdrop-blur-sm p-0.5 text-white text-[10px] truncate text-center">
        {participant.name.split(' ')[0]}
      </div>
    </div>
  );
};
