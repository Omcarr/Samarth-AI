import React, { useEffect, useState } from "react";
import axios from "axios";
import { AnimatePresence, motion } from "framer-motion";
import {
  Lock,
  Mail,
  ArrowLeft,
  Loader2,
  ChevronRight,
  Shield,
  User2,
} from "lucide-react";
import { useNavigate } from "react-router-dom";

const LoginSignup = () => {
  const [step, setStep] = useState(1);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [verificationCode, setVerificationCode] = useState("");
  const [timer, setTimer] = useState(90);
  const [canResend, setCanResend] = useState(false);

  useEffect(() => {
    if (timer > 0) {
      const countdown = setInterval(() => {
        setTimer((prevTimer) => prevTimer - 1);
      }, 1000);

      return () => clearInterval(countdown);
    } else {
      setCanResend(true);
    }
  }, [timer]);

  const navigate = useNavigate();
  const slideVariants = {
    enter: { x: 100, opacity: 0 },
    center: { x: 0, opacity: 1 },
    exit: { x: -100, opacity: 0 },
  };

  const handleLogin = async () => {
    setError("");
    setLoading(true);

    try {
      const response = await axios.post(
        "http://localhost:8080/login",
        {
          username: email,
          password,
        }
      );

      const message = response.data.message;

      if (message) {
        setStep(3);
      }
    } catch (err) {
      const errorMessage =
        err.response?.data?.detail?.message ||
        err.message ||
        "Something went wrong.";
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const validateOtp = async () => {
    setError("");
    setLoading(true);

    try {
      const response = await axios.post(
        "https://localhost:8080/verify-2fa",
        {
          username: email,
          code: verificationCode,
        }
      );

      // Destructure the response data
      const { 
        access_token, 
        username, 
        isAdmin, 
        Pinned_chats, 
        Previous_chats 
      } = response.data;

      // Save multiple items to localStorage
      localStorage.setItem("token", access_token);
      localStorage.setItem("username", username);
      localStorage.setItem("isAdmin", JSON.stringify(isAdmin));
      localStorage.setItem("pinnedChats", JSON.stringify(Pinned_chats));
      localStorage.setItem("previousChats", JSON.stringify(Previous_chats));

      navigate("/home");
    } catch (err) {
      const errorMessage =
        err.response?.data?.detail ||
        err.message ||
        "Invalid verification code or server error.";
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleResendOtp = async () => {
    // Only allow resend if timer is 0
    if (timer === 0) {
      try {
        setLoading(true);
        setError(null);

        // Replace with your actual API endpoint
        const response = await axios.post(`http://localhost:8080/resend_otp?user_trying_to_login=${email}`, 
         
        );

        // Reset timer and prevent immediate resend
        setTimer(180);
        setCanResend(false);

        // Optional: Handle successful OTP resend
        // You might want to show a success toast/message
        console.log('OTP Resent Successfully', response.data);
      } catch (err) {
        // Handle any errors during OTP resend
        setError(err.response?.data?.message || 'Failed to resend OTP');
        console.error('OTP Resend Error:', err);
      } finally {
        setLoading(false);
      }
    }
  };

  const renderStep = () => {
    switch (step) {
      case 1:
        return (
          <motion.div
            key="username"
            variants={slideVariants}
            initial="enter"
            animate="center"
            exit="exit"
            className="w-full space-y-6"
          >
            <div className="space-y-2">
              <h2 className="text-3xl font-bold text-gray-800">
                GAIL Login
              </h2>
              <p className="text-gray-600">Enter your username</p>
            </div>

            <form
              className="space-y-4"
              onSubmit={(e) => {
                e.preventDefault();
                setStep(2);
              }}
            >
              {error && (
                <div className="bg-red-100 border border-red-300 text-red-700 p-3 rounded-lg text-center">
                  {error}
                </div>
              )}

              <div className="relative">
                <input
                  type="username"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-white border border-gray-300 text-gray-900 px-4 py-3 rounded-lg focus:ring-2 focus:border-transparent pl-12"
                  placeholder="Username here"
                  required
                />
                <User2 className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
              </div>

              <button
                type="submit"
                className="w-full bg-[#272721] text-white py-3 rounded-lg transition-all duration-200 flex items-center justify-center gap-2 group"
              >
                {loading ? (
                  <Loader2 className="animate-spin" size={20} />
                ) : (
                  <>
                    <span>Continue</span>
                    <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                  </>
                )}
              </button>
              <div className="flex justify-center align-center">
              <button className="pointer  " onClick={()=>{navigate('/signup')}}>don't have an account , Signup</button>
              </div>
              
            </form>
          </motion.div>
        );
      case 2:
        return (
          <motion.div
            key="password"
            variants={slideVariants}
            initial="enter"
            animate="center"
            exit="exit"
            className="w-full space-y-6"
          >
            <button
              onClick={() => setStep(1)}
              className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Back</span>
            </button>

            <div className="space-y-2">
              <h2 className="text-3xl font-bold text-gray-800">Secure Access</h2>
              <p className="text-gray-600">Enter your GAIL credentials</p>
            </div>

            <form
              className="space-y-4"
              onSubmit={(e) => {
                e.preventDefault();
                handleLogin();
              }}
            >
              {error && (
                <div className="bg-red-100 border border-red-300 text-red-700 p-3 rounded-lg text-center">
                  {error}
                </div>
              )}

              <div className="relative">
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-white border border-gray-300 text-gray-900 px-4 py-3 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent pl-12"
                  placeholder="Enter secure password"
                  required
                />
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
              </div>

              <button
                type="submit"
                className="w-full bg-[#272721] text-white py-3 rounded-lg transition-all duration-200 flex items-center justify-center gap-2 group"
              >
                {loading ? (
                  <Loader2 className="animate-spin" size={20} />
                ) : (
                  <>
                    <span>Verify Credentials</span>
                    <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                  </>
                )}
              </button>
            </form>
          </motion.div>
        );
      case 3:
        return (
          <motion.div
            key="verification"
            variants={slideVariants}
            initial="enter"
            animate="center"
            exit="exit"
            className="w-full space-y-6"
          >
            <button
              onClick={() => setStep(2)}
              className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Back</span>
            </button>
        
            <div className="space-y-2">
              <h2 className="text-3xl font-bold text-gray-800">Two-Factor Authentication</h2>
              <p className="text-gray-600">
                Enter verification code sent to
                <br />
                <span className="text-black text-1xl">{email}</span>
              </p>
            </div>
        
            <div className="space-y-4">
              {error && (
                <div className="bg-red-100 border border-red-300 text-red-700 p-3 rounded-lg text-center">
                  {error}
                </div>
              )}
        
              <div className="flex gap-2 justify-center">
                {[...Array(6)].map((_, i) => (
                  <input
                    key={i}
                    type="text"
                    maxLength={1}
                    className="w-10 sm:w-12 h-10 sm:h-12 bg-white border border-gray-300 text-gray-900 rounded-lg text-center text-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    value={verificationCode[i] || ""}
                    onChange={(e) => {
                      const newCode = verificationCode.split("");
                      newCode[i] = e.target.value;
                      setVerificationCode(newCode.join(""));
                      if (e.target.value && e.target.nextElementSibling) {
                        e.target.nextElementSibling.focus();
                      }
                    }}
                  />
                ))}
              </div>
        
              <button
                onClick={validateOtp}
                className="w-full bg-[#272721] text-white py-3 rounded-lg  transition-all duration-200 flex items-center justify-center gap-2 group"
              >
                {loading ? (
                  <Loader2 className="animate-spin" size={20} />
                ) : (
                  <>
                    <span>Verify & Access Platform</span>
                    <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                  </>
                )}
              </button>
        
              <div className="flex items-center justify-between">
                <button 
                  onClick={handleResendOtp}
                  disabled={timer > 0}
                  className={`w-full text-sm transition-colors 
                    ${timer > 0 
                      ? 'text-gray-500 cursor-not-allowed' 
                      : 'text-blue-600 hover:text-blue-700 hover:underline'
                    }`}
                >
                  {timer > 0 
                    ? `Resend OTP in ${timer} seconds` 
                    : 'Resend Verification Code'
                  }
                </button>
              </div>
            </div>
          </motion.div>
        );
      default:
        return null;
    }
  };

  // Mobile background component
  const MobileBackground = () => (
    <div className="absolute inset-0 bg-gradient-to-br from-blue-200 via-blue-100 to-blue-50 opacity-50" />
  );

  return (
    <div className="min-h-screen w-full flex flex-col lg:flex-row bg-[#EEEEE8]">
      {/* Visual Side - Hidden on mobile, shown on desktop */}
      <div className="relative w-full lg:w-1/2 p-6 sm:p-8 flex items-center justify-center min-h-screen">
        {/* Show gradient background only on mobile */}
        <div className="block lg:hidden">
          <MobileBackground />
        </div>

        <div className="relative w-full max-w-md mx-auto bg-white p-8 rounded-xl shadow-lg">
          <div className="mb-12">
            <motion.div
              initial={{ scale: 0.8 }}
              animate={{ scale: 1 }}
              className="flex items-center gap-2"
            >
              <Shield className="w-8 h-8 " />
              <h1 className="text-3xl font-bold text-gray-800">
                GAIL Chatbot
              </h1>
            </motion.div>
          </div>

          <AnimatePresence mode="wait">{renderStep()}</AnimatePresence>
        </div>
      </div>
      <div className="hidden text-center lg:block w-1/2 relative overflow-hidden bg-white shadow-lg">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="absolute inset-0 flex items-center justify-center"
        >
          <div className="relative w-full">
            <motion.div
              animate={{
                rotate: 360,
                scale: [1, 1.1, 1],
              }}
              transition={{
                rotate: { duration: 20, repeat: Infinity, ease: "linear" },
                scale: { duration: 4, repeat: Infinity, ease: "easeInOut" },
              }}
              className="absolute text-center inset-0 rounded-full opacity-20 blur-2xl"
            />
            <img src="/gail_logo.svg" alt="" className="mx-auto" />
          </div>
        </motion.div>

        {/* Animated Lines */}
        <div className="absolute inset-0">
          {[...Array(5)].map((_, i) => (
            <motion.div
              key={i}
              initial={{ x: "-100%" }}
              animate={{ x: "200%" }}
              transition={{
                duration: 3,
                delay: i * 0.4,
                repeat: Infinity,
                ease: "linear",
              }}
              className="absolute h-px bg-gradient-to-r from-transparent via-gray-300 to-transparent opacity-30"
              style={{ top: `${20 + i * 15}%` }}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

export default LoginSignup;