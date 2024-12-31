import React, { useState } from "react";
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
  Phone,
} from "lucide-react";
import { Link, useNavigate } from "react-router-dom";

const Signup = () => {
  const [step, setStep] = useState(1);
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [phoneNumber, setPhoneNumber] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [verificationCode, setVerificationCode] = useState("");
  const [passwordStrength, setPasswordStrength] = useState(0);

  const navigate = useNavigate();

  const slideVariants = {
    enter: { x: 100, opacity: 0 },
    center: { x: 0, opacity: 1 },
    exit: { x: -100, opacity: 0 },
  };

  const calculatePasswordStrength = (password) => {
    let strength = 0;
    if (password.length >= 8) strength++;
    if (password.match(/[a-z]+/)) strength++;
    if (password.match(/[A-Z]+/)) strength++;
    if (password.match(/[0-9]+/)) strength++;
    if (password.match(/[$@#&!]+/)) strength++;
    return strength;
  };

  const handlePasswordChange = (e) => {
    const newPassword = e.target.value;
    setPassword(newPassword);
    setPasswordStrength(calculatePasswordStrength(newPassword));
  };

  const handleSignup = async () => {
    setError("");
    setLoading(true);

    try {
      const response = await axios.post(
        "https://815d-117-96-43-108.ngrok-free.app/signup",
        {
          username,
          email,
          password,
          phone_number: phoneNumber,
        }
      );

      const message = response.data.message;

      if (message) {
        navigate("/login_signup");
      }
    } catch (err) {
      const errorMessage =
        err.response?.data?.detail?.message ||
        err.message ||
        "Something went wrong during signup.";
      setError(errorMessage);
    } finally {
      setLoading(false);
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
                Create Account
              </h2>
              <p className="text-gray-600">Choose your username</p>
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
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full bg-white border border-gray-300 text-gray-900 px-4 py-3 rounded-lg focus:ring-2 focus:border-transparent pl-12"
                  placeholder="Choose a username"
                  required
                />
                <User2 className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
              </div>

              <button
                type="submit"
                className="w-full bg-[#272721] text-white py-3 rounded-lg transition-all duration-200 flex items-center justify-center gap-2 group"
              >
                <span>Continue</span>
                <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </button>
            </form>
          </motion.div>
        );
      case 2:
        return (
          <motion.div
            key="details"
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
              <h2 className="text-3xl font-bold text-gray-800">Your Details</h2>
              <p className="text-gray-600">Complete your profile</p>
            </div>

            <form
              className="space-y-4"
              onSubmit={(e) => {
                e.preventDefault();
                handleSignup();
              }}
            >
              {error && (
                <div className="bg-red-100 border border-red-300 text-red-700 p-3 rounded-lg text-center">
                  {error}
                </div>
              )}

              <div className="relative">
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-white border border-gray-300 text-gray-900 px-4 py-3 rounded-lg focus:ring-2 focus:border-transparent pl-12"
                  placeholder="Email address"
                  required
                />
                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
              </div>

              <div className="relative">
                <input
                  type="tel"
                  value={phoneNumber}
                  onChange={(e) => setPhoneNumber(e.target.value)}
                  className="w-full bg-white border border-gray-300 text-gray-900 px-4 py-3 rounded-lg focus:ring-2 focus:border-transparent pl-12"
                  placeholder="Phone number"
                  required
                />
                <Phone className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
              </div>

              <div className="relative">
                <input
                  type="password"
                  value={password}
                  onChange={handlePasswordChange}
                  className="w-full bg-white border border-gray-300 text-gray-900 px-4 py-3 rounded-lg focus:ring-2 focus:border-transparent pl-12"
                  placeholder="Create a strong password"
                  required
                />
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                
                {/* Password Strength Indicator */}
                <div className="mt-2 flex space-x-1">
                  {[1, 2, 3, 4, 5].map((level) => (
                    <div
                      key={level}
                      className={`h-1 flex-1 rounded-full ${
                        level <= passwordStrength
                          ? "bg-green-500"
                          : "bg-gray-200"
                      }`}
                    />
                  ))}
                </div>
              </div>

              <button
                type="submit"
                className="w-full bg-[#272721] text-white py-3 rounded-lg transition-all duration-200 flex items-center justify-center gap-2 group"
              >
                {loading ? (
                  <Loader2 className="animate-spin" size={20} />
                ) : (
                  <>
                    <span>Create Account</span>
                    <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                  </>
                )}
              </button>
            </form>
           
          </motion.div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen w-full flex flex-col lg:flex-row bg-[#EEEEE8]">
      {/* Visual Side - Hidden on mobile, shown on desktop */}
      <div className="relative w-full lg:w-1/2 p-6 sm:p-8 flex items-center justify-center min-h-screen">
        <div className="relative w-full max-w-md mx-auto bg-white p-8 rounded-xl shadow-lg">
          <div className="mb-12">
            <motion.div
              initial={{ scale: 0.8 }}
              animate={{ scale: 1 }}
              className="flex items-center gap-2"
            >
              <Shield className="w-8 h-8" />
              <h1 className="text-3xl font-bold text-gray-800">
                GAIL Signup
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

export default Signup;