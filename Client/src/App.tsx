
import { useState, useEffect, useContext, } from 'react';
import { FaEye } from 'react-icons/fa';

import VideoList from './Components/VideoList';
import LiveFeed from './Components/LiveFeed';

import './App.scss';

import ConfigContext from './Helpers/ConfigContext';
import { SocketContext } from './Helpers/SocketContext';
import VideoPlayer from './Components/VideoPlayer';
import { FileInfo } from './Resources/interfaces';

const App = () => {    
    const [selectedVideo, setSelectedVideo] = useState<FileInfo | null>(null);
    const [ip, setIp] = useState<string>("");
    const { config, fetchData } = useContext(ConfigContext);
    const { clientCount, savedVideoFiles, videoFiles } = useContext(SocketContext);

    useEffect(() => { 
        if (config !== null) {
            setIp(`http://${config.ip}:${config.port}/`);
        }
    }, [config]);

    useEffect(() => {
        if (selectedVideo === null) {
            // Ignore this function if no video has been selected
            return;
        }

        const maxLength = Math.max(videoFiles.length, savedVideoFiles.length);

        let foundVideo = false;

        for (let i = 0; i < maxLength; i++) {
            const obj1 = videoFiles[i];
            const obj2 = savedVideoFiles[i];
          
            if (obj1) {
                if (obj1.uid === selectedVideo.uid) {
                    setSelectedVideo(obj1);
                    foundVideo = true;
                    break;
                }
            }
          
            if (obj2) {
                if (obj2.uid === selectedVideo.uid) {
                    setSelectedVideo(obj2);
                    foundVideo = true;
                    break;
                }
            }
        }
    }, [videoFiles, savedVideoFiles])

    useEffect(() => { fetchData(); }, []);

    return (
        <div className={'app-container'}>
            <div className={'container'}>
                <div className={'information'}>
                    <div className={'viewer'}> 
                        <FaEye/>
                        <div> { clientCount } </div>
                    </div>
                    <div className={'title'}> {selectedVideo?.display_name} </div>
                </div>

                {
                    selectedVideo === null
                    ? <LiveFeed ShowControl/> 
                    : <VideoPlayer selectedVideo={selectedVideo}/>
                }
            </div>

            {/* <SnapshotList/> */}

            <div className={'side-bar'}>
                <VideoList selectedVideo={selectedVideo} setSelectedVideo={setSelectedVideo}/>
                <div>
                    10
                </div>
            </div>
        </div>
    );
};

export default App;