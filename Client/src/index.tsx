import React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter, Routes, Route } from "react-router-dom";

import './index.scss';
import App from './App.tsx';
import Layout from './Layout.tsx';

ReactDOM.render(
    <BrowserRouter>
        <Routes>
            <Route path="/" element={<Layout />}>
                <Route index element={<App />} />
                <Route path="blogs" element={<App />} />
            </Route>
        </Routes>
    </BrowserRouter>,
    document.getElementById('root')
);