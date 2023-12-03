import ReactDOM from 'react-dom';
import { BrowserRouter, Routes, Route } from "react-router-dom";

import './index.scss';
import App from './App';
import ConfigProvider from './Helpers/ConfigProvider';

ReactDOM.render(
    <BrowserRouter>
        <Routes>
            <Route path="/" element={
                <ConfigProvider> 
                    <App /> 
                </ConfigProvider>
            } />
        </Routes>
    </BrowserRouter>,

    document.getElementById('root')
);