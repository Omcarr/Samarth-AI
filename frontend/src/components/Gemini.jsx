import React, { useState } from "react";
import Sidebar from "./Sidebar";
import { Settings } from "lucide-react";

const GeminiPage = ({theme ,isSidebarOpen ,setSidebarOpen }) => {
  const [isSidebarOpen1, setIsSidebarOpen1] = useState(false);


  const toggleSidebar = () => {
    setIsSidebarOpen1(!isSidebarOpen1);
  };

  return (
    <div className="md:flex  md:h-screen md:absolute">
      {/* Sidebar */}
      <div
  onMouseLeave={toggleSidebar}
  className={`absolute left-0 top-1 bottom-1  backdrop-blur-lg  rounded-r-xl transform transition-transform duration-300 ${
    isSidebarOpen1 ? "translate-x-0" : "-translate-x-full"
  }`}
  style={{ width: "18rem" }}
>
  <Sidebar
  theme={theme}
  isSidebarOpen={isSidebarOpen}
  setSidebarOpen={setSidebarOpen}
  />
</div>


      {/* Sidebar Toggle Button */}
      {!isSidebarOpen1 && (
        <>
        <div
  onMouseEnter={toggleSidebar}
  className="flex flex-col justify-between h-screen "
>
  <h1 className={`text-[1.5rem] font-bold ${theme == 'dark' ? 'text-white' : 'text-black'} p-4 "`}>Gail Ministry</h1>

  <h1 className={`self-start text-[1.5rem] font-bold ${theme == 'dark' ? 'text-white' : 'text-black'} p-4 "`}><Settings/></h1>
</div>

        </>
      )}

    </div>
  );
};

export default GeminiPage;