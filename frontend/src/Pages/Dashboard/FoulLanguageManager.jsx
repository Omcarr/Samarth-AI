import React, { useState, useEffect } from 'react';
import { 
  Filter as FilterIcon, 
  Trash2 as DeleteIcon, 
  PlusCircle as AddIcon,
  Clock as HistoryIcon
} from 'lucide-react';
import axios from 'axios';

const FoulLanguageManager = () => {
  const [foulWords, setFoulWords] = useState([]);
  const [wordHistory, setWordHistory] = useState([]);
  const [newWord, setNewWord] = useState('');
  const [error, setError] = useState('');

  // Load existing history from localStorage on component mount
  useEffect(() => {
    const savedHistory = JSON.parse(localStorage.getItem('foulLanguageHistory') || '[]');
    setWordHistory(savedHistory);

    const savedWords = JSON.parse(localStorage.getItem('foulWordsList') || '[]');
    setFoulWords(savedWords);
  }, []);

  const handleAddWord = () => {
    // Trim the word and convert to lowercase
    const sanitizedWord = newWord.trim().toLowerCase();

    // Validation checks
    if (!sanitizedWord) {
      setError('Please enter a word');
      return;
    }

    if (foulWords.includes(sanitizedWord)) {
      setError('This word is already in the list');
      return;
    }

    // Prepare new history entry
    const newEntry = {
      word: sanitizedWord,
      addedAt: new Date().toLocaleString(),
      action: 'Added'
    };

    // Update words list
    const updatedWords = [...foulWords, sanitizedWord];
    
    // Update history
    const updatedHistory = [newEntry, ...wordHistory];

    // Update state
    setFoulWords(updatedWords);
    setWordHistory(updatedHistory);
    setNewWord('');
    setError('');

    // Persist to localStorage
    localStorage.setItem('foulWordsList', JSON.stringify(updatedWords));
    localStorage.setItem('foulLanguageHistory', JSON.stringify(updatedHistory));

    // Simulate sending data to backend
    sendToBackend(updatedWords);
  };

  const handleDeleteWord = (wordToDelete) => {
    // Prepare history entry
    const newEntry = {
      word: wordToDelete,
      addedAt: new Date().toLocaleString(),
      action: 'Removed'
    };

    // Update words list
    const updatedWords = foulWords.filter(word => word !== wordToDelete);
    
    // Update history
    const updatedHistory = [newEntry, ...wordHistory];

    // Update state
    setFoulWords(updatedWords);
    setWordHistory(updatedHistory);

    // Persist to localStorage
    localStorage.setItem('foulWordsList', JSON.stringify(updatedWords));
    localStorage.setItem('foulLanguageHistory', JSON.stringify(updatedHistory));

    // Simulate sending updated list to backend
    sendToBackend(updatedWords);
  };

  const sendToBackend = (words) => {
    // Get the last (most recent) word from the input array
    const recentWord = words[words.length - 1];
    
    // Create payload with just the recent word
    const payload = JSON.stringify({ recentWord });
    
    console.log('Sending recent word to backend:', recentWord);
    
    return axios.post(`http://localhost:8080/system_dict?word=${words[words.length - 1]}`, {
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        console.log('Backend response:', response.data);
        return response.data;
    })
    .catch(error => {
        console.error('Error sending to backend:', error);
        throw error;
    });
};
  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleAddWord();
    }
  };

  const clearHistory = () => {
    setWordHistory([]);
    localStorage.removeItem('foulLanguageHistory');
  };

  return (
    <div className="md:-mt-12 bg-gradient-to-br from-gray-50 to-gray-200 min-h-screen flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-2xl bg-white rounded-2xl shadow-2xl overflow-hidden">
        <div className="bg-gradient-to-r from-zinc-800 to-zinc-900 p-6">
          <div className="flex items-center justify-center space-x-3">
            <FilterIcon className="text-white" size={32} />
            <h1 className="text-2xl font-bold text-white">
              Foul Language Filter Management
            </h1>
          </div>
        </div>

        <div className="p-6 space-y-6">
          <div className="flex space-x-2">
            <div className="flex-grow relative">
              <input
                type="text"
                value={newWord}
                onChange={(e) => {
                  setNewWord(e.target.value);
                  setError('');
                }}
                onKeyPress={handleKeyPress}
                placeholder="Enter Word to Filter"
                className={`w-full p-3 border rounded-lg ${
                  error ? 'border-red-500' : 'border-gray-300'
                } focus:outline-none focus:ring-2 focus:ring-zinc-500`}
              />
              {error && (
                <p className="text-red-500 text-sm absolute mt-1">{error}</p>
              )}
            </div>
            <button
              onClick={handleAddWord}
              className="bg-zinc-900 text-white px-4 py-3 rounded-lg hover:bg-zinc-800 flex items-center space-x-2 transition-colors"
            >
              <AddIcon size={20} />
              <span>Add</span>
            </button>
          </div>

         
          {/* Word History */}
          <div className="border rounded-lg">
            <div className="flex justify-between items-center p-4 border-b">
              <div className="flex items-center space-x-2">
                <HistoryIcon className="text-gray-600" />
                <h2 className="text-lg font-semibold text-gray-700">
                  Word Management History
                </h2>
              </div>
              {wordHistory.length > 0 && (
                <button
                  onClick={clearHistory}
                  className="text-sm text-red-500 hover:text-red-700 transition-colors"
                >
                  Clear History
                </button>
              )}
            </div>

            {wordHistory.length > 0 ? (
              <table className="w-full">
                <thead>
                  <tr className="border-b bg-gray-100">
                    <th className="p-3 text-left">Word</th>
                    <th className="p-3">Action</th>
                    <th className="p-3 text-right">Timestamp</th>
                  </tr>
                </thead>
                <tbody>
                  {wordHistory.map((entry, index) => (
                    <tr key={index} className="border-b last:border-b-0">
                      <td className="p-3">
                        <span className={`
                          px-2 py-1 rounded-full text-xs
                          ${entry.action === 'Added' 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-red-100 text-red-800'
                          }
                        `}>
                          {entry.word}
                        </span>
                      </td>
                      <td className="p-3 text-center">
                        <span className={`
                          ${entry.action === 'Added' 
                            ? 'text-green-600' 
                            : 'text-red-600'
                          }
                        `}>
                          {entry.action}
                        </span>
                      </td>
                      <td className="p-3 text-right text-gray-500 text-sm">
                        {entry.addedAt}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="p-4 text-center text-gray-500">
                No history available. Start adding or removing words to track changes.
              </div>
            )}
          </div>
        </div>
      </div>

      <p className="mt-4 text-sm text-center text-gray-600 max-w-2xl">
        This tool helps manage and track filtered words. All modifications are securely logged and can be sent to your backend system.
      </p>
    </div>
  );
};

export default FoulLanguageManager;