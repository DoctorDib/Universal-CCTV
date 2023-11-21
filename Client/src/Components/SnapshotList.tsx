
import React from 'react';
import { useState, useEffect } from 'react';
import classNames from 'classnames';
import { FaTrash } from "react-icons/fa";

import './SnapshotList.scss';

const App = () => {

    const [snapshotList, setSnapshotList] = useState<Array<string>>([]); // Set an initial value
    const [previewSelection, setPreviewSelection] = useState<string | null>(null);

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
                const response = await fetch('http://192.168.0.21:5000/get/snapshot_list');

                // Check if the request was successful (status code 200)
                if (response.ok) {
                    
                    var data = (await response.json()).data.pictures;
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
    }, []); // Empty dependency array to run the effect only once when the component mounts

    return (
        <div className={'snapshot-list-container'}>
            <div className={'title'}> Snapshots </div>

            <div className={'list-container'}>
                {snapshotList.slice().sort((a, b) => b.localeCompare(a)).map((name, index) => (
                    <div key={index} className={'snapshot'} onClick={() => setPreviewSelection(name)}>

                        <div className={'delete-button'}>
                            <FaTrash/>
                        </div>

                        <div className='main-content'>    
                            <img src={`http://192.168.0.21:5000/get/snapshot/${name}`}/>
                        </div>

                        {index == 0 ? <div className={'blinking-circle'}> </div> : null}
                    </div>
                ))}
            </div>
        </div>
    );
}

export default App;
