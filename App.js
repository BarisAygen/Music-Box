import React, { useState } from 'react';
import { Login } from './Login';
import { Home } from './Home';
import { Register } from './Register'; 
import { Search } from './Search';
import './App.css';
import './Colors.css';
import { Provider } from 'react-redux';
import { store } from './store/store';

function App() {
    const [currentPage, setCurrentPage] = useState('login');
    
    const togglePage = (pageName) => {
        setCurrentPage(pageName);
    }

    return (
        <Provider store={store}>
            <div className="App">
                {currentPage === 'login' ? (
                    <Login onFormSwitch={togglePage} />
                ) : currentPage === 'home' ? (
                    <Home onPageChange={togglePage} currentPage={currentPage} />
                ) : currentPage === 'register' ? (
                    <Register onFormSwitch={togglePage} />
                ) : (
                    <Search />
                )}
            </div>
        </Provider>
    );
}

export default App;