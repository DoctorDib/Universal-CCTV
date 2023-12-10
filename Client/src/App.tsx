
import { useState, useEffect, useContext, useRef } from 'react';
import JMuxer from 'jmuxer';

import VideoList from './Components/VideoList';
import LiveFeed from './Components/LiveFeed';
import SnapshotList from './Components/SnapshotList';

import './App.scss';

import { BuildUrl } from './Helpers/helper';
import ConfigContext from './Helpers/ConfigContext';
import { SocketContext } from './Helpers/SocketContext';

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
                <div className={'title'}> {ip} </div>
                <div className={'title'}> {selectedVideo} </div>

                <div className={'title'}> {clientCount} </div>

                {
                    selectedVideo === null
                    ? <LiveFeed ShowControl/> 
                    : <VideoPlayer selectedVideo={selectedVideo}/>
                }
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
};

export default App;

interface VideoPlayerInterface {
    selectedVideo: string | null,
}

const VideoPlayer = ({ selectedVideo }: VideoPlayerInterface) => {
    const [playbackRate, setPlaybackRate] = useState<number>(0);
    const [videoUrl, setVideoUrl] = useState<string>("");
    const [isMp4, setIsMp4] = useState<boolean>(false);
    const [key, setKey] = useState<number>(0); // Add key state
    const videoPlayer = useRef(null);
    const { config, fetchData } = useContext(ConfigContext);

    const onIncreasePlayRate = () => {
        if (playbackRate > 4) {
            setPlaybackRate(4);
        } else {
            setPlaybackRate(playbackRate + 0.25);
        }

    };
    const onResetPlayRate = () => setPlaybackRate(1);
    const onDecreasePlayRate = () => {
        if (playbackRate < 0.25) {
            setPlaybackRate(0.25);
        } else {
            setPlaybackRate(playbackRate - 0.25);
        }
    };

    useEffect(() => {
        if (videoPlayer !== null) {
            videoPlayer.current.playbackRate = playbackRate;
        }
    }, [playbackRate]);

    useEffect(() => {
        const TriggerVideo = async () => {
            if (selectedVideo === null) {
                return;
            }

            // Resetting playback rate to default
            setPlaybackRate(1);

            var isMp4Format: boolean = selectedVideo.includes('.mp4');
            setIsMp4(isMp4Format);

            const url: string = BuildUrl(config, `/video/${selectedVideo}`);

            if (isMp4Format) {
                setVideoUrl(url);
            } else {
                // Raspberry Pi
                const jmuxer = new JMuxer({
                    node: 'h264Stream',
                    mode: 'video',
                    debug: false,
                    fps: 24,
                });
        
                fetch(url).then(async (response) => {
                    jmuxer.feed({
                        video: new Uint8Array(await response.arrayBuffer()),
                    });
                });
            }

            // Increment key to force remount of the video element
            setKey((prevKey) => prevKey + 1);
        }

        TriggerVideo();
    }, [selectedVideo]);

    useEffect(() => { 
        fetchData();
    }, []);

    return (
        <div>
            {isMp4 ? (
                <video key={key} className={'video-player'} controls ref={videoPlayer}>
                    <source src={videoUrl} type='video/mp4'/>
                    Your browser does not support the video tag.
                </video>
            ) : (
                <video key={key} id="h264Stream" className={'video-player'} controls ref={videoPlayer}>
                    <source src={videoUrl}/>
                    Your browser does not support the video tag.
                </video>
            )}

            <button onClick={() => onIncreasePlayRate()}> + </button>
            <button onClick={() => onResetPlayRate()}> * </button>
            <button onClick={() => onDecreasePlayRate()}> - </button>
        </div>
    );
};