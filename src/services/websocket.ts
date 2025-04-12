class WebSocketService {
  private ws: WebSocket | null = null;
  private static instance: WebSocketService;
  private callbacks: { [key: string]: (data: any) => void } = {};

  private constructor() {}

  static getInstance(): WebSocketService {
    if (!WebSocketService.instance) {
      WebSocketService.instance = new WebSocketService();
    }
    return WebSocketService.instance;
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.ws = new WebSocket('ws://localhost:9083');
      
      this.ws.onopen = () => {
        console.log('WebSocket Connected');
        resolve();
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket Error:', error);
        reject(error);
      };

      this.ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        Object.values(this.callbacks).forEach(callback => callback(data));
      };

      this.ws.onclose = () => {
        console.log('WebSocket Closed');
      };
    });
  }

  sendMessage(message: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.error('WebSocket is not connected');
    }
  }

  addMessageListener(id: string, callback: (data: any) => void) {
    this.callbacks[id] = callback;
  }

  removeMessageListener(id: string) {
    delete this.callbacks[id];
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

export const websocketService = WebSocketService.getInstance(); 