
import React from 'react';
import { useState, useEffect } from 'react';
import classNames from 'classnames';
import { FaDownload } from "react-icons/fa";

import './VideoList.scss';
import LiveFeed from './LiveFeed.tsx';

interface VideoList {
    setSelectedVideo: (filename: string | null) => void,
    selectedVideo: string | null,
}

const App = ({ setSelectedVideo, selectedVideo }: VideoList) => {

    const [videoList, setVideoList] = useState<Array<string>>([]); // Set an initial value

    const formatName = (name: string) => {
        console.log(name)
        name = name.split('.')[0];
        name = name.replace('_', '-');
        const split = name.split('-');
        return `${split[3]}:${split[4]} ${split[2]}/${split[1]}/${split[0]}`;
    };

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await fetch('http://192.168.0.21:5000/get_files');

                // Check if the request was successful (status code 200)
                if (response.ok) {
                    var data = (await response.json()).data.files;
                    setVideoList(data)
                    // setValue((await response.json()).data.position * 100);                
                } else {
                    console.error(`Error: ${response.status}`);
                }
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        };
    
        fetchData();
    }, []); // Empty dependency array to run the effect only once when the component mounts

    return (
        <div className={'video-list-container'}>

            <div onClick={()=>setSelectedVideo(null)}>
                {
                    selectedVideo == null ? <div className={'camera-display'}></div> : <LiveFeed ShowControl={false}/>
                }
            </div>
            
            <div className={'list-container'}>
                {videoList.slice().sort((a, b) => b.localeCompare(a)).map((name, index) => (
                    <div key={index} className={classNames('video-button', name == selectedVideo ? 'selected' : null)} onClick={() => setSelectedVideo(name)}>
                        <div className='main-content'>
                            <a href={'http://192.168.0.21:5000/download/' + name}>
                                <div className='download-button'>
                                    <FaDownload />
                                </div>
                            </a>
                            
                            {formatName(name)}
                        </div>

                        {index == 0 ? <div className={'blinking-circle'}> </div> : null}
                    </div>
                ))}
            </div>
        </div>
    );
}

export default App;
