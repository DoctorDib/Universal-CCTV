
import { useState, useEffect, useContext } from 'react';
import { FaTrash } from "react-icons/fa";

import './SnapshotList.scss';
import ConfigContext from '../Helpers/ConfigContext';
import { BuildUrl, FetchData } from '../Helpers/helper';

const App = () => {

    const [element, setElement] = useState<Array<React.ReactElement>>();
    const [snapshotList, setSnapshotList] = useState<Array<string>>([]); // Set an initial value
    const { config } = useContext(ConfigContext);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await FetchData(config, '/get/snapshot_list');

                // Check if the request was successful (status code 200)
                if (response.success) {
                    
                    var data = response.data.pictures;
                    setSnapshotList(data);
                    // setValue((await response.json()).data.position * 100);                
                } else {
                    console.error(`Error: ${response.status}`);
                }
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        };
    
        fetchData();
    }, [config]); // Empty dependency array to run the effect only once when the component mounts

    useEffect(() => {
        console.log(snapshotList)
        setElement(snapshotList.slice().sort((a, b) => b.localeCompare(a)).map((name, index) => (
            <div key={index} className={'snapshot'}>

                <div className={'delete-button'}>
                    <FaTrash/>
                </div>

                <div className='main-content'>    
                    <img src={BuildUrl(config, `/get/snapshot/${name}`)}/>
                </div>

                {index == 0 ? <div className={'blinking-circle'}> </div> : null}
            </div>
        )));
    }, [snapshotList]);

    return (
        <div className={'snapshot-list-container'}>
            <div className={'title'}> Snapshots </div>

            <div className={'list-container'}>
                {element}
            </div>
        </div>
    );
}

export default App;
