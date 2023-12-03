
import { useState, useEffect, useContext } from 'react';
import JMuxer from 'jmuxer';

import VideoList from './Components/VideoList';
import LiveFeed from './Components/LiveFeed';
import SnapshotList from './Components/SnapshotList';

import './App.scss';

import { BuildUrl } from './Helpers/helper';
import ConfigContext from './Helpers/ConfigContext';

const App = () => {    
    const [selectedVideo, setSelectedVideo] = useState<string | null>(null);
    const [fps, setFps] = useState<number>(20);
    const [videoUrl, setVideoUrl] = useState<string>("");
    const [ip, setIp] = useState<string>("");
    const { config, fetchData } = useContext(ConfigContext);

    useEffect(() => {
        const test = async () => {
            if (selectedVideo == null) {
                return;
            }
    
            // const jmuxer = new JMuxer({
            //     node: 'h264Stream',
            //     mode: 'video',
            //     debug: false,
            //     fps: fps,
            // });
    
            const url: string = BuildUrl(config, `/video/${selectedVideo}`);

            const response = await fetch(url, {
                method: 'GET',
              });
      
            if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
            }

            var blob = await response.blob();
            console.log(blob);

            setVideoUrl(URL.createObjectURL(blob));
        }

        test();
    }, [selectedVideo]);

    useEffect(() => { 
        if (config !== null) {
            setIp(`http://${config.ip}:${config.port}/`);
        }
    }, [config]);

    useEffect(() => { fetchData(); }, []);

    return (
        <div className={'app-container'}>
            <div className={'container'}>
                <div className={'title'}> {ip} </div>
                <div className={'title'}> {selectedVideo} </div>
                { selectedVideo == null 
                    ? <LiveFeed ShowControl/> 
                    : <video className={'video-player'} controls> <source src={videoUrl} type='video/mp4'/> Your browser does not support the video tag. </video> }
            </div>

            <div className={'fps-slider-container'}>
                <div> {fps} </div>
                <input type="range" min="5" max="120" value={fps} onChange={(event) => setFps(Number(event.target.value))} className={'slider'} />
            </div>

            <SnapshotList/>

            <div className={'side-bar'}>
                <VideoList selectedVideo={selectedVideo} setSelectedVideo={setSelectedVideo}/>
                <div>
                    10
                </div>
            </div>
        </div>
    );
}

export default App;