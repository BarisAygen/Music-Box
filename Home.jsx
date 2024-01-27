import React from 'react';
import { Route, Routes, useLocation } from 'react-router-dom';
import { Navbar } from './Navbar';
import { SecondNavbar } from './SecondNavbar';
import { Search } from './Search';
import { Upload } from './Upload';
import { Statistics } from './Statistics';
import { Profile } from './Profile';
import { Songs } from './Songs';
import { Recommendations } from './Recommendations';
import { Friends } from './Friends';

export const Home = () => {
    const location = useLocation();
    const visibleOnPages = ['/Home', '/Songs', '/Recommendations', '/Friends'];
    const isSecondNavbarVisible = visibleOnPages.includes(location.pathname);

    return (
        <>
            <div className='Home'>
                <Navbar />
                <Routes>
                    <Route path='/Search' element={<Search />} />
                    <Route path='/Upload' element={<Upload />} />
                    <Route path='/Statistics' element={<Statistics />} />
                    <Route path='/Profile' element={<Profile />} />
                </Routes>
                {isSecondNavbarVisible && <SecondNavbar />}
                <Routes>
                    <Route path='/Songs' element={<Songs />} />
                    <Route path='/Recommendations' element={<Recommendations />} />
                    <Route path='/Friends' element={<Friends />} />
                </Routes>
            </div>
        </>
    );
};