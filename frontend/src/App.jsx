import { RouterProvider, createBrowserRouter } from "react-router-dom";
import LoginSignupForm from "./Pages/LoginSignup";
import { ThemeProvider } from "./Context/ThemeContext";
import Dashboard from "./Pages/Dashboard/Dashboard";
import ChatHistory from "./components/ChatHistory";
import Protected from "./Backend/Protected";
import GeminiPage from "./components/Gemini";
import Modes from "./components/Modes";
import Sidebar from "./components/Sidebar";
import Signup from "./Pages/signup";



const router = createBrowserRouter([
  {
    path: "/",
    element: <LoginSignupForm />, 
  },
  {
    path: "/home",
    element: <Protected path={'home'} />,
  },
  {
    path: "/chat_history",
    element:  <Protected path={'chat_history'} />,
  },
  {
    path: "/modes/Documentprocessing",
    element: <Protected path={'modes/Documentprocessing'} />,
  },
  {
    path: "/modes/genericpolicy",
    element: <Protected path={'modes/genericpolicy'} />,
  },
  {
    path: "/modes/Projectquestion",
    element: <Protected path={'modes/Projectquestion'} />,
  },
  {
    path: "/admin",
    element: <Protected path={'admin'} />,
  },
  {
    path: "/login_signup",
    element: <LoginSignupForm />,
  },
  {
    path: "/signup",
    element: <Signup />,
  },
  {
    path: "/main",
    element: <Protected path={'main'} />,
  },
]);


function App() {

  return (
    <>
    <ThemeProvider>
      <RouterProvider router={router} />
      </ThemeProvider>
    </>
  )
}

export default App
