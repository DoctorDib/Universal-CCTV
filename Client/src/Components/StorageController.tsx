
import { useState, useEffect, useContext } from 'react';

import './StorageController.scss';
import { FetchData } from '../Helpers/helper';
import ConfigContext from '../Helpers/ConfigContext';

interface StorageControllerInterface {
}

const App = ({  }: StorageControllerInterface) => {
    const [total, setTotal] = useState<number>(0); // Set an initial value
    const [available, setAvailable] = useState<number>(0);
    const [usedPercentage, setUsedPercentage] = useState<number>(0);
    const { config } = useContext(ConfigContext);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await FetchData(config, '/get/disk');

                // Check if the request was successful (status code 200)
                if (response.success) {
                    setTotal(response.data.total.toFixed(2));
                    setAvailable(response.data.availiable.toFixed(2));

                    if (response.data.availiable === 0) {
                        setUsedPercentage(100);
                    } else {
                        setUsedPercentage(100 - (response.data.total / response.data.availiable));
                    }

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
                <div className={'available'}> { available } GB </div>
                <div className={'total'}> { total } GB </div>
            </div>
        </div>
    );
}

export default App;
