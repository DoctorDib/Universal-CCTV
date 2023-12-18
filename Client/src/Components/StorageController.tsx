
import { useState, useEffect, useContext } from 'react';

import './StorageController.scss';
import { FetchData } from '../Helpers/helper';
import ConfigContext from '../Helpers/ConfigContext';
import { SocketContext } from '../Helpers/SocketContext';

interface StorageControllerInterface {
}

const App = ({  }: StorageControllerInterface) => {
    const [total, setTotal] = useState<number>(0); // Set an initial value
    const [usedPercentage, setUsedPercentage] = useState<number>(0);
    const { storageUsed } = useContext(SocketContext);
    const { config } = useContext(ConfigContext);

    useEffect(() => {
        if (total === 0) {
            return;
        }

        if (storageUsed === 0) {
            setUsedPercentage(100);
        } else {
            setUsedPercentage(100 - ((storageUsed / total) * 100));
        }
    }, [storageUsed]);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await FetchData(config, '/get/disk');

                // Check if the request was successful (status code 200)
                if (response.success) {
                    setTotal(response.data.total.toFixed(2));
                } else {
                    console.error(`Error: ${response.status}`);
                }
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        };
    
        fetchData();
    }, [config]); // Empty dependency array to run the effect only once when the component mounts

    return (
        <div className={'storage-container'}>
            <div className={'bar'}>
                <div className={'filler'} style={{ width: `${usedPercentage}%` }}> </div>
            </div>
            <div className={'titles'}> 
                <div className={'available'}> Available </div>
                <div className={'total'}> Total </div>
            </div>
            <div className={'info'}> 
                <div className={'available'}> { storageUsed.toFixed(2) } GB </div>
                <div className={'total'}> { total } GB </div>
            </div>
        </div>
    );
}

export default App;
