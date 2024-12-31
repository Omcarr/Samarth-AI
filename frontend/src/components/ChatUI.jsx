import React, { useState } from "react";
import { useTheme } from '../Context/ThemeContext';
import {
  MessageCircle,
  Send,
  Menu,
  X,
  User,
  Settings,
  FileText,
  Lock,
  LogOut,
  Home,
  Sun,
  Moon,
} from "lucide-react";
import DocumentProcessing from "../Pages/Features/DocumentProcessing";

const ChatUI = () => {
  const { theme, toggleTheme } = useTheme();

  
  const [isSidebarOpen, setSidebarOpen] = useState(false);

  const toggleSidebar = () => {
    setSidebarOpen(!isSidebarOpen);
  };

  const sidebarLinks = [
    { name: "Home", icon: <Home size={20} /> },
    { name: "Security Settings", icon: <Lock size={20} /> },
    { name: "Log Out", icon: <LogOut size={20} /> },
  ];

  return (
    <div
      className={`flex h-screen ${
        theme == "dark" ? "bg-black" : "bg-[#0c1638]"
      } text-gray-900`}
    >
      {/* Sidebar */}
      <aside
        className={`transform ${
          isSidebarOpen ? "translate-x-0" : "-translate-x-full"
        } transition-transform duration-300 fixed z-30 inset-y-0 left-0 w-64 ${
          theme === "dark" ? "bg-black" : "bg-[#0c1638]"
        } text-white p-4 md:static md:translate-x-0 shadow-lg`}
      >
        <div className="flex items-center justify-between ">
          <div className=" w-full">
            <h2 className="text-[1.6rem] font-bold tracking-wide ">
              Organization Bot
            </h2>
            
          </div>

          <button
        onClick={toggleSidebar}
        className="md:hidden focus:outline-none md:mt-0 mt-2"
      >
        {isSidebarOpen ? (
          <X className="text-white" />
        ) : (
          <Menu className="text-white" />
        )}
      </button>
      
        </div>
        <hr
              className={`${
                theme == "dark" ? "bg-white" : "bg-white"
              } h-1 w-full border-0 mt-3`}
            />
        <nav className="mt-8">
          <ul className="space-y-4">
            {sidebarLinks.map((link, index) => (
              <li
                key={index}
                className={`flex items-center space-x-3 p-2 rounded-lg cursor-pointer transform transition-transform duration-200 hover:scale-105 ${
                  theme == "dark" ? "hover:bg-gray-700" : "hover:bg-blue-800"
                }`}
              >
                {link.icon}
                <span className="font-medium">{link.name}</span>
              </li>
            ))}
          </ul>
        </nav>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden m-3 rounded-[2.6rem] ">
        {/* Header */}
        <header className="bg-white shadow-md p-4 flex justify-between items-center ">
          <div className="flex items-center space-x-4">
            <button
              onClick={toggleSidebar}
              className="md:hidden focus:outline-none"
            >
              <Menu className="cursor-pointer" />
            </button>
            <h1 className="text-2xl font-bold text-gray-800">
              Organization AI Assistant
            </h1>
          </div>
          <div className="flex items-center space-x-4">
            <button
              onClick={toggleTheme}
              className="p-2 rounded-full transition-transform transform hover:scale-110 focus:outline-none"
            >
              {theme === "dark" ? <Sun /> : <Moon className="text-gray-600" />}
            </button>
            <Settings className="cursor-pointer" />
            <User className="cursor-pointer" />
          </div>
        </header>
        <hr />
        <DocumentProcessing/>
       
      </div>
    </div>
  );
};

export default ChatUI;
