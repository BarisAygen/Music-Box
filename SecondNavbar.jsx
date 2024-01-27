import React from 'react';
import {NavLink} from 'react-router-dom'
import './SecondNavbar.css';

export const SecondNavbar = () => {
    return (
        <>
            <nav className='second-navbar'>
                <ul>
                    <li><NavLink to='/Songs'>Songs</NavLink></li>
                    <li><NavLink to='/Recommendations'>Recommendations</NavLink></li>
                    <li><NavLink to='/Friends'>Friends</NavLink></li>
                </ul>
            </nav>
        </>
    );
}