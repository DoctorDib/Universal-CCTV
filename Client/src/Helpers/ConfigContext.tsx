import { createContext } from 'react';

interface ConfigContextType {
    config: Config;
    fetchData: () => Promise<void>;
}

const ConfigContext = createContext<ConfigContextType | undefined>(undefined);

export interface Config {
    ip: string, 
    port: string,
}

export default ConfigContext;
