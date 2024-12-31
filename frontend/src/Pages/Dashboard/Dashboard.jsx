import React, { useState } from "react";
import DocumentUpload from "./DocumentUpload";
import PolicyManagement from "./PolicyManagement";
import DatabaseUpdate from "./FoulLanguageManager";
import { 
  Home as HomeIcon, 
  Upload as UploadIcon, 
  FileText as PolicyIcon, 
  Database as DatabaseIcon, 
  LogOut as LogoutIcon,
  Menu as MenuIcon,
  X as XIcon
} from "lucide-react";
import { Navigate, useNavigate } from "react-router-dom";
import FoulLanguageManager from "./FoulLanguageManager";

const Dashboard = () => {
  const [selectedPage, setSelectedPage] = useState("dashboard");
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const navigate = useNavigate();

  const renderContent = () => {
    switch (selectedPage) {
      case "dashboard":
        return (
          <div className="p-4 md:p-6 min-h-screen bg-[#EEEEE8]">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {[
                {
                  title: "Total Users",
                  value: "5",
                  color: "blue",
                  icon: "users",
                  change: "24hrs+",
                  changeColor: "green"
                },
                {
                  title: "Active Policies",
                  value: "19",
                  color: "green",
                  icon: "file-text",
                  change: "+5% from last week",
                  changeColor: "green"
                },
                {
                  title: "Pending Renewals",
                  value: "0",
                  color: "red",
                  icon: "refresh-cw",
                  change: "-2 from last period",
                  changeColor: "red"
                }
              ].map((card, index) => (
                <div 
                  key={index} 
                  className={`
                    bg-white border-${card.color}-500
                    rounded-2xl shadow-lg p-6 border-l-4 
                    transform transition-transform 
                    hover:scale-105 hover:shadow-xl
                  `}
                >
                  <div className="flex justify-between items-center">
                    <div>
                      <h5 className="text-gray-600 mb-2">{card.title}</h5>
                      <h3 className={`font-bold text-${card.color}-600`}>{card.value}</h3>
                    </div>
                    <div className={`
                      bg-${card.color}-100 
                      text-${card.color}-600 
                      w-12 h-12 rounded-full 
                      flex items-center justify-center
                    `}>
                      <i className={`fas fa-${card.icon}`}></i>
                    </div>
                  </div>
                  <p className={`text-sm text-${card.changeColor}-600 mt-2`}>{card.change}</p>
                </div>
              ))}
            </div>

            <div className="mt-8 p-4 bg-white rounded-2xl shadow-md ">
              <h5 className="mb-4 text-gray-800">Recent Activities</h5>
              <div className="space-y-4">
                {[
                  {
                    icon: "upload",
                    title: "New Document Uploaded",
                    description: "Policy document for John Doe",
                    time: "2 mins ago",
                  },
                  {
                    icon: "file-text",
                    title: "Policy Renewed",
                    description: "Auto Insurance Policy #5678",
                    time: "1 hour ago",
                  },
                ].map((activity, index) => (
                  <div
                    key={index}
                    className={`
                      flex items-center justify-between p-4 
                      bg-gray-50 hover:bg-gray-100
                      rounded-xl transition-colors
                    `}
                  >
                    <div className="flex items-center space-x-4">
                      <div className="bg-white shadow-sm w-12 h-12 rounded-full flex items-center justify-center">
                        <i className={`fas fa-${activity.icon} text-blue-600`}></i>
                      </div>
                      <div>
                        <h5 className="font-semibold text-gray-800">
                          {activity.title}
                        </h5>
                        <p className="text-gray-600">
                          {activity.description}
                        </p>
                      </div>
                    </div>
                    <p className="text-gray-500">{activity.time}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        );
      case "upload":
        return <DocumentUpload />;
      case "policy":
        return <PolicyManagement />;
      case "database":
        return <FoulLanguageManager />;
      default:
        return (
          <div className="p-8 min-h-screen bg-[#EEEEE8]">
            <h4 className="mb-4">Settings</h4>
            <p className="text-gray-600">
              Configure your system settings here.
            </p>
          </div>
        );
    }
  };

  const menuItems = [
    { text: "Dashboard", icon: <HomeIcon />, page: "dashboard" },
    { text: "Document Upload", icon: <UploadIcon />, page: "upload" },
    { text: "Policy Management", icon: <PolicyIcon />, page: "policy" },
    { text: "Foul language Dict", icon: <DatabaseIcon />, page: "database" },
  ];

  const handleMenuItemClick = (page) => {
    setSelectedPage(page);
    setIsMobileMenuOpen(false);
  };

  return (
    <div className="flex flex-col md:flex-row h-screen bg-[#EEEEE8]">
      {/* Mobile Header */}
      <div className="md:hidden flex justify-between items-center p-4 border-b bg-white">
        <div className="flex items-center space-x-4">
          <button 
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="p-2 rounded-md focus:outline-none"
          >
            {isMobileMenuOpen ? <XIcon /> : <MenuIcon />}
          </button>
          <h5 className="text-gray-800">{localStorage.getItem('username')}</h5>
        </div>
      </div>

      {/* Mobile Sidebar */}
      {isMobileMenuOpen && (
        <div className="md:hidden fixed inset-0 z-40 bg-white">
          <div className="p-6 text-center border-b">
            <h5 className="text-gray-800">Omkar Yadav</h5>
            <p className="text-gray-500">Admin</p>
            <div 
              onClick={() => setIsMobileMenuOpen(false)} 
              className="
                fixed top-4 right-4 z-50 p-2 rounded-full 
                bg-white text-black border-black hover:bg-gray-100 
                shadow-md border 
                cursor-pointer transition-all 
                transform hover:scale-105 active:scale-95
              "
              aria-label="Close menu"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
          </div>

          <ul className="p-4 space-y-2">
            {menuItems.map((item) => (
              <li
                key={item.text}
                onClick={() => handleMenuItemClick(item.page)}
                className={`
                  cursor-pointer p-2 rounded-lg flex items-center 
                  ${selectedPage === item.page 
                    ? 'bg-blue-100 text-blue-600'
                    : 'hover:bg-gray-100 text-gray-700'
                  }
                `}
              >
                <span className="w-6 h-6 mr-3">{item.icon}</span>
                {item.text}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Desktop Sidebar */}
      <div className="hidden md:block w-64 shadow-lg relative bg-white">
        <div className="p-6 text-center border-b">
          <h5 className="text-gray-800">Omkar Yadav</h5>
          <p className="text-gray-500">Admin</p>
        </div>

        <ul className="p-4 space-y-2">
          {menuItems.map((item) => (
            <li
              key={item.text}
              onClick={() => setSelectedPage(item.page)}
              className={`
                cursor-pointer p-2 rounded-lg flex items-center 
                ${selectedPage === item.page 
                  ? 'bg-zinc-100 text-zinc-950'
                  : 'hover:bg-gray-100 text-gray-700'
                }
              `}
            >
              <span className="w-6 h-6 mr-3">{item.icon}</span>
              {item.text}
            </li>
          ))}
        </ul>

        <div className="absolute bottom-4 left-3 right-0">
          <button 
            onClick={() => navigate('/home')}
            className="
              w-full p-2 rounded-lg 
              hover:bg-gray-100
              flex items-center justify-start
            "
          >
            <span className="w-6 h-6 mr-3"><LogoutIcon /></span>
            Back to the Bot
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 p-4 md:p-8">
        {renderContent()}
      </div>
    </div>
  );
};

export default Dashboard;