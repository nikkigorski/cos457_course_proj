/*
Lobster Notes Import Data
Gabrielle Akers
November 12, 2025
Gage White And nikki Gorski
November 14, 2025
*/

-- Insert sample subjects
INSERT INTO subject (Code, Name) VALUES ('CS', 'Computer Science');
INSERT INTO subject (Code, Name) VALUES ('MTH', 'Mathematics');
INSERT INTO subject (Code, Name) VALUES ('PHY', 'Physics');

-- Create sample professor and students
CALL SP_User_Create('Dr. Smith', 'CS', TRUE, 'password123');
CALL SP_User_Create('Alice Johnson', 'CS,MTH', FALSE, 'password123');
CALL SP_User_Create('Bob Williams', 'CS', FALSE, 'password123');

-- Create sample course with the professor
INSERT INTO course (Section, Name, Session, Year, Subject, CatalogNumber, ProfessorID)
VALUES ('001', 'Introduction to Programming', 'Fall', 2024, 'CS', 101, 1);

-- Enroll students in the course
INSERT INTO enrolled (StudentID, CourseID) VALUES (2, 1);
INSERT INTO enrolled (StudentID, CourseID) VALUES (3, 1);

-- Professor teaches the course
INSERT INTO teaches (ProfessorID, CourseID) VALUES (1, 1);

-- Import data scraped from Khan Academy
delimiter //
create procedure ImportData(in did int)
begin
    -- Load JSON
    declare j JSON;
    
    declare video_count int;
    declare image_count int;
    declare pdf_count int;
    declare website_count int;
    declare note_count int;
    
    select WebData into j from StageWebData where DataID = did and Imported = 0;

    -- Ensure fallback author exists
    insert ignore into user(Name, Password, IsProfessor) values('Web Scraped', 'webscraper', FALSE);

    insert into resource (Date, DateFor, Author, Topic, Keywords, Format, Rating, isVerified)
    values(CURDATE(), CURDATE(), COALESCE(JSON_UNQUOTE(JSON_EXTRACT(j, '$.Website[0].Author')), 'Web Scraped'), 'Main Page', null, 'website', 5.0, false);
    set @MainResourceID = LAST_INSERT_ID();
    
    insert into website(ResourceID, Link)
    values(
        @MainResourceID,
        JSON_UNQUOTE(JSON_EXTRACT(j, '$.Website[0].Link'))
    );

    -- Insert resources for videos
    if JSON_LENGTH(j, '$.Video') > 0 then
        
        set video_count = JSON_LENGTH(j, '$.Video');
        
       insert into resource (ResourceID, Date, DateFor, Author, Topic, Keywords, Format, Rating, isVerified)
        select
            rt.ResourceID,
            CURDATE(),
            CURDATE(),
            COALESCE(rt.Author, 'Web Scraped'),
            COALESCE(rt.Topic, 'n/a'),
            rt.Keywords,
            rt.Format,
            5.0,
            false
        from JSON_TABLE(
            cast(j as JSON),
            '$.resource[*]' COLUMNS(
                ResourceID int PATH '$.ResourceID',
                Format varchar(64) PATH '$.Format',
                Author varchar(255) PATH '$.Author',
                Topic varchar(255) PATH '$.Topic',
                Keywords varchar(255) PATH '$.Keywords'
            )
        ) as rt
        where rt.Format = 'video';

    -- Insert into video table using the same JSON_TABLE column names
    -- Use INSERT IGNORE so re-running the procedure won't fail on duplicate primary keys
    insert ignore into video (ResourceID, Duration, Link)
    select jt.ResourceID, jt.Duration, jt.Link
    from JSON_TABLE(
        j,
        '$.Video[*]' COLUMNS(
            ResourceID int PATH '$.ResourceID',
            Link varchar(2048) PATH '$.Link',
            Duration int PATH '$.Duration'
        )
    ) as jt;
    end if;

	-- Insert resources for images
    if JSON_LENGTH(j, '$.Image') > 0 then

        set image_count = (
        select count(*)
        from json_table(j, '$.Image[*]' columns(link_value varchar(2048) path '$.Link'))
        as jt_count
        where jt_count.link_value regexp '\\.(jpg|jpeg|png|gif|svg)$'
        );

        insert into resource (ResourceID, Date, DateFor, Author, Topic, Keywords, Format, Rating, isVerified)
        select
            rt.ResourceID,
            CURDATE(),
            CURDATE(),
            COALESCE(rt.Author, 'Web Scraped'),
            COALESCE(rt.Topic, 'n/a'),
            rt.Keywords,
            rt.Format,
            5.0,
            false
        from JSON_TABLE(
            cast(j as JSON),
            '$.resource[*]' COLUMNS(
                ResourceID int PATH '$.ResourceID',
                Format varchar(64) PATH '$.Format',
                Author varchar(255) PATH '$.Author',
                Topic varchar(255) PATH '$.Topic',
                Keywords varchar(255) PATH '$.Keywords'
            )
        ) as rt
        where rt.Format = 'image';
        
    -- Use INSERT IGNORE so re-running the procedure won't fail if child rows already exist
    -- Insert child image rows using ResourceID from the JSON
    insert ignore into image (ResourceID, Size, Link)
    select jt.ResourceID, jt.img_size, jt.link_value
    from JSON_TABLE(
        j,
        '$.Image[*]' COLUMNS(
            ResourceID int PATH '$.ResourceID',
            link_value varchar(2048) PATH '$.Link',
            img_size int unsigned PATH '$.Size'
        )
    ) as jt
    where jt.link_value regexp '\\.(jpg|jpeg|png|gif|svg)$';
    end if;
    
    -- Insert resources for pdf files
    if JSON_LENGTH(j, '$.pdf') > 0 then

        set pdf_count = JSON_LENGTH(j, '$.pdf');

        insert into resource (ResourceID, Date, DateFor, Author, Topic, Keywords, Format, Rating, isVerified)
        select
            rt.ResourceID,
            CURDATE(),
            CURDATE(),
            COALESCE(rt.Author, 'Web Scraped'),
            COALESCE(rt.Topic, 'n/a'),
            rt.Keywords,
            rt.Format,
            5.0,
            false
        from JSON_TABLE(
            cast(j as JSON),
            '$.resource[*]' COLUMNS(
                ResourceID int PATH '$.ResourceID',
                Format varchar(64) PATH '$.Format',
                Author varchar(255) PATH '$.Author',
                Topic varchar(255) PATH '$.Topic',
                Keywords varchar(255) PATH '$.Keywords'
            )
        ) as rt
        where rt.Format = 'pdf';
        
    -- Use INSERT IGNORE so re-running the procedure won't fail if child rows already exist
    insert ignore into pdf (ResourceID, Body, Link)
    select jt.ResourceID,
           CASE WHEN jt.body_value IS NULL OR jt.body_value = '' THEN jt.link_value ELSE jt.body_value END as Body,
           CASE WHEN jt.link_value IS NULL OR jt.link_value = '' THEN jt.body_value ELSE jt.link_value END as Link
    FROM JSON_TABLE(
        j,
        '$.pdf[*]' COLUMNS(
            ResourceID int PATH '$.ResourceID',
            link_value varchar(2048) PATH '$.Link',
            body_value varchar(2048) PATH '$.Body'
        )
    ) as jt
    where (jt.link_value regexp '\\.(pdf)$' or jt.body_value regexp '\\.(pdf)$');
    end if;
    
    -- exercises removed (not needed)
    
    set website_count = (
        select count(*)
        from JSON_TABLE(
            j, '$.Website[*]' COLUMNS(link_value varchar(2048) PATH '$.Link')
            ) as jt
        where jt.link_value regexp '^https?://');
        
    -- Insert resources for web links
    insert into resource (Date, DateFor, Author, Topic, Keywords, Format, Rating, isVerified)
    select
        CURDATE(),
        CURDATE(),
        COALESCE(rt.Author, 'Web Scraped'),
        COALESCE(rt.Topic, 'n/a'),
        rt.Keywords,
        rt.Format,
        5.0,
        false
    from JSON_TABLE(
        cast(j as JSON),
        '$.resource[*]' COLUMNS(
            Format varchar(64) PATH '$.Format',
            Author varchar(255) PATH '$.Author',
            Topic varchar(255) PATH '$.Topic',
            Keywords varchar(255) PATH '$.Keywords',
            link_value varchar(2048) PATH '$.Link'
        )
    ) as rt
    where rt.Format = 'website' and rt.link_value regexp '^https?://';

    -- Use INSERT IGNORE to avoid duplicate-key errors when re-running imports
    insert ignore into website (ResourceID, Link)
    select jt.ResourceID, jt.link_value
    from JSON_TABLE(
        j,
        '$.Website[*]' COLUMNS(
            ResourceID int PATH '$.ResourceID',
            link_value varchar(2048) PATH '$.Link'
        )
    ) as jt
    where jt.link_value regexp '^https?://';
    
    -- Insert resources for notes
    if JSON_LENGTH(j, '$.Note') > 0 then
    
		set note_count = JSON_LENGTH(j, '$.Note');
    
        insert into resource (Date, DateFor, Author, Topic, Keywords, Format, Rating, isVerified)
        select
            CURDATE(),
            CURDATE(),
            COALESCE(rt.Author, 'Web Scraped'),
            COALESCE(rt.Topic, 'n/a'),
            rt.Keywords,
            rt.Format,
            5.0,
            false
        from JSON_TABLE(
            cast(j as JSON), 
            '$.resource[*]' COLUMNS(
                Format varchar(64) PATH '$.Format',
                Author varchar(255) PATH '$.Author',
                Topic varchar(255) PATH '$.Topic',
                Keywords varchar(255) PATH '$.Keywords'
            )
        ) as rt
        where rt.Format = 'note';
        
    -- Use INSERT IGNORE so notes aren't re-inserted on procedure re-run
    insert ignore into note (ResourceID, Body)
    select jt.ResourceID, jt.note_body
    from JSON_TABLE(
        j,
        '$.Note[*]' COLUMNS(
            ResourceID int PATH '$.ResourceID',
            note_body varchar(2048) PATH '$.Body'
        )
    ) as jt;
        
		
        
	end if;

    -- Mark as imported
    update StageWebData set Imported = 1 where DataID = did;
end//
delimiter ;
