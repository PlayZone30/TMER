import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { LanguageGenderSelect } from "@/components/LanguageGenderSelect";

export const Home = () => {
  const navigate = useNavigate();
  const [language, setLanguage] = useState("english");
  const [gender, setGender] = useState("male");

  const handleJoinRoom = () => {
    navigate(`/room/1?language=${language}&gender=${gender}`);
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4 bg-gray-50">
      <div className="w-full max-w-md space-y-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold">Welcome to MediConnect</h1>
          <p className="mt-2 text-gray-600">Select your preferences and join the room</p>
        </div>
        
        <div className="space-y-4">
          <LanguageGenderSelect
            onLanguageChange={setLanguage}
            onGenderChange={setGender}
          />
          
          <button
            onClick={handleJoinRoom}
            className="w-full py-2 px-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Join Room
          </button>
        </div>
      </div>
    </div>
  );
}; 