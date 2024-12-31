import React, { useEffect, useState } from "react";
import DocumentProcessing from "../Pages/Features/DocumentProcessing";
import GenericPolicyQuestion from "../Pages/Features/GenericPolicyQuestion";
import ProjectPersonalQuestion from "../Pages/Features/ProjectPersonalQuestion";
import Sidebar from "./Sidebar";
import GeminiPage from "./Gemini";
import { Menu, Moon, Sun , X, } from "lucide-react";
import { useTheme } from '/src/Context/ThemeContext.jsx';
import { useLocation, useNavigate } from "react-router-dom";

export default function Modes({isSidebarOpen, setSidebarOpen}) {
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();

  const location = useLocation();
  const [currentMode, setCurrentMode] = useState(null);

  // Extract pathname and determine current mode
  const pathname = location.pathname.split('/')[2];
  
  // Determine initial mode based on pathname
  useEffect(() => {
    switch (pathname) {
      case "Documentprocessing":
        setCurrentMode("documentProcessing");
        break;
      case "genericpolicy":
        setCurrentMode("genericPolicy");
        break;
      case "Projectquestion":
        setCurrentMode("personalQuestion");
        break;
      default:
        setCurrentMode(null);
    }
  }, [pathname]);

  const renderComponent = () => {
    switch (currentMode) {
      case "documentProcessing":
        return <DocumentProcessing key="documentProcessing" />;
      case "genericPolicy":
        return <GenericPolicyQuestion key="genericPolicy" />;
      case "personalQuestion":
        return <ProjectPersonalQuestion key="personalQuestion" />;
      default:
        return null;
    }
  };

  // Handle new chat creation
  const handleNewChat = (mode) => {
    // Set the current mode
    setCurrentMode(mode);

    // Navigate to the corresponding route
    switch (mode) {
      case "documentProcessing":
        navigate("/modes/Documentprocessing");
        break;
      case "genericPolicy":
        navigate("/modes/genericpolicy");
        break;
      case "personalQuestion":
        navigate("/modes/Projectquestion");
        break;
      default:
        break;
    }
  };

  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);

  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth < 768);
    window.addEventListener("resize", handleResize);

    // Cleanup the event listener on component unmount
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  return (
    <div
      className={`flex h-screen w-full overflow-hidden ${
        theme === "dark" ? "bg-zinc-950" : "bg-[#F5F5F2]"
      }`}
    >
      {/* {!isMobile ? (
        <GeminiPage
          theme={theme}
          isSidebarOpen={isSidebarOpen}
          setSidebarOpen={setSidebarOpen}
          onNewChat={handleNewChat}
        />
      ) : (
        <> */}
        <Sidebar
          theme={theme}
          isSidebarOpen={isSidebarOpen}
          setSidebarOpen={setSidebarOpen}
          onNewChat={handleNewChat}
          
        />
        {/* </>
      )} */}

      {renderComponent()}

      
    </div>
  );
}