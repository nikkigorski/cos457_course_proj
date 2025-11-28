/*
File: Stored Procedures and Functions - Lobster Notes.sql
Author: Gage White
Date: 10 November 2025
Description: Stored Procedures and Functions for Lobster Notes Project
*/
/*
Edited by Jove Emmons 15 November 2025
*/



/*
Procedure for creating a new user, specifying enrolled courses and if user is a professor
*/
delimiter //
drop procedure if exists SP_User_Create //
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

delimiter //
drop trigger if exists TR_User_AfterInsert //
create trigger TR_User_AfterInsert
after insert on User
for each row
begin
	if new.IsProfessor = True then
		insert into Professor (UserID, Badge)
        values (new.UserID, Null);
	else
		insert into Student (UserID)
        values (new.UserID);
	end if;
end//

delimiter ;

/*
Procedure for updating username by taking UserID for user to be altered
*/
delimiter //
drop procedure if exists SP_Update_User //
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
drop procedure if exists SP_Resource_Create //
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
			Date,
			DateFor,
			Author,
			Topic,
			Keywords,
			Format,
			isVerified
	)
	values
	(
			curdate(),
			lecture_date,
			author_of,
			lecture_topic,
			resource_keywords,
			format_of,
			false
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
		when 'pdf' then
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
			insert into Image
				(
					ResourceID,
                    Size,
                    Link
				)
                values
                (
					resource_id,
                    image_size,
                    web_address
				);
			when 'Video' then
				insert into Video
					(
						ResourceID,
                        Duration,
                        Link
					)
                    values
                    (
						resource_id,
                        video_duration,
                        web_address
					);

	end case;
    
	commit;
end//
delimiter ; 

/*
Links professor to course
*/
delimiter //
drop procedure if exists SP_Course_IsProfessor //
create procedure SP_Course_IsProfessor
(
	IN course_id int unsigned,
    IN prof_id int unsigned
)
begin
	if exists(
		select 1
        from Professor
        where UserID = prof_id) then
			update Course
            set ProfessorID = prof_id
            where CourseID = course_id;
	end if;
end//
delimiter ;



/*
Allows submission of rating
*/
delimiter //
drop procedure if exists SP_Rating_Rate //
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
--     update Resource
-- 		set Rating =
--         (
--         Select avg(r.Score) 
--         from Rating as r
--         where r.ResourceID = resource_ID
--         )
-- 	where ResourceID = resource_ID;
    
    
end//
delimiter ;


/*
Gets details for a resource based on ResourceID
*/
delimiter //
drop procedure if exists SP_Resource_Details //
create procedure SP_Resource_Details
(
	IN resource_ID int unsigned,
	OUT outRID int unsigned,
	OUT	outTopic varchar(25),
	OUT	outFormat varchar(7),
	OUT outDateMade date,
	OUT outDateFor date,
	OUT outAuthor varchar(50),
	OUT outBody varchar(2048),
	OUT outLink varchar(2048),
	OUT outDuration int unsigned,
	OUT outKeywords varchar(25),
	OUT outRating numeric(2,1),
	OUT outVerified boolean,
	OUT outSize int unsigned
)
begin
DECLARE outRID int unsigned;
DECLARE	outTopic varchar(25);
DECLARE	outFormat varchar(7);
DECLARE outDateMade date;
DECLARE outDateFor date;
DECLARE outAuthor varchar(50);
DECLARE outBody varchar(2048);
DECLARE outLink varchar(2048);
DECLARE outDuration int unsigned;
DECLARE outKeywords varchar(25);
DECLARE outRating numeric(2,1);
DECLARE outVerified boolean;
DECLARE outSize int unsigned;

select R.ResourceID, R.Date, R.DateFor, R.Author, R.Topic, R.Keywords, R.Format, R.isVerified
into outRID, outDateMade, outDateFor, outAuthor, outTopic, outKeywords, outFormat, outVerified
from Resource as R
where R.ResourceID = resource_ID;

select avg(score) into outRating
from Rating 
where ResourceID = resource_id;

set outBody = "";
set outLink = "";
set outSize = 0;
set outDuration = 0;


case outFormat
		when 'Note' then
			set outBody = FN_Resource_Body(resource_ID);
		when 'Website' then
			set outLink = FN_Resource_Link(resource_ID);
		when 'pdf' then
			set outBody = FN_Resource_Body(resource_ID);
			set outLink = FN_Resource_Link(resource_ID);
		when 'Image' then
			set outLink = FN_Resource_Link(resource_ID);
			select size into outsize
			from Image
			where resourceid = resource_ID;
		when 'Video' then
			set outLink = FN_Resource_Link(resource_ID);
			select Duration into outDuration
			from Video
			where ResourceID = resource_ID;
end case;

end//
delimiter ; 

/*
Returns body of requested resource
*/
delimiter //
drop function if exists FN_Resource_Body //
create function FN_Resource_Body(resource_id int)
	returns varchar(2048)
    reads sql data
	begin
		declare outbody varchar(2048);
		declare Reqformat varchar(7);
		select format into Reqformat
		from resource
		where resourceid = resource_ID;
		case format
			when 'Note' then
				select body into outbody
				from Note
				where resourceid = resource_ID;
			when 'pdf' then
				select body into outbody
				from Pdf
				where resourceid = resource_ID;
			return outbody;
		end case;
end//
delimiter ;


/*
Returns link of requested resource
*/
delimiter //
drop function if exists FN_Resource_Link //
create function FN_Resource_Link(resource_id int)
	returns varchar(2048)
	reads sql data
    begin
		declare outlink varchar(2048);
		declare Reqformat varchar(7);
		select format into Reqformat
		from Resource
		where resourceid = resource_ID;
		case format
			when 'pdf' then
				select link into outlink
				from Pdf
				where resourceid = resource_ID;
			when 'Image' then
				select link into outlink
				from Image
				where resourceid = resource_ID;
			when 'Video' then
				select link into outlink
				from Video
				where resourceid = resource_ID;
			when 'Website' then
				select link into outlink
				from Website
				where resourceid = resource_ID;
			return outlink;
		end case;
end//
delimiter ;


/*
Returns average score of given ResourceID
*/
delimiter //
drop function if exists FN_Rating_Avg //
create function FN_Rating_Avg(resource_id int)
	returns decimal(2,1)
    reads sql data
	begin
	declare r_avg decimal(2,1);
		select round(avg(Score), 1) into r_avg
		from Rating
		where Resource.ResourceID = resource_id;
	return r_avg;
end//
delimiter ;

/*
Takes UserID and checks if user is professor
*/
delimiter //
drop function if exists FN_User_Isprofessor //
create function FN_User_Isprofessor(user_id int)
	returns boolean
    reads sql data
begin
    declare is_prof boolean;
		select IsProfessor into is_prof
        from User
        where User.UserID = user_id;
	return is_prof;
end//
delimiter ;
    
