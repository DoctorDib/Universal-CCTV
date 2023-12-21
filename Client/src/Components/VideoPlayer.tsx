import { useContext, useEffect, useRef, useState } from "react";
import JMuxer from "jmuxer";
import { BsRewindFill, BsFillFastForwardFill , } from "react-icons/bs";
import { BiReset, BiStar } from "react-icons/bi";

import './VideoPlayer.scss';

import ConfigContext from "../Helpers/ConfigContext";
import { BuildUrl } from "../Helpers/helper";

interface VideoPlayerInterface {
    selectedVideo: string | null,
}

enum ViewerFormat {
    jpeg = 'jpeg',
    mp4 = 'mp4',
    h264 = 'h264',
}

const VideoPlayer = ({ selectedVideo }: VideoPlayerInterface) => {
    const [playbackRate, setPlaybackRate] = useState<number>(0);
    const [videoUrl, setVideoUrl] = useState<string>("");
    const [key, setKey] = useState<number>(0); // Add key state
    const [format, setFormat] = useState<ViewerFormat>();
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
    const OnSaveJob = () => {
        if (playbackRate < 0.25) {
            setPlaybackRate(0.25);
        } else {
            setPlaybackRate(playbackRate - 0.25);
        }

        // Fetch('/save/video/')
    };

    useEffect(() => {
        
        console.log(videoPlayer);

        if (videoPlayer !== null && videoPlayer.current !== null) {
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

            if (selectedVideo.includes(ViewerFormat.mp4)) {
                setFormat(ViewerFormat.mp4);
            } else if (selectedVideo.includes(ViewerFormat.jpeg)) {
                setFormat(ViewerFormat.jpeg);
            } else if (selectedVideo.includes(ViewerFormat.h264)) {
                setFormat(ViewerFormat.h264);
            }

            const additionUrl: string = selectedVideo.includes(ViewerFormat.jpeg) ? 'get/snapshot' :  'video';
            const url: string = BuildUrl(config, `/${additionUrl}/${selectedVideo}`);
            setVideoUrl(url);
            // Increment key to force remount of the video element
            setKey((prevKey) => prevKey + 1);
        };

        TriggerVideo();
    }, [selectedVideo]);

    useEffect(() => { fetchData(); }, []);

    return (
        <div>
            <div className={'video-display-container'}>
                {format === ViewerFormat.mp4 ? (
                    <video key={key} className={'video-display'} controls ref={videoPlayer}>
                        <source src={videoUrl} type='video/mp4'/>
                        Your browser does not support the video tag.
                    </video>
                ) : format === ViewerFormat.h264 ? (
                    <H246VideoPlayer key={key} url={videoUrl} videoReference={videoPlayer}/>
                ) : (
                    <img src={videoUrl} className={'video-display'} ref={videoPlayer} alt="Snapshot"/>
                )}
            </div>

            <div className={'speed-control-container'}>
                <div className={'playback-rate'}> { playbackRate } </div>
                <div className={'speed-control-buttons'}>
                    <button title={'Decrease Speed'} onClick={() => onDecreasePlayRate()}> <BsRewindFill/> </button>
                    <button title={'Default Speed'} onClick={() => onResetPlayRate()}> <BiReset/> </button>
                    <button title={'Increase Speed'} onClick={() => onIncreasePlayRate()}> <BsFillFastForwardFill /> </button>
                    <button title={'Save Video'} onClick={() => OnSaveJob()}> <BiStar /> </button>
                </div>
            </div>
        </div>
    );
};

export default VideoPlayer;

interface VideoEnumInterface {
    url: string,
    videoReference: any
}

const H246VideoPlayer = ({ url, videoReference }: VideoEnumInterface) => {
    useEffect(() => {
        console.log(url)
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
    }, [url]);

    return (
        <video id="h264Stream" className={'video-display'} controls ref={videoReference}></video>
    );
};