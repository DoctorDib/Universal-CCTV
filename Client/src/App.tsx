
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
    const { config, fetchData } = useContext(ConfigContext);

    useEffect(() => {
        const test = async () => {
            if (selectedVideo == null) {
                return;
            }
    
            const jmuxer = new JMuxer({
                node: 'h264Stream',
                mode: 'video',
                debug: false,
                fps: fps,
            });
    
            const url: string = BuildUrl(config, `/video/${selectedVideo}`);

            fetch(url).then(async (response) => {
                jmuxer.feed({
                    video: new Uint8Array(await response.arrayBuffer()),
                });      
            });
        }

        test();
    }, [selectedVideo]);

    useEffect(() => { fetchData(); }, []);

    return (
        <div className={'app-container'}>
            <div className={'container'}>
                <div className={'title'}> {selectedVideo} </div>
                { selectedVideo == null 
                    ? <LiveFeed ShowControl/> 
                    : <video id="h264Stream" className={'video-player'} controls></video> }
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