import { useState, useCallback, useEffect, useRef } from 'react';

export const useWebSocket = ({ url }) => {
  const [socket, setSocket] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [response, setResponse] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [responseTime, setResponseTime] = useState(0);

  const startTimeRef = useRef(null);
  const timerRef = useRef(null);

  const connect = useCallback(() => {
    const ws = new WebSocket(url);

    ws.onopen = () => {
      setIsConnected(true);
      setResponse('');

      // Retrieve token from localStorage

    };

    ws.onclose = () => {
      setIsConnected(false);
    };

    ws.onmessage = (event) => {

      if (!startTimeRef.current) {
        startTimeRef.current = Date.now();

        timerRef.current = setInterval(() => {
          if (startTimeRef.current) {
            const currentTime = Date.now();
            setResponseTime((currentTime - startTimeRef.current) / 1000);
          }
        }, 100);
      }

      setResponse((prev) => prev + event.data);
    };

    setSocket(ws);

    return ws;
  }, [url]);

  useEffect(() => {
    const ws = connect();

    // Cleanup on unmount
    return () => {
      ws.close();
    };
  }, [connect]);

  const sendMessage = useCallback(
    (message) => {
      if (socket && socket.readyState === WebSocket.OPEN) {
        // Reset everything before sending
        setIsLoading(true);
        setResponse('');
        startTimeRef.current = null;
        setResponseTime(0);

        // Stop any existing timer
        if (timerRef.current) {
          clearInterval(timerRef.current);
          timerRef.current = null;
        }

        socket.send(message);
      }
    },
    [socket]
  );

  // Effect to stop timer when response is complete
  useEffect(() => {
    // Stop timer and calculate final time when response is complete
    if (!isLoading && response !== '' && startTimeRef.current) {
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }

      const endTime = Date.now();
      setResponseTime((endTime - startTimeRef.current) / 1000);
    }
  }, [isLoading, response]);

  return {
    sendMessage,
    response,
    isConnected,
    isLoading,
    responseTime,
    reset: () => {
      setResponse('');
      setResponseTime(0);
      startTimeRef.current = null;
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    },
  };
};