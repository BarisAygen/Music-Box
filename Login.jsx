import React, { useState } from 'react';
import axios from 'axios';
import { useLazyGetAllTracksQuery, useLazyGetGeneralTopRatedTracksQuery, useLazyGetTopRatedTracksQuery, useLazyGetUserLikedTracksQuery, useLazyGetUserNameQuery } from './services/musicboxApi';

export const Login = (props) => {
    const [email, setEmail] = useState('');
    const [pass, setPassword] = useState('');
    const [triggergetlikedsongs] = useLazyGetUserLikedTracksQuery(); 
    const [triggergetalltracks] = useLazyGetAllTracksQuery();
    const [triggergetgeneraltopratedtracks] = useLazyGetGeneralTopRatedTracksQuery();
    const [triggergettopratedtracks] = useLazyGetTopRatedTracksQuery();
    const [triggergetusername] = useLazyGetUserNameQuery();
    const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post("http://localhost:5000/login", {
                email: email,
                password: pass 
            });

                if (response.status === 200) {
                    const { access_token, refresh_token } = response.data;
                    localStorage.setItem("access_token", access_token);
                    localStorage.setItem("refresh_token", refresh_token);
                    await sleep(1000);
                    triggergetlikedsongs();
                    triggergetalltracks();
                    triggergettopratedtracks();
                    triggergetgeneraltopratedtracks();
                    triggergetusername();
                    props.onFormSwitch('home');
                }
        }
        catch (error) {
            console.log(error);
            alert("Wrong email or password!");
        }
    }  

    return (
        <>
            <div className='auth-form-container'>
                <h2>Login</h2>
                <form className='login-form' onSubmit={handleSubmit}>
                    <label htmlFor="email">Email</label>
                    <input value={email} onChange={(e) => setEmail(e.target.value)} type='email' name='email' id='email' placeholder='ilkan@gmail.com' required maxLength={50} />
                    <label htmlFor="password">Password</label>
                    <input value={pass} onChange={(e) => setPassword(e.target.value)} type='password' name='password' id='password' required maxLength={50} />
                    <button type='submit'>Login</button>
                </form>
                <button className='link-btn' onClick={() => props.onFormSwitch('register')}>Do not have an account?</button>
            </div>
        </>
    );
};