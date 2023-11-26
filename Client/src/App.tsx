
import { useState, useEffect } from 'react';
import JMuxer from 'jmuxer';

import VideoList from './Components/VideoList';
import LiveFeed from './Components/LiveFeed';
import SnapshotList from './Components/SnapshotList';

import './App.scss';

import { BuildUrl } from './Helpers/helper';

const App = () => {    
    const [selectedVideo, setSelectedVideo] = useState<string | null>(null);

    useEffect(() => {
        if (selectedVideo == null) {
            return;
        }

        const jmuxer = new JMuxer({
            node: 'h264Stream',
            mode: 'video',
            debug: false,
            fps: 20,
        });

        // const streamUrl = 'http://192.168.0.21:5000/video/2023-11-19_23-42-11.h264';
        // const streamUrl = 'http://192.168.0.21:5000/video/' + selectedVideo;
        const streamUrl = BuildUrl(`video/${selectedVideo}`);

        fetch(streamUrl)
            .then(async (response) => {
                jmuxer.feed({
                    video: new Uint8Array(await response.arrayBuffer()),
                });      
            });
    }, [selectedVideo]);

    return (
        <div className={'app-container'}>
            <div className={'container'}>
                <div className={'title'}> {selectedVideo} </div>
                { selectedVideo == null 
                    ? <LiveFeed ShowControl/> 
                    : <video id="h264Stream" className={'video-player'} controls></video> }
            </div>

            
            <SnapshotList/>

            <div className={'side-bar'}>
                <VideoList selectedVideo={selectedVideo} setSelectedVideo={setSelectedVideo}/>
            </div>
        </div>
    );
}

export default App;