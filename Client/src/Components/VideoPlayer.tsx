import { useContext, useEffect, useRef, useState } from "react";
import JMuxer from "jmuxer";
import { BsRewindFill, BsFillFastForwardFill , } from "react-icons/bs";
import { BiReset } from "react-icons/bi";

import './VideoPlayer.scss';

import ConfigContext from "../Helpers/ConfigContext";
import { BuildUrl } from "../Helpers/helper";

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
        };

        TriggerVideo();
    }, [selectedVideo]);

    useEffect(() => { 
        fetchData();
    }, []);

    return (
        <div>
            <div className={'video-display-container'}>
                {isMp4 ? (
                    <video key={key} className={'video-display'} controls ref={videoPlayer}>
                        <source src={videoUrl} type='video/mp4'/>
                        Your browser does not support the video tag.
                    </video>
                ) : (
                    <video key={key} id="h264Stream" className={'video-display'} controls ref={videoPlayer}>
                        <source src={videoUrl}/>
                        Your browser does not support the video tag.
                    </video>
                )}
            </div>

            <div className={'speed-control-container'}>
                <div className={'playback-rate'}> { playbackRate } </div>
                <div className={'speed-control-buttons'}>
                    <button onClick={() => onDecreasePlayRate()}> <BsRewindFill/> </button>
                    <button onClick={() => onResetPlayRate()}> <BiReset/> </button>
                    <button onClick={() => onIncreasePlayRate()}> <BsFillFastForwardFill /> </button>
                </div>
            </div>
        </div>
    );
};

export default VideoPlayer;