import React, {
    createContext,
    useContext,
    useEffect,
    useState,
    ReactNode,
} from 'react';

import { io, Socket } from 'socket.io-client';
import ConfigContext from './ConfigContext';
  
interface SocketContextProps {
    children: ReactNode;
}
  
interface SocketContextValue {
    socket: Socket | null;
    clientCount: number;
    isStreaming: boolean;
    isRecording: boolean;
    controlLockState: boolean;

    servoPosition: number;
    storageUsed: number;
    videoFiles: Array<string>;
    screenshotFiles: Array<string>;

    doAction: (actionName: string) => void;
}
  
export const SocketContext = createContext<SocketContextValue | undefined>(undefined);

export const SocketProvider: React.FC<SocketContextProps> = ({ children }) => {
    const [socket, setSocket] = useState<Socket | null>(null);
    const [clientCount, setClientCount] = useState<number>(0);
    const [isStreaming, setIsStreaming] = useState<boolean>(false);
    const [isRecording, setIsRecording] = useState<boolean>(false);
    const [servoPosition, setServoPosition] = useState<number>(0);
    const [storageUsed, setStorageUsed] = useState<number>(0);
    const [videoFiles, setVideoFiles] = useState<Array<string>>([]);
    const [controlLockState, setControlLockState] = useState<boolean>(false);
    const [screenshotFiles, setScreenshotFiles] = useState<Array<string>>([]);
    const { config } = useContext(ConfigContext);

    const doAction = (actionName: string) => {
        // Check if socket is not null before calling emit
        if (socket) {
            socket.emit('action', actionName);
        }
    };

    useEffect(() => {
        if (config == null) {
            return;
        }

        const newSocket = io(`http://${config.ip}:${config.port}`);

        newSocket.connect();
        setSocket(newSocket);

        newSocket.on('welcome_package', (data: any): void => {
            console.log(data)
            setClientCount(data.clients_count);
            setIsStreaming(data.is_streaming);
            setIsRecording(data.is_recording);
            setServoPosition(data.servo_position);
            setStorageUsed(data.storage_used);
            setVideoFiles(data.video_files);
            setScreenshotFiles(data.snapshot_files);
            setControlLockState(data.control_lock_state);
        });

        newSocket.on('is_recording', (data: boolean): void => setIsRecording(data));
        newSocket.on('is_streaming', (data: boolean): void => setIsStreaming(data));
        newSocket.on('servo_position', (data: number): void => setServoPosition(data)); 
        newSocket.on('storage_used', (data: number): void => setStorageUsed(data)); 
        newSocket.on('video_files', (data: Array<string>): void => setVideoFiles(data)); 
        newSocket.on('snapshot_files', (data: Array<string>): void => setScreenshotFiles(data)); 
        newSocket.on('control_lock_state', (data: boolean): void => setControlLockState(data));
        
        // Clean up the socket connection on component unmount
        return (): void => { newSocket.disconnect(); };
    }, [config]);

    return <SocketContext.Provider value={{ 
        socket, clientCount, isStreaming, isRecording, 
        servoPosition, storageUsed, videoFiles, screenshotFiles, controlLockState,
        doAction 
    }}> {children} </SocketContext.Provider>
};

export const useSocket = () => {
    const context = useContext(SocketContext);

    if (!context) {
        throw new Error('useSocket must be used within a SocketProvider');
    }

    return context;
};