import ChatHistory from "../components/ChatHistory"
import GeminiPage from "../components/Gemini"
import Modes from "../components/Modes"
import Dashboard from "../Pages/Dashboard/Dashboard"
import Home from "../Pages/Home"

function Protected({path}) {
    const tvar = localStorage.getItem('token')
    const redirect_path = ()=>{
        if(tvar == undefined || tvar == null){
           window.location.href = '/'
        }
        else if(path == 'home'){
            return <Home/>
        }
        else if(path == 'chat_history'){
            return <ChatHistory />
        }
        else if(path == 'modes/Documentprocessing'){
            return <Modes />
        }
        else if(path == 'modes/genericpolicy'){
            return <Modes />
        }
        else if(path == 'modes/Projectquestion'){
            return <Modes />
        }
        else if(path == 'admin'){
            return <Dashboard />
        }
        else if(path == 'main'){
            return <GeminiPage />
        }
    }
    
  return (
    <div>

        {redirect_path()}
      
    </div>
  )
}

export default Protected
