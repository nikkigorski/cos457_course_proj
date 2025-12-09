import { useEffect, useRef, useState } from 'react';

function Topbar({ searchQuery, setSearchQuery, onSearch, onClear, onDashboard, 
  onNotes, user, hasUser, onLogout, onHome, onLoginButton, onCreateAccount}){
  // When no user exists yet, hide navigation/search controls.
  const isProfessor = user?.isProfessor;
  return (
    <header className="topbar">
      <div style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '12px', width: '100%'}}>
        <div style={{display: 'flex', alignItems: 'center', gap: '12px'}}>
          <div className="brand">Lobster Notes</div>
          {hasUser ? (
            <div style={{display:'flex'}}>
              <button className="btn" type="button" onClick={onHome} title="Homepage">Home</button>
              <form onSubmit={onSearch} style={{display:'flex', alignItems:'center', gap: '8px'}}>
                <input
                  className="note-search"
                  placeholder="Search notes..."
                  value={searchQuery}
                  onChange={e => setSearchQuery(e.target.value)}
                  style={{padding: '6px 8px', borderRadius: 6, border: '1px solid #e6e9ef'}}
                />
                <button className="btn" type="submit">Search</button>
                <button className="btn" type="button" onClick={onClear}>Clear</button>
              </form>
              {isProfessor && <button className="btn" type="button" onClick={onDashboard} title="Open Professor Dashboard">Professor Dashboard</button>}
              <button className="btn" type="button" onClick={onNotes} title="Back to Notes">Notes</button>
            </div>
          ) : null}
        </div>
        {(!hasUser) && <button className='btn' type='button' onClick={onCreateAccount} title='Account Creation'>Create Account</button>}
        {loginOrUser(onLoginButton,onLogout,user,hasUser)}
      </div>
    </header>
  );
}

export default Topbar;


/**Serves either the login button or the user button.
 * 
 * The user button includes the user dropdown component, which is conditionally visible.
 * @returns The login button if not logged in. Otherwise, the user button and user dropdown.
 */
function loginOrUser(onLoginButton,onLogoutButton,user,hasUser){
  //  Whether or not the user dropdown is visible
  const [userDropVisible,setVisibility] = useState(false);
  //  A reference to the user dropdown
  const ref = useRef(null);
  
  //  When the user logs in and ref is changed, creates an event listener for clicking
  useEffect(() => {
    function clickOut(e){
      if(ref.current && !ref.current.contains(e.target)){
        setVisibility(false);
      }
    }
    document.addEventListener('mousedown',clickOut);
    return () => {
      document.removeEventListener('mousedown',clickOut);
    }
  }, [ref]);
  
  
  /** Returns the user button.  
   *  Includes functions used for its logic.
   * 
   * @returns The user button. dropdown. Conditionally visible.
   */
  function userBtn(){
    //Sets the user dropdown to be visible if the user button is clicked
    function userClick(){
      setVisibility(true);
    };

    //
    /** Logic for the log out button within the dropdown
     */
    function onLogout(){
      setVisibility(false);
      onLogoutButton();
    };

    /** The dropdown element.
     * 
     * Appears when the user button is clicked
     * Disappears when anything other than itself or its children components is clicked
     * The user button being clicked will make it momentarily disappear and then reappear
    */
    return <div className='dropdown-shell' style={{position:'relative'}}>
      <button className="btn" type="button" style={{marginLeft:0}} onClick={userClick} title="User">User</button>
      <div ref={ref} style={{position:'fixed',width:'fit-content',display:'flex',background:"rgba(0,0,0,0)"}}>
        {userDropVisible && (<div className="dropdown" style={{width:'fit-content',position:'relative',top:'0%',left:'0%'}}>
          <h5>{user.name}</h5>
          <div>{user.isprofessor ? "Professor" : "Student"}</div>
          <div>UserID: {user.userid}</div>
          <button className='btn btn-primary' type="button" onClick={onLogout}>
          Log out</button></div>)}
      </div>
    </div> 
  };

  if (!hasUser){
    return <button className="btn" style={{float:'right'}} type="button" onClick={onLoginButton} title="Login page" >Login</button>;
  }else{
    return userBtn();
  }
}