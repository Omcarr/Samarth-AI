import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { User, Mail, Key, LogOut, X as XIcon, ChevronRight } from "lucide-react";

const SettingsPage = ({ theme = "dark" }) => {
  const navigate = useNavigate();
  const [activeSection, setActiveSection] = useState(null);
  const [isVisible, setIsVisible] = useState(true);

  const onClose = () => {
    setIsVisible(false);
    navigate("/home");
  }

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("userRole");
    navigate("/login_signup");
  };

  const menuItems = [
    { 
      icon: <Mail size={22} className="text-blue-500" />, 
      label: "Email Notifications",
      description: "Manage your notification preferences"
    },
    { 
      icon: <Key size={22} className="text-blue-500" />, 
      label: "Password & Security",
      description: "Update password and security settings"
    },
  ];

  // If not visible, return null to completely hide the component
  if (!isVisible) return null;

  return (
    <div className={`
      fixed inset-0 z-[9999] flex items-center justify-center 
      ${theme === "dark" ? "bg-zinc-900/50 backdrop-blur-sm" : "bg-gray-100/50 backdrop-blur-sm"}
      h-screen w-screen overflow-hidden
    `}>
      <div className={`
        w-[400px] rounded-2xl p-6 relative
        ${theme === "dark" ? "bg-zinc-800 text-white" : "bg-white text-gray-900"}
        shadow-2xl border 
        ${theme === "dark" ? "border-zinc-700" : "border-gray-200"}
        transform transition-all duration-300 ease-in-out scale-100 hover:scale-105
      `}>
        {/* Exit Button */}
        <button 
          onClick={onClose}
          className={`
            absolute top-4 right-4 p-2 rounded-full 
            transition-all duration-200
            ${theme === "dark"
              ? "hover:bg-zinc-700 text-gray-300 hover:text-white"
              : "hover:bg-gray-100 text-gray-600 hover:text-black"
            }
          `}
        >
          <XIcon size={24} />
        </button>

        {/* Existing component content remains the same */}
        {/* Profile Header */}
        <div className="flex items-center space-x-4 mb-6">
          <div className={`
            w-16 h-16 rounded-full flex items-center justify-center 
            ${theme === "dark" ? "bg-zinc-700 text-gray-200" : "bg-gray-200 text-gray-800"}
          `}>
            <User size={36} className="text-blue-500" />
          </div>
          <div>
            <h2 className="text-xl font-bold">John Doe</h2>
            <p className={`text-sm ${theme === "dark" ? "text-gray-400" : "text-gray-600"}`}>
              johndoe@example.com
            </p>
          </div>
          <button className={`
            ml-auto px-3 py-1.5 rounded-full text-sm font-medium
            ${theme === "dark" 
              ? "bg-blue-600 hover:bg-blue-700 text-white" 
              : "bg-blue-500 hover:bg-blue-600 text-white"
            }
          `}>
            Edit
          </button>
        </div>

        {/* Settings Menu */}
        <div className="space-y-2">
          {menuItems.map((item, index) => (
            <div 
              key={item.label}
              onClick={() => setActiveSection(index)}
              className={`
                flex items-center justify-between p-4 rounded-xl cursor-pointer 
                transition-all duration-200 group
                ${activeSection === index 
                  ? (theme === "dark" 
                    ? "bg-zinc-700" 
                    : "bg-gray-200") 
                  : (theme === "dark" 
                    ? "hover:bg-zinc-700" 
                    : "hover:bg-gray-100")
                }
              `}
            >
              <div className="flex items-center space-x-4">
                {item.icon}
                <div>
                  <h3 className="font-semibold">{item.label}</h3>
                  <p className={`text-xs ${theme === "dark" ? "text-gray-400" : "text-gray-500"}`}>
                    {item.description}
                  </p>
                </div>
              </div>
              <ChevronRight 
                size={20} 
                className={`
                  opacity-0 group-hover:opacity-100 transition-opacity 
                  ${theme === "dark" ? "text-gray-400" : "text-gray-600"}
                `} 
              />
            </div>
          ))}
        </div>

        {/* Footer Action */}
        <div className="mt-6 text-center">
          <button 
            onClick={handleLogout}
            className={`
              w-full py-3 rounded-xl text-sm font-medium
              ${theme === "dark" 
                ? "bg-red-600/20 text-red-400 hover:bg-red-600/30" 
                : "bg-red-100 text-red-600 hover:bg-red-200"}
              transition-colors duration-200
            `}
          >
            <LogOut size={20} className="inline-block mr-2 -mt-1" />
            Log Out
          </button>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;