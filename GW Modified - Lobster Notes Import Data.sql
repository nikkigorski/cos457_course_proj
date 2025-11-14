/*
Lobster Notes Import Data
Gabrielle Akers
November 12, 2025
*/
create table StageWebData(
	DataID int unsigned auto_increment primary key,
    WebData JSON not null,
    Imported int default 0
);

-- Import data scraped from Khan Academy
delimiter //
create procedure ImportData(in did int)
begin
    -- Load JSON
    declare j JSON;
    
    declare video_count int;
    declare image_count int;
    declare pdf_count int;
    declare exercise_count int;
    declare website_count int;
    declare note_count int;
    
    select WebData into j from StageWebData where DataID = did and Imported = 0;

    -- Insert main URL
    insert into Resource (Date, DateFor, Author, Topic, Keywords, Format)
    values(CURDATE(), CURDATE(), 'Web Scraped', 'Main Page', null, 'Website');
    set @MainResourceID = LAST_INSERT_ID();
    
    insert into Website(ResourceID, Link)
    values(
        @MainResourceID,
        JSON_UNQUOTE(JSON_EXTRACT(j, '$.Website[0].Link'))
    );

    -- Insert resources for videos
    if JSON_LENGTH(j, '$.videos') > 0 then
        
        set video_count = JSON_LENGTH(J, '$.videos');
        
		insert into Resource (Date, DateFor, Author, Topic, Keywords, Format)
		select
			CURDATE(),
			CURDATE(),
			'Web Scraped',
			'n/a',
			null,
			'Video'
		from JSON_TABLE(
			cast(j as JSON),
			'$.videos[*]' COLUMNS(url varchar(2048) PATH '$')
		) as jt;
    
		-- Insert into Video table
		insert into Video (ResourceID, Duration, Link)
		select 
			r.ResourceID, 
			null, 
			jt.value
		from(
			select ResourceID
			from Resource
			where Topic = 'n/a' and Author = 'Web Scraped'
			order by ResourceID desc
			limit video_count
		) as r
		join JSON_TABLE(
			j, 
			'$.videos[*]' COLUMNS(value varchar(2048) PATH '$')
		) as jt;
    end if;

	-- Insert resources for iamges
    if JSON_LENGTH(j, '$.image') > 0 then
    
		set image_count = JSON_LENGTH(j, '$.image');
    
		insert into Resource(Date, DateFor, Author, Topic, Keywords, Format)
        select
			CURDATE(),
            CURDATE(),
            'Web Scraped',
            'n/a',
            null,
            'Image'
		from JSON_TABLE(
			j, 
			'$.image[*]' COLUMNS(value varchar(2048) PATH '$')
		) as jt
        where jt.value regexp '\\.(jpg|jpeg|png|gif)$';
        
        insert into Image (ResourceID, Size, Link)
        select r.ResourceID, jt.img_size, jt.link_value
        from(
            select ResourceID
            from Resource
            where Topic = 'n/a' and Author = 'Web Scraped'
            order by ResourceID desc
            limit image_count
        ) as r
        join JSON_TABLE(
            j,
            '$.image[*]' COLUMNS(
            link_value varchar(2048) PATH '$.Link',
            img_size int unsigned path '$.Size'
            )
        ) as jt
        where jt.value regexp '\\.(jpg|jpeg|png|gif)$';
    end if;
    
    -- Insert resources for pdf files
    if JSON_LENGTH(j, '$.pdf') > 0 then
    
		set pdf_count = JSON_LENGTH(j, '$.pdf');
    
		insert into Resource (Date, DateFor, Author, Topic, Keywords, Format)
		select
			CURDATE(),
			CURDATE(),
			'Web Scraped',
			'n/a',
			null,
            'pdf'
		from JSON_TABLE(
			j, 
			'$.pdf[*]' COLUMNS(value varchar(2048) PATH '$')
		) as jt;
        
        insert into pdf (ResourceID, Body, Link)
        select r.ResourceID, null, jt.value
        FROM (
            select ResourceID
            from Resource
            where Topic = 'n/a' AND Author = 'Web Scraped'
            order by ResourceID desc
            limit pdf_count
        ) as r
        join JSON_TABLE(
            j,
            '$.pdf[*]' COLUMNS(value varchar(2048) PATH '$')
        ) as jt
        where jt.value regexp '\\.pdf$';
    end if;
    
    -- Insert each exercise as Website
    if JSON_LENGTH(j, '$.exercises') > 0 then
    
		set exercise_count = JSON_LENGTH(j, '$.exercises');
    
		insert into Resource (Date, DateFor, Author, Topic, Keywords, Format)
		select
			CURDATE(),
			CURDATE(),
			'Web Scraped',
			'Exercises',
			null,
            'Website'
		from JSON_TABLE(
			j, 
			'$.exercises[*]' COLUMNS(value varchar(2048) PATH '$')
		) as jt;

		insert into Website (ResourceID, Link)
		select r.ResourceID, jt.value
		from (
			select ResourceID
			from Resource
			where Topic = 'Exercises' and Author = 'Web Scraped'
			order by ResourceID desc
			limit exercise_count
		) as r
		join JSON_TABLE(
			j, 
			'$.exercises[*]' COLUMNS(value varchar(2048) PATH '$')
		) as jt;
    end if;
    
    -- Insert resources for web links
    insert into Resource (Date, DateFor, Author, Topic, Keywords, Format)
    select
        CURDATE(),
        CURDATE(),
        'Web Scraped',
        'n/a',
        null,
        'Website'
    from JSON_TABLE(
		j, 
        '$.website[*]' COLUMNS(value varchar(2048) PATH '$')
	) as jt
    where jt.value regexp '^https?://';

    insert into Website (ResourceID, Link)
    select r.ResourceID, jt.value
    from(
        select ResourceID
        from Resource
        where Topic = 'n/a' and Author = 'Web Scraped'
        order by ResourceID desc
        limit website_count)
        -- (
--             select COUNT(*)
--             from JSON_TABLE(
-- 				j, 
--                 '$.website[*]' COLUMNS(value varchar(2048) PATH '$')
-- 			) as jt
--             where jt.value regexp '^https?://'
--         )
--     ) 
	as r
    join(
        select value from JSON_TABLE(
			j, 
            '$.website[*]' COLUMNS(value varchar(2048) PATH '$')
		) as jt
        where jt.value regexp '^https?://'
    ) as jt;
    
    -- Insert resources for notes
    if JSON_LENGTH(j, '$.note') > 0 then
    
		set note_count = JSON_LENGTH(j, '$.note');
    
		insert into Resource (Date, DateFor, Author, Topic, Keywords, Format)
		select
			CURDATE(),
			CURDATE(),
			'Web Scraped',
			'n/a',
			null,
            'Note'
		from JSON_TABLE(
			j, 
			'$.note[*]' COLUMNS(value varchar(2048) PATH '$')
		) as jt;
        
        insert into Note (ResourceID, Body)
        select r.ResourceID, jt.body
        from(
            select ResourceID
            from Resource
            where Topic = 'Note' and Author = 'Web Scraped'
            order by ResourceID desc
            limit note_count
        ) as r
        join JSON_TABLE(
            j,
            '$.note[*]' COLUMNS(body varchar(2048) PATH '$')
        ) as jt;
	end if;

    -- Mark as imported
    update StageWebData set Imported = 1 where DataID = did;
end//
delimiter ;
