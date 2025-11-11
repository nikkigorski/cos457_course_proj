/*
File: Stored Procedures and Functions - Lobster Notes.sql
Author: Gage White
Date: 10 November 2025
Description: Stored Procedures and Functions for Lobster Notes Project
*/



/*
Procedure for creating a new user, specifying enrolled courses and if user is a professor
*/
delimiter //
create procedure SP_User_Create
(
    IN user_name varchar(50),
    IN enrolled_courses varchar(50),
    IN professor_check boolean
)

begin
Insert into user
(
    Name,
    Courses,
    IsProfessor
)
values
(
    user_name,
    enrolled_courses,
    professor_check
);
end//
delimiter ;

/*
Procedure for updating username by taking UserID for user to be altered
*/
delimiter //
create procedure SP_Update_User
(
	IN user_id int UNSIGNED,
	IN new_name varchar(50)
)
begin
	update user
	set name = new_name
	where UserID = user_id;

end//
delimiter ;

/*
Creates a new resource
*/
delimiter//
create procedure SP_Resource_Create
(
	IN lecture_date date,
    IN author_of varchar(50),
    IN lecture_topic varchar(25),
    IN resource_keywords varchar(25),
    IN format_of varchar(7),
    IN note_body varchar(2048),
    IN web_address varchar(2048)
)
begin
	declare resource_id int;
	start transaction;
		
	insert into resource
	(
			DateFor,
			Author,
			Topic,
			Keywords,
			Format
	)
	values
	(
			lecture_date,
			author_of,
			lecture_topic,
			resource_keywords,
			format_of
	);

	set resource_id = last_insert_id();

	if format_of = 'Note' then
	insert into note
		(
			ResourceID,
			Body
		)
		values
		(
			resource_id,
			note_body
		);
	elseif format_of = 'Website' 
	then insert into website
		(
			ResourceID,
			Link
		)
		values
		(
			resource_id,
			web_address
		);
	end if;
	commit;
end//
delimiter ; 

    