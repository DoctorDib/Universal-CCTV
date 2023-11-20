import React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter, Routes, Route } from "react-router-dom";

import './index.scss';
import App from './App.tsx';

ReactDOM.render(
    <BrowserRouter>
        <Routes>
            {/* <Route  element={<Layout />}> */}
            <Route path="/" element={<App />} />
            {/* <Route path="videos" element={<Videos />} />
            <Route path="video_editor" element={<VideoEditor />} /> */}
            {/* </Route> */}
        </Routes>
    </BrowserRouter>,

    document.getElementById('root')
);