/*
Constraint Validation: tests constraints in tables with small queries that intentially violate
@Author Gage White
@Date 15 November 2025
*/

/*
Checks that there are no more than 1 user with the same UserID
*/
Select UserID, Count(*)
From user
group by UserID having count(*) > 1;

/*
Attempts to insert user with existing name, violating uniqueness constraint
Expected error: Duplicate Entry
*/
Call SP_User_Create('Zelda', null, true, 'password123');
Call SP_User_Create('Zelda', null, true, 'password456');

/*
Parent User record to Professor
*/
SELECT *
FROM user
WHERE UserID = '12418';

/*
Illustrates that there is a matching key in professor table
*/
SELECT *
FROM Professor
WHERE UserID = 12418;