
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";

const Index = () => {
  const navigate = useNavigate();
  const [isHovered, setIsHovered] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleCreateRoom = () => {
    setIsLoading(true);
    // Generate a random room ID
    const roomId = Math.random().toString(36).substring(2, 11);
    
    // Simulate loading for a smoother transition
    setTimeout(() => {
      navigate(`/room/${roomId}`);
    }, 800);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 flex flex-col items-center justify-center px-4">
      <AnimatePresence>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="text-center"
        >
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3, duration: 0.8 }}
            className="mb-2"
          >
            <span className="bg-gray-100 text-gray-500 text-xs font-medium px-3 py-1 rounded-full">
              MEDICONNECT
            </span>
          </motion.div>
          
          <motion.h1 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5, duration: 0.8 }}
            className="text-4xl md:text-5xl lg:text-6xl font-semibold text-gray-900 mb-4 tracking-tight"
          >
            Medical consultations,{" "}
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-500 to-cyan-400">
              reimagined
            </span>
          </motion.h1>
          
          <motion.p 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.7, duration: 0.8 }}
            className="text-gray-500 max-w-lg mx-auto mb-10"
          >
            Experience seamless video consultations with integrated AI assistance for medical support and insights.
          </motion.p>
          
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.9, duration: 0.5 }}
          >
            <Button
              className={`relative bg-gray-900 hover:bg-gray-800 text-white px-8 py-6 rounded-2xl text-lg font-medium transition-all duration-300 ${
                isHovered ? "shadow-lg" : "shadow-md"
              } ${isLoading ? "pl-12" : ""}`}
              disabled={isLoading}
              onClick={handleCreateRoom}
              onMouseEnter={() => setIsHovered(true)}
              onMouseLeave={() => setIsHovered(false)}
            >
              {isLoading && (
                <div className="absolute left-6 top-1/2 transform -translate-y-1/2">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                </div>
              )}
              {isLoading ? "Creating room..." : "Create Room"}
            </Button>
          </motion.div>
        </motion.div>
      </AnimatePresence>

      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.2, duration: 0.8 }}
        className="absolute bottom-8 text-xs text-gray-400"
      >
        <p>© 2023 MediConnect. All rights reserved.</p>
      </motion.div>
    </div>
  );
};

export default Index;
