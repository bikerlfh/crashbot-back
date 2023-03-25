import WebSocket from 'ws';

import { WEB_SOCKET_URL } from '../constants';

export class WebSocketClient {
    private static instance: WebSocketClient;
    private socket: WebSocket | any;
    private connectedPromise: Promise<void>;

    private constructor() {
        this.socket = new WebSocket(WEB_SOCKET_URL);
        this.connectedPromise = new Promise((resolve) => {
            this.socket.addEventListener('open', () => {
                console.log('WebSocket connection established');
                resolve();
            });
        });
        this.socket.onclose = this.onClose.bind(this);
        this.socket.onerror = this.onError.bind(this);
        // this.socket.onmessage = this.onMessage.bind(this);
        this.setOnMessage(this.onMessage.bind(this));
    }

    public static async getInstance(): Promise<WebSocketClient> {
        if (!WebSocketClient.instance) {
            WebSocketClient.instance = new WebSocketClient();
            await WebSocketClient.instance.connect();
        }
        return WebSocketClient.instance;
    }

    async connect(): Promise<void> {
        await this.connectedPromise;
    }

    setOnMessage(onMessage: (event: MessageEvent) => void) {
        this.socket.onmessage = onMessage;
    }

    private onOpen(event: Event): void {
        console.log('WebSocket connection established');
    }

    private onClose(event: CloseEvent): void {
        console.log('WebSocket connection closed');
        console.log('connnecting to WebSocket....');
        WebSocketClient.instance.connect().then(() => {}).catch((error) => {
            console.error('Error reconnecting to WebSocket', error);
        });
        
    }

    private onError(event: ErrorEvent): void {
        console.error('WebSocket error:', event);
    }

    private onMessage(event: MessageEvent): void {
        console.log('WebSocket message received:', event.data);
    }

    public send(message: any): void {
        this.socket.send(message);
    }

    public close(): void {
        this.socket.close();
    }
}