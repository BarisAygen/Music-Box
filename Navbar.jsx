import React from 'react';
import {Link, NavLink} from 'react-router-dom';
import './Navbar.css';
import Logo from "./img/music-box-logo.jpeg";

export const Navbar = () => {
    const isActive = (path) => {
        const currentPath = window.location.pathname;
        const matchPaths = ["/Home", "/FriendsSongs", "/RecommendedSongs", "/Songs", "/Recommendations", "/Friends"];
    
        return matchPaths.some((matchPath) => currentPath.includes(matchPath)) || currentPath === path;
    };
    
    return (
        <>
            <nav className='main-navbar'>
                <div className='leftSide'>
                    <Link to='/Songs' className='title'>
                        <img className='logo' src={Logo} alt=''/>
                    </Link>
                </div>
                <ul>
                    <li><NavLink to='/Songs' isActive={() => isActive('/Songs')} className={isActive('/Songs') ? 'active' : ''}>Home</NavLink></li>
                    <li><NavLink to='/Search'>Search</NavLink></li>
                    <li><NavLink to='/Upload'>Upload</NavLink></li>
                    <li><NavLink to='/Statistics'>Statistics</NavLink></li>
                    <li><NavLink to='/Profile'>Profile</NavLink></li>
                </ul>
            </nav>
        </>
    );
};