import { useContext, useEffect, useState } from 'react';
import { FaEye, FaCameraRetro } from "react-icons/fa";
import { VscDebugRestart } from "react-icons/vsc";

import './LiveFeed.scss';
import ReactSlider from "react-slider";
import { BuildUrl, FetchData } from '../Helpers/helper';
import ConfigContext from '../Helpers/ConfigContext';
import { SocketContext } from '../Helpers/SocketContext';

interface LiveFeedInterface {
    ShowControl: boolean,
}

const Layout = ({ShowControl = true}:LiveFeedInterface) => {
    const [value, setValue] = useState<number | null>(null); // Set an initial value
    const [client, setClient] = useState<number>(50); // Set an initial value
    const [streamIp, setStreamIp] = useState<string>(""); // Set an initial value
    const { config } = useContext(ConfigContext);
    const { controlLockState, isRecording, isStreaming, doAction } = useContext(SocketContext);

    const handleChange = (newValue:any) => setClient(newValue *  10);
    const onRestart = () => FetchData(config, '/restart');
    const onToggleStreaming = () => doAction('toggle_stream');
    const onToggleRecord = () => doAction('toggle_recording');
    const onSnapshot = () => FetchData(config, '/snapshot');

    useEffect(() => setStreamIp(isStreaming ? BuildUrl(config, '/video_feed') : null), [isStreaming]);

    useEffect(() => {
        const moveServo = async () => {
            try {
                if (value != null) {
                    setValue(client);
                    FetchData(config, `/move/${client}`);
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
        const getPercent = async () => {
            try {
                const response = await FetchData(config, '/get_percentage');
                
                // Check if the request was successful (status code 200)
                if (response.success) {
                    var initialPosition = response.data.position * 100;
                    setClient(initialPosition);
                    setValue(initialPosition);
                } else {
                    console.error(`Error: ${response.status}`);
                }
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        };

        const initialLoad = () => setStreamIp(BuildUrl(config, '/video_feed'));

        initialLoad();
        getPercent();
    }, [config]); // Empty dependency array to run the effect only once when the component mounts

    return (
        <div className={'livefeed-container'}>
            <div className={'video-display-container'}>
                <img className={'video-display'} src={streamIp} />
            </div>

            <div className={'control-bar'} style={{display: ShowControl ? 'block' : 'none'}}>
                {/* <ReactSlider
                    className={"horizontal-slider"}
                    markClassName={"mark"} 
                    thumbClassName={"thumb"}
                    marks
                    min={0} max={10}
                    value={client / 10}
                    renderThumb={(props, state) => <div {...props}>{value}</div>}
                    onChange={handleChange}
                /> */}

                <div className={'button-container'} style={{display: controlLockState ? 'none' : 'block'}}>
                    <button onClick={()=>onToggleStreaming()} className={isStreaming ? 'streaming' : ''}> <FaEye/> </button>
                    <button onClick={()=>onToggleRecord()} className={isRecording ? 'recording' : ''}> • </button>
                    <button onClick={()=>onRestart()} content="restart"> <VscDebugRestart/> </button>
                    <button onClick={()=>onSnapshot()} content="snapshot"> <FaCameraRetro/> </button>
                </div>
            </div>
        </div> 
    )
};

export default Layout;
