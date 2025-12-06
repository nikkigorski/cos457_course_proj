/*
Author: Jove Emmons

*/

import {useState,useEffect} from 'react';

export default function Login({onLogin,user,fetchUser,doLogin}){
  //  Keeps track of the text entered into the Username field.
  const [username,setUsername] = useState('');
  //  Keeps track of the text entered into the Password field.
  const [password,setPassword] = useState('');
  //  Keeps track of the result of login attempts. -1 is no attempts made, 0 failure, 1 success.
  const [results,setResults] = useState(-1);
  
  useEffect(
    () => {
      if (user != null){
        fetchUser(user);
      }
    },[]
  );

  const login = async (e) => {
    e.preventDefault();
    let response = await onLogin(username,password);
    if (response.data.length == 1){//login succeeded
      setResults(response.data[0]);
      await doLogin(response.data[0]);
      return;
    }else{
      setResults(0);
      return;
    }
  };

  return (
    <form className="login" onSubmit={login}>
      <h2>Login</h2>
      <input className="login-username" placeholder="Username" value={username} onChange={e=>setUsername(e.target.value)} />
      <input className="login-password" placeholder="Password" value={password} onChange={e=>setPassword(e.target.value)} />
      <div className="login-actions">
        <button className='btn btn-primary' type="submit">Log In</button>
      </div>
      <div>{results ? "" : "Incorrect username or password"}</div>
    </form>
  );
}