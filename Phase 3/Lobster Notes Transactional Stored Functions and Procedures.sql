/*
Stored Procedures and Functions
Author: Gage White
Date: 10 November 2025
Edited on December 7, 2025 by Gabrielle Akers to add transaction management
*/

/*
Procedure for creating a new user, specifying enrolled courses and if user is a professor
*/
delimiter //
create procedure SP_User_Create
(
    in user_name varchar(50),
    in enrolled_courses varchar(50),
    in professor_check boolean
)
begin
    declare exit handler for sqlexception
    begin
        rollback;
        signal sqlstate '45000'
        set message_text = 'User creation failed';
    end;

    start transaction;
    insert into user
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
    commit;
end//

delimiter //
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

delimiter //
create procedure SP_Update_User
(
    in user_id int unsigned,
    in new_name varchar(50)
)
begin
    declare exit handler for sqlexception
    begin
        rollback;
        signal sqlstate '45000'
        set message_text = 'User update failed. Rolled back to last saved version.';
    end;

    start transaction;
    update user
    set name = new_name
    where UserID = user_id;
    commit;
end//
delimiter ;

/*
Creates a new resource
*/
delimiter //
create procedure SP_Resource_Create
(
    in lecture_date date,
    in author_of varchar(50),
    in lecture_topic varchar(25),
    in resource_keywords varchar(25),
    in format_of varchar(7),
    in note_body varchar(2048),
    in web_address varchar(2048),
    in video_duration int unsigned,
    in image_size int unsigned
)
begin
    declare resource_id int;

    declare exit handler for sqlexception
    begin
        rollback;
        signal sqlstate '45000'
        set message_text = 'Transaction failed. Changes will be rolled back to last checkpoint.';
    end;

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
            insert into note (ResourceID, Body)
            values (resource_id, note_body);

        when 'Website' then
            insert into website (ResourceID, Link)
            values (resource_id, web_address);

        when 'Pdf' then
            insert into pdf (ResourceID, Body, Link)
            values (resource_id, note_body, web_address);

        when 'Image' then
            insert into image (ResourceID, Size, Link)
            values (resource_id, image_size, web_address);

        when 'Video' then
            insert into video (ResourceID, Duration, Link)
            values (resource_id, video_duration, web_address);
    end case;
    commit;
end//
delimiter ;

/*
Links professor to course
*/
delimiter //
create procedure SP_Course_IsProfessor
(
    in course_id int unsigned,
    in prof_id int unsigned
)
begin
    declare exit handler for sqlexception
    begin
        rollback;
        signal sqlstate '45000'
        set message_text = 'Course update failed';
    end;

    start transaction;
    if exists (
        select 1
        from Professor
        where UserID = prof_id
    ) then
        update Course
        set ProfessorID = prof_id
        where CourseID = course_id;
    end if;
    commit;
end//
delimiter ;

/*
Allows submission of rating
*/
delimiter //
create procedure SP_Rating_Rate
(
    in resource_id int unsigned,
    in rater varchar(50),
    in rating numeric(2,1),
    in date_of date
)
begin
    declare exit handler for sqlexception
    begin
        rollback;
        signal sqlstate '45000'
        set message_text = 'Rating submission failed. Please try again';
    end;

    start transaction;
    insert into rating
    (
        ResourceID,
		Poster,
		Score,
		Date
    )
    values
    (
        resource_id,
        rater,
        rating,
        date_of
    );
    commit;
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
		select round(avg(Score), 1) into r_avg
		from Rating
		where Resource.ResourceID = resource_id;
	return r_avg;
end//
delimiter ;

/*
Takes UserID and checks if user is professor
*/
delimiter //Name
create function FN_User_Isprofessor(user_id int)
	returns boolean
begin
    declare is_prof boolean;
		select IsProfessor into is_prof
        from User
        where User.UserID = user_id;
	return is_prof;
end//
delimiter ;