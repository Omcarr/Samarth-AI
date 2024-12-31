import { Moon, Sun } from 'lucide-react'
import { useTheme } from '/src/Context/ThemeContext.jsx';


function ThemeT() {
const { theme, toggleTheme } = useTheme();

  return (
   <>
   <div className="fixed top-4 right-4 z-50">
      {theme === 'dark' ? 
        <Sun 
          onClick={toggleTheme} 
          className="cursor-pointer text-white  hover:text-yellow-500 transition-colors"
        /> : 
        <Moon 
          onClick={toggleTheme} 
          className="cursor-pointer hover:text-indigo-500 transition-colors"
        />
      }
    </div>
   
  
   
   </>
  )
}

export default ThemeT
