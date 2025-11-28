/*
SPF Demonstration: scripts to demonstrate stored procedures and functions for video
@Author Gage White
@Date 15 November 2025

/*
SP For Creating User
*/
CALL SP_User_Create('William Riker', null, TRUE);

SELECT *
FROM user
WHERE Name = 'William Riker';

/*
Trigger TR_User_AfterInsert adds to Professor table automatically
*/
SELECT *
FROM Professor
WHERE UserID = 12415;

/*
Creates a new Resource
*/
CALL SP_Resource_Create(CURDATE(), 'William Riker', 'Game Development', Null, 'Website', Null, 'https://ocw.mit.edu/gamedev');

Select *
FROM Resource
ORDER BY ResourceID DESC LIMIT 1;

SELECT *
FROM website
Where ResourceID = (1583);

SELECT FN_User_IsProfessor(12415) as Is_Prof;

Call SP_Update_User(12415, 'Jack');

/*
Shows William Riker no longer exists
*/
select *
from user
where name = 'William Riker';

/*
Shows Odo in Riker's place
*/
select *
from user
where name = 'Jack';

/*
Queries User
*/
select *
from user;

/*
Queries Resource
*/
select *
from resource;

select FN_Rating_Avg(360) as resource_id;
