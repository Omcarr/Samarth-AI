import React, { useState, useEffect } from "react";
import { useTheme } from "/src/Context/ThemeContext.jsx";
import {
  Home,
  X,
  Menu,
  Settings,
  PlusCircle,
  Sparkles,
  MessageCircleDashed,
  ShieldCheck,
  LogOut,
  HelpCircle,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import SettingsPage from "./SettingsPage";

const Sidebar = ({ theme, isSidebarOpen, setSidebarOpen, onNewChat }) => {
  const navigate = useNavigate();
  const { toggleTheme } = useTheme();

  // State Management
  const [isAdmin, setIsAdmin] = useState(false);
  const [isAccountSettingsOpen, setIsAccountSettingsOpen] = useState(false);
  const [activeMode, setActiveMode] = useState(null);
  const [isTutorialOpen, setIsTutorialOpen] = useState(false);
  const [currentTutorialStep, setCurrentTutorialStep] = useState(0);

  // Tutorial Steps
  const tutorialSteps = [
    {
      element: "new-chat-button",
      title: "Start New Chat",
      description: "Click here to begin a fresh conversation with AI. The sparkles indicate intelligent assistance!",
      position: "bottom"
    },
    {
      element: "recent-chats",
      title: "Recent Chats",
      description: "Easily view and resume your recent conversations. Each chat preview helps you quickly find previous discussions.",
      position: "top"
    },
    {
      element: "admin-dashboard",
      title: "Admin Dashboard",
      description: "Access powerful administrative tools to manage your organization's settings and configurations.",
      position: "top"
    },
    {
      element: "account-settings",
      title: "Account Settings",
      description: "Personalize your experience by customizing your profile, preferences, and application settings.",
      position: "bottom"
    }
  ];


  const startTutorial = () => {
    setIsTutorialOpen(true);
    setCurrentTutorialStep(0);
  };

  const nextTutorialStep = () => {
    if (currentTutorialStep < tutorialSteps.length - 1) {
      setCurrentTutorialStep(currentTutorialStep + 1);
    } else {
      setIsTutorialOpen(false);
    }
  };

  const previousTutorialStep = () => {
    if (currentTutorialStep > 0) {
      setCurrentTutorialStep(currentTutorialStep - 1);
    }
  };


  const renderTutorialOverlay = () => {
    if (!isTutorialOpen) return null;

    const currentStep = tutorialSteps[currentTutorialStep];

    return (
      <div className="fixed inset-0 z-50 bg-black/60 flex items-center justify-center">
        <div 
          className={`bg-white  p-6 rounded-2xl shadow-2xl 
          max-w-md w-full relative animate-fade-in ${
            theme === "dark" ? "text-white" : "text-black"
          }`}
        >
          <div className="absolute top-4 right-4 flex space-x-2">
            {currentTutorialStep > 0 && (
              <button 
                onClick={previousTutorialStep}
                className="text-sm bg- text-black dark: px-3 py-1 rounded"
              >
                Previous
              </button>
            )}
            <button 
              onClick={nextTutorialStep}
              className="text-sm border border-black text-black px-3 py-1 rounded"
            >
              {currentTutorialStep === tutorialSteps.length - 1 ? 'Finish' : 'Next'}
            </button>
          </div>

          <h2 className="text-2xl  text-black font-bold mb-4">{currentStep.title}</h2>
          <p className="text-black  mb-6">{currentStep.description}</p>

          <div className="text-center mt-4">
            <span className="text-sm text-gray-500">
              Step {currentTutorialStep + 1} of {tutorialSteps.length}
            </span>
          </div>
        </div>
      </div>
    );
  };
 
  const TutorialTriggerButton = () => (
    <div 
      onClick={startTutorial}
      className={`fixed bottom-4 right-4 z-40 p-3 rounded-full 
      bg-[#2a2a08] text-white shadow-lg hover:bg-blue-600 
      transition-all duration-300 cursor-pointer animate-bounce`}
    >
      <HelpCircle size={24} />
    </div>
  );

  // Hardcoded Demo Chat History
  const [chatHistory] = useState([
    {
      id: "chat_001",
      title: "Project Budget Discussion",
      createdAt: "2024-03-15T09:30:00Z",
      lastMessageAt: "2024-03-15T10:45:00Z",
      userMessage: "Can we review the quarterly budget allocation?",
      botMessage: "Let's break down the budget for each department.",
    },
    {
      id: "chat_002",
      title: "Ministry Event Planning",
      createdAt: "2024-03-14T14:20:00Z",
      lastMessageAt: "2024-03-14T15:10:00Z",
      userMessage: "I need help planning our annual community outreach event.",
      botMessage: "I can assist you with event logistics and planning strategies.",
    },
    {
      id: "chat_003",
      title: "Grant Application Support",
      createdAt: "2024-03-13T11:15:00Z",
      lastMessageAt: "2024-03-13T12:00:00Z",
      userMessage: "Can you help me draft a grant proposal for our youth program?",
      botMessage: "Certainly! I'll guide you through the key components of a strong grant application.",
    },
    {
      id: "chat_004",
      title: "Volunteer Coordination",
      createdAt: "2024-03-12T16:40:00Z",
      lastMessageAt: "2024-03-12T17:20:00Z",
      userMessage: "We need to organize our volunteer recruitment for the upcoming month.",
      botMessage: "Let's create a comprehensive volunteer management strategy.",
    },
    {
      id: "chat_005",
      title: "Community Needs Assessment",
      createdAt: "2024-03-11T10:05:00Z",
      lastMessageAt: "2024-03-11T11:30:00Z",
      userMessage: "I want to conduct a comprehensive needs assessment for our community.",
      botMessage: "I'll help you develop a structured approach to gathering community insights.",
    },
  ]);

  // Check Admin Status (Hardcoded for demo)
  useEffect(() => {
    // For demo purposes, set admin to true
    setIsAdmin(true);
  }, []);

  // Handle Chat Selection
  const handleChatSelect = (chatId) => {
    
    navigate('/chat_history');
  };

  // New Chat Handler
  const handleNewChat = (mode) => {
    if (typeof window !== "undefined") {
      window.location.reload();
    }
    if (onNewChat) {
      onNewChat(mode);
    }
  };

  return (
    <>
    <div
      className={`transform md:w-[20%] h-full md:rounded-r-2xl ${
        isSidebarOpen ? "translate-x-0" : "-translate-x-full"
      } transition-transform duration-300 fixed z-30 inset-y-0 left-0 w-full ${
        theme === "dark" ? "bg-zinc-900 text-white" : "bg-[#EEEEE8] text-black"
      } p-4 md:relative md:translate-x-0 shadow-lg overflow-y-auto`}
    >
      {/* Sidebar Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="md:text-[1.7rem] font-bold tracking-wide">GAIL (INDIA) LIMITED</h2>
        <button
          onClick={() => setSidebarOpen(!isSidebarOpen)}
          className="md:hidden focus:outline-none"
        >
          {isSidebarOpen ? (
            <X className="text-white" />
          ) : (
            <Menu className="text-white" />
          )}
        </button>
      </div>

      {/* New Chat Button */}
      <div
        onClick={() => {
          const modeToUse = activeMode;
          handleNewChat(modeToUse);
        }}
        className={`group relative overflow-hidden 
         p-4 rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-300 
        transform hover:-translate-y-1 cursor-pointer mb-6 
        flex items-center justify-between active:scale-95 ${
          theme === "dark"
            ? "bg-gradient-to-r from-blue-600 to-blue-400 text-white"
            : "bg-gray-800 text-white"
        }`}
      >
        <div className="flex items-center space-x-3">
          <PlusCircle
            size={24}
            className="text-white group-hover:rotate-180 transition-transform duration-300"
          />
          <span className="block font-bold text-lg">Start New Chat</span>
        </div>
        <Sparkles
          size={20}
          className="absolute top-2 right-2 text-yellow-300 
          opacity-0 group-hover:opacity-100 transition-opacity duration-300 
          group-hover:animate-pulse"
        />
      </div>

      {/* Recent History Section */}
      <div className="mt-4">
  <h3 className="text-xl font-semibold mb-4">Recent Chats</h3>
  <div className="space-y-3">
    {chatHistory.slice(0, 5).map((chat) => (
      <div
        key={chat.id}
        className={`relative p-3 rounded-lg cursor-pointer transition-all duration-200 
          hover:bg-blue-800/10 hover:scale-[1.02] 
          ${
            theme === "dark"
              ? "hover:bg-blue-900/30"
              : "hover:bg-blue-100/50"
          }`}
      >
        {/* Chat Details */}
        <div
          onClick={() => handleChatSelect(chat.id)}
          className="flex items-center space-x-3"
        >
          <MessageCircleDashed size={20} className="text-blue-500" />
          <div className="flex-grow">
            <h4 className="font-medium text-sm">{chat.title}</h4>
          </div>
        </div>

        {/* Delete and Pin Options */}
        <div
          className="absolute top-1/2 right-3 transform -translate-y-1/2 opacity-0 
            transition-opacity duration-200 group-hover:opacity-100 flex space-x-2"
        >
          <button
            onClick={(e) => {
              e.stopPropagation(); // Prevent triggering chat selection
              // Handle delete logic here
              console.log(`Delete chat ${chat.id}`);
            }}
            className="p-1 rounded-full hover:bg-red-500 hover:text-white transition-colors duration-200"
          >
            <X size={16} />
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation(); // Prevent triggering chat selection
              // Handle pin logic here
              console.log(`Pin chat ${chat.id}`);
            }}
            className="p-1 rounded-full hover:bg-yellow-400 hover:text-white transition-colors duration-200"
          >
            <Sparkles size={16} />
          </button>
        </div>
      </div>
    ))}
    {chatHistory.length > 5 && (
      <button
        onClick={() => navigate('/home')}
        className="w-full text-center text-sm text-blue-500 hover:underline"
      >
        View All Chats
      </button>
    )}
  </div>
</div>

      {/* Admin Dashboard Button */}
      {isAdmin && (
        <div 
          onClick={() => navigate('/admin')}
          className={`mt-4 flex items-center space-x-3 p-3 rounded-lg cursor-pointer 
          transform transition-all duration-200 hover:scale-105 hover:bg-blue-800/30 
          ${theme === "dark" ? "hover:bg-blue-900/30" : "hover:bg-blue-100/50"}`}
        >
          <ShieldCheck size={20} className="text-green-500" />
          <span className="font-medium">Admin Dashboard</span>
        </div>
      )}

      {/* Account Settings */}
      <div
    onClick={() => {
      // Handle logout logic here
      console.log("User logged out");
      navigate('/login'); // Redirect to login page or perform any cleanup
    }}
    className="mt-10 ml-1  flex items-center space-x-3 p-2 rounded-lg cursor-pointer transform transition-all duration-200 hover:scale-105 hover:bg-red-500/30"
  >
    <LogOut size={20} className="text-red-500" />
    <span className="font-medium text-red-500">Log Out</span>
  </div>




      
    </div>
  {renderTutorialOverlay()}

<TutorialTriggerButton />
</>
  );
};

export default Sidebar;