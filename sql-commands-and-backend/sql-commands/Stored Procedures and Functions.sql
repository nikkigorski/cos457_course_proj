/*
File: Stored Procedures and Functions - Lobster Notes.sql
Author: Gage White
Date: 10 November 2025
Description: Stored Procedures and Functions for Lobster Notes Project
*/

USE lobsternotes;


/*
Procedure for creating a new user, specifying enrolled courses and if user is a professor
*/
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

-- Replicate trigger functionality since triggers can't be piped
IF professor_check = TRUE THEN
    INSERT INTO professor (UserID, Badge)
    VALUES (LAST_INSERT_ID(), NULL);
ELSE
    INSERT INTO student (UserID)
    VALUES (LAST_INSERT_ID());
END IF;
end;

-- create trigger TR_User_AfterInsert
-- after insert on User
-- for each row
-- begin
-- 	if new.IsProfessor = True then
-- 		insert into Professor (UserID, Badge)
--         values (new.UserID, Null);
-- 	else
-- 		insert into Student (UserID)
--         values (new.UserID);
-- 	end if;
-- end;

/*
Procedure for updating username by taking UserID for user to be altered
*/
create procedure SP_Update_User
(
	IN user_id int UNSIGNED,
	IN new_name varchar(50)
)
begin
	update user
	set name = new_name
	where UserID = user_id;

end;

/*
Creates a new resource
*/

create procedure SP_Resource_Create
(
	IN lecture_date date,
    IN author_of varchar(50),
    IN lecture_topic varchar(25),
    IN resource_keywords varchar(25),
    IN format_of varchar(7),
    IN note_body varchar(2048),
    IN web_address varchar(2048),
    IN video_duration int unsigned,
    IN image_size int unsigned
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
		when 'Pdf' then
			insert into pdf
				(
					ResourceID,
                    Body,
					Link
				)
                values
                (
					resource_id,
                    note_body,
                    web_address
				);
		when 'Image' then
			insert into image
				(
					ResourceID,
                    Size,
                    Link
				)
                values
                (
					resource_id,
                    null,
                    web_address
				);
			when 'Video' then
				insert into video
					(
						ResourceID,
                        Duration,
                        Link
					)
                    values
                    (
						resource_id,
                        null,
                        web_address
					);

	end case;
    
	commit;
end; 

/*
Links professor to course
*/
create procedure SP_Course_IsProfessor
(
	IN course_id int unsigned,
    IN prof_id int unsigned
)
begin
	if exists(
		select 1
        from professor
        where UserID = prof_id) then
			update course
            set ProfessorID = prof_id
            where CourseID = course_id;
	end if;
end;



/*
Allows submission of rating
*/
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
--     update resource
-- 		set Rating =
--         (
--         Select avg(r.Score) 
--         from rating as r
--         where r.ResourceID = resource_ID
--         )
-- 	where ResourceID = resource_ID;
    
    
end;

/*
Gets details for a resource based on ResourceID
*/
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
    
from resource as R join user as U on R.Author = U.Name
left join note as N on R.ResourceID = N.ResourceID
left join website as W on R.ResourceID = W.ResourceID
left join video as V on R.ResourceID = V.ResourceID

where R.ResourceID = resource_ID;

end; 

/*
Returns average score of given ResourceID
*/
create function FN_Rating_Avg(resource_id int)
	returns decimal(2,1)
	begin
	declare r_avg decimal(2,1);
		select round(avg(Score), 1) into r_avg
		from rating
		where resource.ResourceID = resource_id;
	return r_avg;
end;

/*
Takes UserID and checks if user is professor
*/
create function FN_User_Isprofessor(user_id int)
	returns boolean
begin
    declare is_prof boolean;
		select IsProfessor into is_prof
        from user
        where user.UserID = user_id;
	return is_prof;
end;
    
