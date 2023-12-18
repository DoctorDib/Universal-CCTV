
import { useState, useEffect, useContext, } from 'react';
import { FaEye } from 'react-icons/fa';

import VideoList from './Components/VideoList';
import LiveFeed from './Components/LiveFeed';

import './App.scss';

import ConfigContext from './Helpers/ConfigContext';
import { SocketContext } from './Helpers/SocketContext';
import VideoPlayer from './Components/VideoPlayer';

const App = () => {    
    const [selectedVideo, setSelectedVideo] = useState<string | null>(null);
    const [ip, setIp] = useState<string>("");
    const { config, fetchData } = useContext(ConfigContext);
    const { clientCount } = useContext(SocketContext);

    useEffect(() => { 
        if (config !== null) {
            setIp(`http://${config.ip}:${config.port}/`);
        }
    }, [config]);

    useEffect(() => { fetchData(); }, []);

    return (
        <div className={'app-container'}>
            <div className={'container'}>
                <div className={'information'}>
                    <div className={'viewer'}> 
                        <FaEye/>
                        <div> { clientCount } </div>
                    </div>
                    <div className={'title'}> {selectedVideo} </div>
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