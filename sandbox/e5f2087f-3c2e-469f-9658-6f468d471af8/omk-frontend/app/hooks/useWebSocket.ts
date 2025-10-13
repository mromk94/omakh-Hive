/**
 * WebSocket hooks for real-time admin dashboard updates
 * Replaces HTTP polling with true real-time WebSocket connections
 */
import { useEffect, useState, useRef, useCallback } from 'react';
import { toast } from 'react-hot-toast';

interface WebSocketHookOptions {
  url: string;
  onMessage?: (data: any) => void;
  onError?: (error: Event) => void;
  onOpen?: () => void;
  onClose?: () => void;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

export function useWebSocket(options: WebSocketHookOptions) {
  const {
    url,
    onMessage,
    onError,
    onOpen,
    onClose,
    reconnectInterval = 3000,
    maxReconnectAttempts = 5,
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<any>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const connect = useCallback(() => {
    try {
      // Close existing connection if any
      if (wsRef.current) {
        wsRef.current.close();
      }

      const ws = new WebSocket(url);

      ws.onopen = () => {
        console.log(`✅ WebSocket connected: ${url}`);
        setIsConnected(true);
        reconnectAttemptsRef.current = 0;
        onOpen?.();
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setLastMessage(data);
          onMessage?.(data);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        onError?.(error);
      };

      ws.onclose = () => {
        console.log(`❌ WebSocket disconnected: ${url}`);
        setIsConnected(false);
        onClose?.();

        // Attempt to reconnect
        if (reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current++;
          console.log(`🔄 Reconnecting... (Attempt ${reconnectAttemptsRef.current}/${maxReconnectAttempts})`);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, reconnectInterval);
        } else {
          console.error('❌ Max reconnect attempts reached');
          toast.error('Lost connection to server. Please refresh the page.');
        }
      };

      wsRef.current = ws;
    } catch (error) {
      console.error('Failed to create WebSocket:', error);
    }
  }, [url, onMessage, onError, onOpen, onClose, reconnectInterval, maxReconnectAttempts]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  const send = useCallback((data: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    } else {
      console.warn('WebSocket is not connected. Cannot send message.');
    }
  }, []);

  useEffect(() => {
    connect();

    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    isConnected,
    lastMessage,
    send,
    disconnect,
    reconnect: connect,
  };
}

/**
 * Hook for Hive Intelligence WebSocket
 */
export function useHiveWebSocket(onUpdate: (data: any) => void) {
  const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'ws://localhost:8001';
  const wsUrl = `${BACKEND_URL.replace('http', 'ws')}/ws/admin/hive`;

  return useWebSocket({
    url: wsUrl,
    onMessage: (message) => {
      if (message.type === 'hive_update') {
        onUpdate(message.data);
      }
    },
    onOpen: () => {
      console.log('🐝 Connected to Hive Intelligence stream');
    },
    onClose: () => {
      console.log('🐝 Disconnected from Hive Intelligence stream');
    },
  });
}

/**
 * Hook for Analytics WebSocket
 */
export function useAnalyticsWebSocket(onUpdate: (data: any) => void) {
  const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'ws://localhost:8001';
  const wsUrl = `${BACKEND_URL.replace('http', 'ws')}/ws/admin/analytics`;

  return useWebSocket({
    url: wsUrl,
    onMessage: (message) => {
      if (message.type === 'analytics_update') {
        onUpdate(message.data);
      }
    },
    onOpen: () => {
      console.log('📊 Connected to Analytics stream');
    },
    onClose: () => {
      console.log('📊 Disconnected from Analytics stream');
    },
  });
}

/**
 * Hook for Bee Monitor WebSocket
 */
export function useBeeWebSocket(onUpdate: (data: any) => void) {
  const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'ws://localhost:8001';
  const wsUrl = `${BACKEND_URL.replace('http', 'ws')}/ws/admin/bees`;

  return useWebSocket({
    url: wsUrl,
    onMessage: (message) => {
      if (message.type === 'bee_update') {
        onUpdate(message.data);
      }
    },
    onOpen: () => {
      console.log('🐝 Connected to Bee Monitor stream');
    },
    onClose: () => {
      console.log('🐝 Disconnected from Bee Monitor stream');
    },
  });
}
