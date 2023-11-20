import React, { useEffect, useState } from 'react';
import { FaPlay, FaStop } from "react-icons/fa";
import { VscDebugRestart } from "react-icons/vsc";

import './LiveFeed.scss';
import ReactSlider from "react-slider";

interface LiveFeedInterface {
    ShowControl: boolean,

}

const Layout = ({ShowControl = true}:LiveFeedInterface) => {
    const [value, setValue] = useState<number | null>(null); // Set an initial value
    const [client, setClient] = useState<number>(50); // Set an initial value

    const handleChange = (newValue) => {
        console.log(newValue * 10)
        setClient(newValue * 10);
    };

    const onRestart = () => {
        fetch(`http://192.168.0.21:5000/restart`);
    };

    const onStop = () => {
        fetch(`http://192.168.0.21:5000/stop`);
    };

    const onStart = () => {
        fetch(`http://192.168.0.21:5000/start`);
    };

    useEffect(() => {
        const moveServo = async () => {
            try {

                if (value != null) {
                    setValue(client);
                    
                    fetch(`http://192.168.0.21:5000/move/${client}`);
                } else {
                    setValue(client);
                }
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        };
    
        moveServo();
    }, [client]);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await fetch('http://192.168.0.21:5000/get_percentage');
                
                // Check if the request was successful (status code 200)
                if (response.ok) {
                    var initialPosition = (await response.json()).data.position * 100;
                    setClient(initialPosition);
                    setValue(initialPosition);
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
        <div className={'livefeed-container'}>
            <img className={'camera-display'} src="http://192.168.0.21:5000/video_feed" />

            <div className={'control-bar'} style={{display: ShowControl ? 'block' : 'none'}}>
                <ReactSlider
                    className="horizontal-slider"
                    marks
                    markClassName="mark"
                    min={0}
                    max={10}
                    value={client / 10}
                    thumbClassName="example-thumb"
                    trackClassName="example-track"
                    renderThumb={(props, state) => <div {...props}>{value}</div>}
                    onChange={handleChange}
                />

                <div className={'button-container'}>
                    <button onClick={()=>onStart()} content="start"> <FaPlay/> </button>
                    <button onClick={()=>onStop()} content="stop"> <FaStop/> </button>
                    <button onClick={()=>onRestart()} content="restart"> <VscDebugRestart/> </button>
                </div>
            </div>
        </div> 
    )
};

export default Layout;
