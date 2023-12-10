
import { useState, useEffect, useContext } from 'react';
import classNames from 'classnames';
import { FaDownload, FaEye } from "react-icons/fa";

import './VideoList.scss';
import LiveFeed from './LiveFeed';
import StorageController from './StorageController';
import { BuildUrl, FetchData, } from '../Helpers/helper';
import ConfigContext from '../Helpers/ConfigContext';
import { SocketContext } from '../Helpers/SocketContext';

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

    const formatName = (name: string) => {
        name = name.split('.')[0];
        name = name.replace('_', '-');
        
        const split = name.split('-');
        return `${split[3]}:${split[4]} ${split[2]}/${split[1]}/${split[0]}`;
    };

    const loadVideo = (name: string) => setSelectedVideo(name);

    useEffect(() => {
        setVideoList(videoFiles);
    }, [videoFiles])

    // useEffect(() => {
    //     const getFiles = async () => {
    //         try {
    //             const response = await FetchData(config, "/get_files");

    //             // Check if the request was successful (status code 200)
    //             if (response.success) {
    //                 var data = response.data.files;
    //                 setVideoList(data);
    //             } else {
    //                 console.error(`Error: ${response.status}`);
    //             }
    //         } catch (error) {
    //             console.error('Error fetching data:', error);
    //         }
    //     };
    
    //     getFiles();
    // }, [config]); // Empty dependency array to run the effect only once when the component mounts

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

            <div onClick={()=>setSelectedVideo(null)}>
                {
                    selectedVideo == null 
                        ? <img src={imageUrl} className={'camera-display'}/>
                        : <LiveFeed ShowControl={false}/>
                }
            </div>

            <div className={'list-container'}>
                {videoList.slice().sort((a, b) => b.localeCompare(a)).map((name, index) => (
                    <div key={index} className={classNames('video-button', name == previewSelection ? 'selected' : null)} onClick={() => setPreviewSelection(name)}>
                        <div className='main-content'>
                            
                            <div className='video-option'>
                                <a href={BuildUrl(config, `/download/${name}`)}>
                                    <FaDownload />
                                </a>
                            </div>
                            
                            <div className='video-option' onClick={() => loadVideo(name)}>
                                <FaEye />
                            </div>
                            
                            <div className={'date'}>
                                {formatName(name)}
                            </div>
                        </div>

                        {index == 0 ? <div className={'blinking-circle'}> </div> : null}
                    </div>
                ))}
            </div>
        </div>
    );
}

export default App;
