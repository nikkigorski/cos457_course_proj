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
    console.log("login attempt");
    console.log("button clicked at ",Date.now());
    let response = await onLogin(username,password);
    console.log("after await",Date.now()); //everything between here and in dologin is fast
    console.log("results are",response);
    console.log(typeof response);
    setResults(response.data.value);
    console.log("after setresults",Date.now());
    if (response.data.value==1){
      console.log("valid, before dologin",Date.now());
      await doLogin(response.data.name);
      console.log("valid, after dologin. all done",Date.now());
    }
    return;
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