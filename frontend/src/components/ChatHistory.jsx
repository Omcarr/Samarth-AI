import React, { useState, useEffect } from "react";
import { useTheme } from "../Context/ThemeContext";
import { 
  BiSearch, 
  BiMoon, 
  BiSun, 
  BiX, 
  BiTrash, 
  BiMessageDetail,
  BiChevronRight 
} from "react-icons/bi";
import { formatDistanceToNow } from 'date-fns';

const ChatHistory = () => {
  const { theme, toggleTheme } = useTheme();
  const [chatHistory, setChatHistory] = useState([
    // Explicit mock data directly in the state initialization
    {
      id: 1,
      title: "React Development Discussion",
      participants: ["John Doe", "AI Assistant"],
      lastMessage: {
        text: "Can you help me with React component design?",
        sender: "John Doe",
        timestamp: new Date('2024-02-15T10:30:00')
      },
      messages: [
        { 
          id: 1,
          sender: "John Doe", 
          text: "Hello! I'm working on a complex React project.",
          timestamp: new Date('2024-02-15T10:25:00')
        },
        { 
          id: 2,
          sender: "AI Assistant", 
          text: "Great! What specific challenges are you facing?",
          timestamp: new Date('2024-02-15T10:27:00')
        }
      ]
    },
    {
      id: 2,
      title: "Python Machine Learning",
      participants: ["Alice Smith", "AI Assistant"],
      lastMessage: {
        text: "Let's discuss neural network architectures.",
        sender: "Alice Smith",
        timestamp: new Date('2024-02-14T15:45:00')
      },
      messages: [
        { 
          id: 1,
          sender: "Alice Smith", 
          text: "I'm struggling with CNN implementation.",
          timestamp: new Date('2024-02-14T15:40:00')
        },
        { 
          id: 2,
          sender: "AI Assistant", 
          text: "Convolutional Neural Networks can be complex. What specific part are you having trouble with?",
          timestamp: new Date('2024-02-14T15:43:00')
        }
      ]
    }
  ]);
  const [filteredChats, setFilteredChats] = useState([]);
  const [selectedChat, setSelectedChat] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");

  // Initialize filteredChats with the mock data
  useEffect(() => {
    setFilteredChats(chatHistory);
  }, [chatHistory]);

  // Search functionality
  const handleSearch = (e) => {
    const term = e.target.value.toLowerCase();
    setSearchTerm(term);

    const filtered = chatHistory.filter(chat => 
      chat.title.toLowerCase().includes(term) ||
      chat.participants.some(participant => 
        participant.toLowerCase().includes(term)
      ) ||
      chat.lastMessage.text.toLowerCase().includes(term)
    );

    setFilteredChats(filtered);
  };

  // Delete chat functionality
  const deleteChat = (chatId) => {
    const updatedChats = chatHistory.filter(chat => chat.id !== chatId);
    setChatHistory(updatedChats);
    setFilteredChats(updatedChats);
  };

  const openChatOverlay = (chat) => {
    setSelectedChat(chat);
  };

  const closeChatOverlay = () => {
    setSelectedChat(null);
  };

  // Rest of the component remains the same as in the previous implementation...
  return (
    <div className={`min-h-screen p-4 md:p-6 ${
      theme === "dark" 
        ? "bg-zinc-950 text-white" 
        : "bg-gray-50 text-gray-900"
    }`}>
      {/* Header Section */}
      <header className={`
        sticky top-0 z-10 py-4 px-4 md:px-6 
        flex flex-col md:flex-row 
        justify-between items-center 
        rounded-lg shadow-lg 
        ${theme === "dark" 
          ? "bg-zinc-900 text-white" 
          : "bg-white text-gray-900"
        }`}
      >
        <h1 className="text-2xl font-semibold mb-4 md:mb-0">Chat History</h1>
        
        <div className="flex flex-col md:flex-row items-center space-y-2 md:space-y-0 md:space-x-4 w-full md:w-auto">
          {/* Search Bar */}
          <div className="relative w-full md:max-w-sm">
            <BiSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search chats..."
              value={searchTerm}
              onChange={handleSearch}
              className={`
                w-full rounded-md pl-10 pr-4 py-2 
                focus:outline-none focus:ring-2 focus:ring-blue-500 
                ${theme === "dark" 
                  ? "bg-zinc-800 text-gray-300" 
                  : "bg-gray-200 text-gray-900"
                }`}
            />
          </div>
          
          {/* Theme Toggle */}
          <button
            onClick={toggleTheme}
            className={`
              p-2 rounded-md focus:outline-none transition 
              ${theme === "dark"
                ? "bg-zinc-800 hover:bg-zinc-700"
                : "bg-gray-200 hover:bg-gray-300"
              }`}
          >
            {theme === "dark" ? <BiSun className="text-xl" /> : <BiMoon className="text-xl" />}
          </button>
        </div>
      </header>

      {/* Chat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6 mt-6">
        {filteredChats.length === 0 ? (
          <div className="col-span-full text-center py-10">
            <p className="text-gray-500">No chats found</p>
          </div>
        ) : (
          filteredChats.map((chat) => (
            <div
              key={chat.id}
              className={`
                relative rounded-lg shadow-md p-4 
                cursor-pointer transition-all group 
                ${theme === "dark"
                  ? "bg-zinc-900 hover:bg-zinc-800"
                  : "bg-white hover:bg-gray-100"
                }`}
              onClick={() => openChatOverlay(chat)}
            >
              <div className="flex justify-between items-start">
                <div>
                  <h2 className="text-lg font-bold">{chat.title}</h2>
                  <p className={`text-sm ${
                    theme === "dark" ? "text-gray-400" : "text-gray-500"
                  }`}>
                    {chat.participants.join(", ")}
                  </p>
                </div>
                
                {/* Delete Chat Button */}
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteChat(chat.id);
                  }}
                  className="text-red-500 hover:text-red-700 opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <BiTrash />
                </button>
              </div>
              
              <div className="mt-2 flex justify-between items-end">
                <p className={`
                  text-xs truncate max-w-[70%] 
                  ${theme === "dark" ? "text-gray-300" : "text-gray-600"}
                `}>
                  {chat.lastMessage.text}
                </p>
                <span className={`
                  text-xs 
                  ${theme === "dark" ? "text-gray-500" : "text-gray-400"}
                `}>
                  {formatDistanceToNow(new Date(chat.lastMessage.timestamp), { addSuffix: true })}
                </span>
              </div>
              
              {/* View Chat Arrow */}
              <div className="absolute bottom-2 right-2 text-blue-500 opacity-0 group-hover:opacity-100 transition-opacity">
                <BiChevronRight />
              </div>
            </div>
          ))
        )}
      </div>

      {/* Chat Overlay Modal */}
      {selectedChat && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 p-4">
          <div
            className={`
              relative w-full max-w-3xl 
              max-h-[90vh] flex flex-col 
              rounded-lg shadow-lg 
              ${theme === "dark" 
                ? "bg-zinc-900 text-white" 
                : "bg-white text-gray-900"
              }`}
          >
            {/* Close Button */}
            <div className="flex justify-between items-center p-4 border-b border-gray-700">
              <h2 className="text-xl font-bold">{selectedChat.title}</h2>
              <button
                className="text-gray-400 hover:text-gray-600"
                onClick={closeChatOverlay}
              >
                <BiX size={24} />
              </button>
            </div>

            {/* Chat Messages */}
            <div className="flex-grow overflow-y-auto p-4 space-y-4">
              {selectedChat.messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${
                    message.sender === "AI Assistant" 
                      ? "justify-end" 
                      : "justify-start"
                  }`}
                >
                  <div className="max-w-[70%]">
                    <p
                      className={`
                        px-4 py-2 rounded-lg 
                        ${message.sender === "AI Assistant"
                          ? theme === "dark"
                            ? "bg-blue-600 text-white"
                            : "bg-blue-100 text-blue-900"
                          : theme === "dark"
                          ? "bg-gray-700 text-gray-100"
                          : "bg-gray-200 text-gray-900"
                        }`}
                    >
                      {message.text}
                    </p>
                    <span className={`
                      text-xs block mt-1 
                      ${message.sender === "AI Assistant" 
                        ? "text-right" 
                        : "text-left"
                      } ${theme === "dark" 
                        ? "text-gray-400" 
                        : "text-gray-500"
                      }`}
                    >
                      {formatDistanceToNow(new Date(message.timestamp), { addSuffix: true })}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatHistory;