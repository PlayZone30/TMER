import React, { forwardRef, useEffect, useRef } from "react";
import { cn } from "@/lib/utils";
import { User } from "lucide-react";

interface Participant {
  id: number;
  name: string;
  avatar?: string;
  role?: string;
  isSpeaking?: boolean;
}

interface VideoFeedProps {
  participant: Participant;
  isVideoOff?: boolean;
  className?: string;
  stream?: MediaStream | null;
}

export const VideoFeed = forwardRef<HTMLVideoElement, VideoFeedProps>(
  ({ participant, isVideoOff = false, className, stream }, ref) => {
    const videoRef = useRef<HTMLVideoElement>(null);

    useEffect(() => {
      if (stream && videoRef.current && !isVideoOff) {
        videoRef.current.srcObject = stream;
      } else if (videoRef.current) {
        videoRef.current.srcObject = null;
      }
    }, [stream, isVideoOff]);

    return (
      <div className={cn(
        "relative w-full h-full bg-gray-100 overflow-hidden rounded-lg",
        className
      )}>
        {isVideoOff ? (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-100">
            <div className="flex flex-col items-center justify-center">
              <div className="w-24 h-24 rounded-full bg-gray-200 flex items-center justify-center mb-2">
                {participant.avatar ? (
                  <img 
                    src={participant.avatar} 
                    alt={participant.name} 
                    className="w-full h-full rounded-full object-cover"
                  />
                ) : (
                  <User className="h-12 w-12 text-gray-400" />
                )}
              </div>
              <p className="text-gray-600 font-medium">{participant.name}</p>
              {participant.role && (
                <p className="text-gray-400 text-sm">{participant.role}</p>
              )}
            </div>
          </div>
        ) : (
          <video
            ref={(el) => {
              videoRef.current = el;
              if (typeof ref === 'function') {
                ref(el);
              } else if (ref) {
                ref.current = el;
              }
            }}
            className="w-full h-full object-cover"
            autoPlay
            playsInline
            muted={participant.id === 1}
          />
        )}
      </div>
    );
  }
);

VideoFeed.displayName = "VideoFeed";
