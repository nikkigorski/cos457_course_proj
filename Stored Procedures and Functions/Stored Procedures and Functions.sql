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

delimiter //
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

	case format_of
		when 'Note' then
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
		when 'Website' then
			insert into website
			(
				ResourceID,
				Link
			)
			values
			(
				resource_id,
				web_address
			);
	end case;
    
	commit;
end//
delimiter ; 

/*
Allows submission of rating
*/
delimiter //
create procedure SP_Rating_Rate
(
	IN resource_ID int unsigned,
	IN rater varchar(50),
    IN rating numeric(2,1),
    IN date_of date
)
begin
	insert into rating
		(
			ResourceID,
			Poster,
            Score,
            Date
		)
	values
    (
		resource_ID,
		rater,
        rating,
        date_of
	);
    update Resource
		set Rating =
        (
        Select avg(r.Score) 
        from Rating as r
        where r.ResourceID = resource_ID
        )
	where ResourceID = resource_ID;
    
    
end//
delimiter ;

/*
Gets details for a resource based on ResourceID
*/
delimiter //
create procedure SP_Resource_Details
(
	IN resource_ID int unsigned
)
begin
select
	R.ResourceID, 
    R.Topic, 
    R.Format, 
    R.DateFor,
    R.Author as Author_Name,
    N.Body as Note_Body,
    W.Link as Web_Address,
    V.Duration as Video_Duration,
    
    (
    select avg(score) 
    from Rating 
    where ResourceID = R.ResourceID
    ) as Average_Rating
    
from Resource as R join user as U on R.Author = U.Name
left join Note as N on R.ResourceID = N.ResourceID
left join Website as W on R.ResourceID = W.ResourceID
left join Video as V on R.ResourceID = V.ResourceID

where R.ResourceID = resource_ID;

end//
delimiter ; 

/*
Returns average score of given ResourceID
*/
delimiter //
create function FN_Rating_Avg(resource_id int)
	returns decimal(2,1)
	begin
	declare r_avg decimal(2,1);
		select avg(Rating) into r_avg
		from Resource
		where Resource.ResourceID = resource_id;
	return r_avg;
end

