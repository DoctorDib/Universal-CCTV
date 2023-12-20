
import { useState, useEffect, useContext, ReactComponentElement } from 'react';
import { AiOutlineEye, AiOutlinePicture  } from "react-icons/ai";
import { TfiVideoClapper } from "react-icons/tfi";
import { FaRegStar } from "react-icons/fa";

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

enum ListNavigation {
    Videos = "Videos",
    Snapshots = "Snapshots",
    SavedVideos = "Saved Videos",
}

const App = ({ setSelectedVideo, selectedVideo }: VideoList) => {
    const [previewSelection, setPreviewSelection] = useState<string | null>(null);
    const [imageUrl, setImageUrl] = useState<string>("");
    const [navigation, setNavigation] = useState<ListNavigation>(null);

    const { config } = useContext(ConfigContext);
    const { videoFiles, screenshotFiles, savedVideoFiles, } = useContext(SocketContext);

    useEffect(() => {
        const getUrl = () => {
            if (previewSelection === null) {
                return;
            }

            const grabList = previewSelection.includes('mp4') ? 'thumbnail' : 'snapshot';
            setImageUrl(BuildUrl(config, `/get/${grabList}/${previewSelection}`));
        }
        getUrl();
    }, [previewSelection]);

    useEffect(() => {
        if (selectedVideo === null) {
            setPreviewSelection(null);
        }
    }, [selectedVideo]);

    // Initial settings
    useEffect(() => setNavigation(ListNavigation.Videos), []);

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

            <div className={'list-content'}>
                <div className={'title'}> {navigation} </div>

                { navigation === ListNavigation.Videos
                    ? <VideoButtonComponent data={videoFiles} selectedVideo={previewSelection} setSelectedVideo={setPreviewSelection} />
                    : navigation === ListNavigation.Snapshots
                    ? <VideoButtonComponent data={screenshotFiles} selectedVideo={previewSelection} setSelectedVideo={setPreviewSelection} />
                    : <VideoButtonComponent data={savedVideoFiles} selectedVideo={previewSelection} setSelectedVideo={setPreviewSelection} />
                }
            </div>

            <div className={'list-mode-container'}>
                <button title={'Recorded Videos'} className={navigation === ListNavigation.Videos ? 'active' : null} onClick={() => setNavigation(ListNavigation.Videos)}><TfiVideoClapper /></button>
                <button title={'Snapshots'} className={navigation === ListNavigation.Snapshots ? 'active' : null} onClick={() => setNavigation(ListNavigation.Snapshots)}><AiOutlinePicture /></button>
                <button title={'Saved Videos'} className={navigation === ListNavigation.SavedVideos ? 'active' : null} onClick={() => setNavigation(ListNavigation.SavedVideos)}> <FaRegStar /> </button>
            </div>
        </div>
    );
}

export default App;