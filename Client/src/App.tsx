
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
            // if (selectedVideo == null) {
            //     return;
            // }
    
            const url: string = BuildUrl(config, `/video/${selectedVideo}`);

            // const url = "http://192.168.0.14:3000/test2.mp4"

            // const response = await fetch(url, {
            //     method: 'GET',
            //     mode: 'cors', // Specify CORS mode
            //     headers: {
            //         'Content-Type': 'video/mp4', // Adjust content type as needed
            //         // Add any other headers as needed for your server
            //     },
            //   });
      
            // if (!response.ok) {
            //     throw new Error(`HTTP error! Status: ${response.status}`);
            // }

            // const videoBlob = await response.blob();
            // console.log('Video Blob:', videoBlob);

            // const turl = URL.createObjectURL(videoBlob);
            // console.log('Video URL:', turl);

            // setVideoUrl(turl);

            setVideoUrl(url);
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
            <video id="samp" width="640" height="480" controls>
                <source src='/test.mp4' type="video/mp4"/>
                Your browser does not support this video format.
            </video>

            <div className={'container'}>
                <div className={'title'}> {ip} </div>
                <div className={'title'}> {selectedVideo} </div>
                { selectedVideo == null 
                    ? <LiveFeed ShowControl/> 
                    : <video className={'video-player'} controls> <source src={videoUrl} type='video/mp4'/> Your browser does not support the video tag. </video> }
            </div>

            <video width="640" height="360" controls>
                <source src={"http://192.168.0.14:5000/test2.mp4"} type="video/mp4"/>
                Your browser does not support the video tag.
            </video>


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