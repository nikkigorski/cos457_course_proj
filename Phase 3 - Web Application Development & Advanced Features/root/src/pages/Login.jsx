/*
Jove Emmons
11/30/25
*/

import React, {useState,useEffect} from 'react';

export default function Login(){
    const [username,setUsername] = useState('');
    const [password,setPassword] = useState('');


    return (
      <form className="login" onSubmit={onSubmitDo}>
        <h2>Login</h2>
        <input className="login-username" placeholder="Username" value={username} onChange={e=>setUsername(e.target.value)} />
        <input className="login-password" placeholder="Password" value={password} onChange={e=>setPassword(e.target.value)} />
        <div className="login-actions">
          <button className='btn btn-primary' type="submit">Log In</button>
        </div>
      </form>
    );
}

export function onSubmitDo(){


}