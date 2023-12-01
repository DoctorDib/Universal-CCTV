// MyProvider.js
import { useState } from 'react';
import MyContext from './ConfigContext';

const MyProvider = ({ children }: any) => {
    const [config, setConfig] = useState(null);

    const fetchData = async () => {
        try {
            const response = await fetch('config.json');
            const result = await response.json();
            setConfig(result);
        } catch (error) {
            console.error('Error fetching data:', error);
        }
    };

    return (
        <MyContext.Provider value={{ config, fetchData }}>
            {children}
        </MyContext.Provider>
    );
};

export default MyProvider;
