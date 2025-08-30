import React, { useState, useRef, useEffect } from "react";
import gsap from 'gsap';
import {
  Send,
  Menu,
  File,
  Mic,
  X,
  Upload,
  StopCircle,
  PlayIcon,
} from "lucide-react";
import { useTheme } from "/src/Context/ThemeContext.jsx";
import ThemeT from "../../components/ThemeT";
import { useWebSocket } from "/src/Backend/useWebSocket.js";


const DocumentProcessing = ({}) => {
  const {theme , toggleTheme} = useTheme();
  const [mode, setMode] = useState('Document_Processing'); // 'generic', 'document_processing', 'personal_query'
  const [inputValue, setInputValue] = useState("");
  const [messages, setMessages] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [recordedAudio, setRecordedAudio] = useState(null);
  const [isSidebarOpen, setSidebarOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const containerRef = useRef(null);
  const leftSectionRef = useRef(null);
  const rightSectionRef = useRef(null);

  useEffect(() => {
    if (messages.length === 0) {
      // Animate the container with fade-in
      gsap.fromTo(
        containerRef.current,
        { opacity: 0 },
        { opacity: 1, duration: 0.5, ease: "power2.out" }
      );

      // Animate the left section with slide-in from left
      gsap.fromTo(
        leftSectionRef.current,
        { x: -50, opacity: 0 },
        { x: 0, opacity: 1, duration: 0.7, delay: 0.3, ease: "power3.out" }
      );

      // Animate the right section with slide-in from right
      gsap.fromTo(
        rightSectionRef.current,
        { x: 50, opacity: 0 },
        { x: 0, opacity: 1, duration: 0.7, delay: 0.5, ease: "power3.out" }
      );
    }
  }, [messages]);

  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const timerIntervalRef = useRef(null);

  // WebSocket hook
  const { 
    sendMessage, 
    response, 
    isConnected, 
    responseTime,
    reset 
  } = useWebSocket({
    url: `ws:localhost:8080/ws/chat?Authorization=Bearer ${localStorage.getItem("token")}`,
    
  });

  console.log(localStorage.token);
  
  

  useEffect(() => {
    if (response) {
      setMessages((prev) => {
        const newMessages = [...prev];
        if (
          newMessages.length > 0 &&
          newMessages[newMessages.length - 1].role === "assistant"
        ) {
          newMessages[newMessages.length - 1].content = response;
        } else {
          newMessages.push({
            role: "assistant",
            content: response,
          });
        }
        // Save conversation after each new message
        return newMessages;
      });
    }
    setIsLoading(false);
  }, [response]);

  // Scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  // Handle message submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() && !selectedFile && !recordedAudio) return;

    // Prepare message payload
    const payload = {
      message: inputValue,
      mode: mode,
      file: null,
      audio: null
    };

    // Handle file upload
    if (selectedFile) {
      const fileReader = new FileReader();
      fileReader.readAsDataURL(selectedFile);
      fileReader.onload = () => {
        payload.file = {
          name: selectedFile.name,
          type: selectedFile.type,
          content: fileReader.result.split(',')[1] // base64 content
        };
        
        // Add user message
        setMessages(prev => [...prev, {
          role: 'user',
          content: inputValue,
          file: selectedFile.name,
          mode: mode
        }]);

        // Send message via WebSocket
        sendMessage(JSON.stringify(payload));

        // Reset input states
        setInputValue("");
        setSelectedFile(null);
        if (fileInputRef.current) fileInputRef.current.value = "";
      };
    } 
    // Handle audio upload
    else if (recordedAudio) {
      const audioReader = new FileReader();
      audioReader.readAsDataURL(recordedAudio);
      audioReader.onload = () => {
        payload.audio = {
          type: recordedAudio.type,
          duration: recordingTime,
          content: audioReader.result.split(',')[1] // base64 content
        };
        
        // Add user message
        setMessages(prev => [...prev, {
          role: 'user',
          content: inputValue,
          audio: 'Recorded Audio',
          mode: mode
        }]);

        // Send message via WebSocket
        sendMessage(JSON.stringify(payload));

        // Reset audio states
        setRecordedAudio(null);
        setRecordingTime(0);
      };
    } 
    // Text-only message
    else {
      // Add user message
      setMessages(prev => [...prev, {
        role: 'user',
        content: inputValue,
        mode: mode
      }]);

      // Send message via WebSocket
      sendMessage(JSON.stringify(payload));

      // Reset input
      setInputValue("");
    }
  };

  // Mode change handler
  const handleModeChange = (newMode) => {
    setMode(newMode);
    // Optionally send mode change notification to server
    sendMessage(JSON.stringify({ 
      type: 'mode_change', 
      mode: newMode 
    }));
  };

  // File selection handler
  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  // Remove selected file
  const handleFileRemove = () => {
    setSelectedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  // Voice recording functionality
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream, {
        mimeType: "audio/webm",
      });

      audioChunksRef.current = [];
      setRecordingTime(0);

      // Start timer
      timerIntervalRef.current = setInterval(() => {
        setRecordingTime((prev) => prev + 1);
      }, 1000);

      mediaRecorderRef.current.ondataavailable = (e) => {
        audioChunksRef.current.push(e.data);
      };

      mediaRecorderRef.current.onstop = () => {
        // Clear timer
        if (timerIntervalRef.current) {
          clearInterval(timerIntervalRef.current);
        }

        const audioBlob = new Blob(audioChunksRef.current, {
          type: "audio/webm",
        });

        // Reset chunks
        audioChunksRef.current = [];

        // Set recorded audio
        setRecordedAudio(audioBlob);
        setIsRecording(false);
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
    } catch (error) {
      console.error("Error accessing microphone:", error);
    }
  };

  // Stop recording
  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
    }
  };

  // Remove recorded audio
  const handleAudioRemove = () => {
    setRecordedAudio(null);
    setRecordingTime(0);
  };

  // Format recording time
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  };
  return (
    <div className="md:w-full flex justify-center align-center">
      <div className="md:block hidden">
        <ThemeT />
      </div>
      <div
        className={` flex md:w-[60%] w-full flex-col min-h-screen  ${
          theme == "dark" ? "" : "rounded-xl"
        }  overflow-hidden`}
      >
        <header
          className={` ${
            theme === "dark" ? " rounded-xl m-1" : " rounded-xl m-1 "
          } p-4 flex  justify-between items-center sticky top-0 z-10`}
        >
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setSidebarOpen(!isSidebarOpen)}
              className={`md:hidden focus:outline-none ${
                theme === "dark" ? "text-white" : "text-[#6B6B6B]"
              }`}
            >
              <Menu className="cursor-pointer" />
            </button>
          </div>
          <div className="flex justify-center align-center text-center w-full">
            <h1
              className={`${
                theme == "dark" ? "text-white" : "text-black"
              } text-center text-3xl `}
            >
              Document Processing Assistant
            </h1>
          </div>
        </header>
        {messages.length > 0 && (
          <hr
            className={`${theme == "dark" ? "bg-white" : "bg-gray-800"} -mt-2"`}
          />
        )}
        <div className="flex-1 md:w-full overflow-hidden flex flex-col ">
        {messages.length === 0 && (
  <div
    ref={containerRef}
    className={`flex items-center justify-center h-full ${
      theme === "dark" ? "" : ""
    }`}
  >
    <div className="w-full max-w-4xl p-6 flex flex-col md:flex-row">
      {/* Left Section */}
      <div
        ref={leftSectionRef}
        className="md:w-1/2 text-center md:text-left md:pr-8 border-b md:border-b-0 md:border-r border-gray-300 pb-6 md:pb-0"
      >
        <h2
          className={`text-3xl md:text-4xl font-medium mb-4 ${
            theme === "dark" ? "text-white" : "text-gray-800"
          }`}
        >
          Document Processing Unit
        </h2>
        <p
          className={`text-base md:text-lg ${
            theme === "dark" ? "text-gray-400" : "text-gray-600"
          }`}
        >
          How can I help you today?
        </p>
      </div>

      {/* Right Section */}
      <div
        ref={rightSectionRef}
        className="md:w-1/2 flex items-center justify-center md:pl-8 mt-6 md:mt-0"
      >
        <p
          className={`text-sm md:text-base ${
            theme === "dark" ? "text-gray-400" : "text-gray-600"
          } text-center md:text-left`}
        >
          Feel free to ask me anything, and I'll do my best to assist you.
        </p>
      </div>
    </div>
  </div>
)}

          {messages.length > 0 && (
            <div
              className={`flex-1 overflow-y-auto p-4 ${
                theme === "dark" ? "bg-zinc-950" : ""
              }`}
            >
              <div className="max-w-4xl mx-auto space-y-4">
                {messages.map((message, index) => (
                  <div
                    key={index}
                    className={`flex mch ${
                      message.role === "user" ? "justify-end" : "justify-start"
                    }`}
                  >
                    <div
                      className={`max-w-[80%] rounded-lg p-3 ${
                        message.role === "user"
                          ? "bg-[#F0F0F0] text-[#333333]"
                          : theme === "dark"
                          ? "bg-[#2A2C3E] text-white"
                          : "bg-[#F5F5F2] text-[#333333]"
                      } shadow mch`}
                    >
                      {message.content}

                      {/* File Attachment Rendering */}
                      {message.file && (
                        <div className="flex items-center mt-2">
                          <File className="mr-2 text-blue-500" size={16} />
                          <span className="text-sm">{message.file}</span>
                        </div>
                      )}

                      {/* Audio Message Rendering */}
                      {message.audioUrl && (
                        <div className="audio-message flex items-center bg-gray-100 dark:bg-gray-700 p-2 rounded-lg mt-2">
                          <button
                            onClick={() => {
                              const audio = new Audio(message.audioUrl);
                              audio.play();
                            }}
                            className="mr-2"
                          >
                            <PlayIcon className="w-6 h-6 text-blue-500" />
                          </button>
                          <div className="flex-grow">
                            <div className="w-full bg-blue-200 dark:bg-blue-900 h-2 rounded">
                              <div
                                className="bg-blue-500 h-2 rounded"
                                style={{
                                  width: `${message.audioDuration || 0}%`,
                                }}
                              />
                            </div>
                            <span className="text-xs text-gray-500 dark:text-gray-300">
                              {message.audioDuration
                                ? `${Math.floor(message.audioDuration)} sec`
                                : ""}
                            </span>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                ))}

                {isLoading && (
                  <div className="flex justify-start">
                    <div
                      className={`${
                        theme === "dark" ? "bg-[#2A2C3E]" : "bg-[#F0F0F0]"
                      } p-3 shadow-md`}
                    >
                      <div className="flex space-x-2">
                        <div
                          className={`w-2 h-2 ${
                            theme === "dark" ? "bg-white" : "bg-black"
                          } animate-bounce`}
                        />
                        <div
                          className={`w-2 h-2 ${
                            theme === "dark" ? "bg-white" : "bg-black"
                          } animate-bounce`}
                          style={{ animationDelay: "0.2s" }}
                        />
                        <div
                          className={`w-2 h-2 ${
                            theme === "dark" ? "bg-white" : "bg-black"
                          } animate-bounce`}
                          style={{ animationDelay: "0.4s" }}
                        />
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            </div>
          )}

          {/* Audio recording indicator */}
          {isRecording && (
            <div
              className="fixed bottom-24 left-1/2 transform -translate-x-1/2 
              bg-red-500 text-white px-4 py-2 rounded-full flex items-center space-x-2 z-50"
            >
              <div className="w-3 h-3 bg-white rounded-full animate-pulse" />
              <span>{formatTime(recordingTime)}</span>
            </div>
          )}

          <div
            className={`p-6  ${
              theme === "dark" ? "bg-zinc-950 shadow-xl" : ""
            }`}
          >
            <form
              onSubmit={handleSubmit}
              className="w-full mx-auto relative rounded-lg"
            >
              {/* File preview if a file is selected */}
              {selectedFile && (
                <div
                  className="absolute bottom-full mb-2 flex items-center 
                bg-gray-100 dark:bg-zinc-800 p-2 rounded-lg"
                >
                  <File className="mr-2 text-blue-500" size={20} />
                  <span className="mr-2 text-sm truncate max-w-[200px]">
                    {selectedFile.name}
                  </span>
                  <button
                    type="button"
                    onClick={handleFileRemove}
                    className="text-red-500 hover:text-red-700"
                  >
                    <X size={20} />
                  </button>
                </div>
              )}

              {/* Recorded audio preview */}
              {recordedAudio && (
                <div
                  className="absolute bottom-full mb-2 flex items-center 
                bg-gray-100 dark:bg-zinc-800 p-2 rounded-lg"
                >
                  <Mic className="mr-2 text-green-500" size={20} />
                  <span className="mr-2 text-sm">
                    Recorded Audio ({formatTime(recordingTime)})
                  </span>
                  <button
                    type="button"
                    onClick={handleAudioRemove}
                    className="text-red-500 hover:text-red-700"
                  >
                    <X size={20} />
                  </button>
                </div>
              )}

              {/* Input container */}
              <div className="flex items-center space-x-2">
                {/* File upload input */}
                <input
                  type="file"
                  ref={fileInputRef}
                  className="hidden"
                  onChange={handleFileSelect}
                />
                <button
                  type="button"
                  onClick={() => fileInputRef.current.click()}
                  className={`p-2 rounded-full ${
                    theme === "dark"
                      ? "bg-gray-600 hover:bg-zinc-700"
                      : " hover:bg-gray-100"
                  }`}
                  title="Upload File"
                >
                  <Upload size={20} />
                </button>

                {/* Voice recording button */}
                <button
                  type="button"
                  onClick={isRecording ? stopRecording : startRecording}
                  className={`p-2 rounded-full ${
                    isRecording
                      ? "bg-red-500 text-white"
                      : theme === "dark"
                      ? "bg-gray-600 hover:bg-zinc-700"
                      : " hover:bg-gray-100"
                  }`}
                  title={isRecording ? "Stop Recording" : "Start Voice Query"}
                >
                  {isRecording ? (
                    <StopCircle size={20} color="white" />
                  ) : (
                    <Mic size={20} color="currentColor" />
                  )}
                </button>

                {/* Text input */}
                <input
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  placeholder="Type your message here..."
                  className={`flex-grow w-full p-4 border border-[#D9D9D9] rounded-full focus:outline-none focus:ring-2 ${
                    theme === "dark"
                      ? "bg-zinc-900 text-white placeholder-gray-500 border-none focus:ring-[#4A90E2]"
                      : "text-[#555555] focus:ring-[#D9D9D9]"
                  }`}
                  disabled={isLoading}
                />

                <button
                  type="submit"
                  disabled={isLoading}
                  className={`rounded-full ${
                    theme === "dark"
                      ? "text-white hover:text-gray-300"
                      : "text-[#6B6B6B] hover:text-[#333333]"
                  } disabled:opacity-50 transition-transform hover:scale-110`}
                >
                  <Send className="" size={20} />
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DocumentProcessing;
