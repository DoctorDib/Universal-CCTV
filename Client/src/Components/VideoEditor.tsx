
import { useState, useEffect } from 'react';

import './Videos.scss';

const VideoEditor = () => {

    const [videoList, setVideoList] = useState<Array<string>>([]); // Set an initial value

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
        <div className={'app-container'}>
            <div className={'container'}>
                <h2> Videos </h2>
                <img className={'camera-display'} src="http://192.168.0.21:5000/video_feed" />
 

                {videoList.map((element, index) => (
                    <div key={index}>
                        {element}
                    </div>
                ))}
            </div>
        </div>
    );
}

export default VideoEditor;
