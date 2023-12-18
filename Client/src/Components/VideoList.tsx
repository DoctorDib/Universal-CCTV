
import { useState, useEffect, useContext } from 'react';
import { AiOutlineEye } from "react-icons/ai";

import './VideoList.scss';
import LiveFeed from './LiveFeed';
import StorageController from './StorageController';
import { BuildUrl, } from '../Helpers/helper';
import ConfigContext from '../Helpers/ConfigContext';
import { SocketContext } from '../Helpers/SocketContext';
import VideoButtonComponent from './VideoButton';

interface VideoList {
    setSelectedVideo: (filename: string | null) => void,
    selectedVideo: string | null,
}

const App = ({ setSelectedVideo, selectedVideo }: VideoList) => {
    const [videoList, setVideoList] = useState<Array<string>>([]); // Set an initial value
    const [previewSelection, setPreviewSelection] = useState<string | null>(null);
    const [imageUrl, setImageUrl] = useState<string>("");
    const { config } = useContext(ConfigContext);
    const { videoFiles } = useContext(SocketContext);

    useEffect(() => {
        setVideoList(videoFiles);
    }, [videoFiles])

    useEffect(() => {
        const getUrl = () => {
            if (previewSelection === null) {
                return;
            }

            setImageUrl(BuildUrl(config, `/get/thumbnail/${previewSelection}`));
        }
        getUrl();
    }, [previewSelection]);

    return (
        <div className={'video-list-container'}>
            <div className={'storage-display'}>
                <StorageController/>
            </div>

            <div>
                {
                    selectedVideo == null 
                        ? <div className={'camera-preview'}>
                            <div className={'interactive'} onClick={() => setSelectedVideo(previewSelection)}
                                style={{ display: previewSelection !== null ? 'flex' : 'none'}}> 
                                <AiOutlineEye className={'display-eye'}/>
                            </div>
                            <img src={imageUrl} className={'camera-display'}/>

                        </div>
                        : <div onClick={()=>setSelectedVideo(null)}> 
                            <LiveFeed ShowControl={false}/> 
                        </div>
                }
            </div>

            <div className={'list-container'}>
                <VideoButtonComponent data={videoList} selectedVideo={previewSelection} setSelectedVideo={setPreviewSelection} />
            </div>
        </div>
    );
}

export default App;