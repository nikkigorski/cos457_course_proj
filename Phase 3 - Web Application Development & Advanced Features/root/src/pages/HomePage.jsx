import { useEffect, useState } from "react"

export default function HomePage({users, user}){
    const initState = [{'UserID':0,'Name':'smths','Courses':'nope','IsProfessor':0},
        {'UserID':1,'Name':'smth','Courses':'yep','IsProfessor':0}];
    
    const [userList,setUserList] = useState(initState); // state variable to contain the results of our query to the database
    
    useEffect( () => { // activates when the component is loaded
      users().then( // the users parameter passed in is a function, so we need to call it as a function
                    // the users function returns a Promise, so we need to use .then() to act once we get its contents
        (result)=>{ // .then() lets us use the contents of the Promise in a function, so we can then pass the value into some other function within it
          setUserList(result); // we can now update a state variable that will be displayed on the website
        }
      );
    }, [] ); // the dependents array being empty means it only goes off once


    
    
    return(
        <div>

            <h1>Empty Homepage</h1>
            {
                userList.map((usr) => (
                    <div key={usr.UserID}>
                    <span>UserID: {usr.UserID}, Name: {usr.Name}, Courses: {usr.Courses}, Is Professor: {usr.IsProfessor} </span>
                    <br></br>
                    </div>
                )
                )
            }
        </div>
    );
}


/*
working example of how to get data from the database
this can be put after the Empty Homepage line and it will work
{ //escaping with {} to use javascript code
                userList.map((usr) => ( //mapping the userList array lets us display its contents across multiple elements
                    <div key={usr.UserID}>
                    <span>UserID: {usr.UserID}, Name: {usr.Name}, Courses: {usr.Courses}, Is Professor: {usr.IsProfessor} </span>
                    // as seen above, we get each row of data as an object. all of the row objects are in an array
                    <br></br>
                    </div>
                )
                )
            }

*/