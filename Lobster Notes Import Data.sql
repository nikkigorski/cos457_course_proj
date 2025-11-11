/*
Lobster Notes Import Data
Gabrielle Akers
November 11, 2025
*/
create table StageWebData(
	DataID int unsigned auto_increment,
    WebData JSON not null,
    Imported int default 0
);

-- Import data scrapped from Khan Academy
delimiter $$
create procedure ImportKhanData(in did int)
begin
    -- Load JSON
    declare j JSON;
    select WebData into j from ImportData where DataID = did and Imported = 0;

    -- Insert main URL
    insert into Resource (Date, DateFor, Author, Topic, Keywords)
    values(CURDATE(), CURDATE(), 'Khan Academy', 'Main Page', NULL);
    set @MainResourceID = LAST_INSERT_ID();
    insert into Website(ResourceID, Link)
    values(
        @MainResourceID,
        JSON_UNQUOTE(JSON_EXTRACT(j, '$.url'))
    );

    -- Insert resources for videos
    insert into Resource (Date, DateFor, Author, Topic, Keywords)
	select
		CURDATE(),
		CURDATE(),
		'Khan Academy',
		'Video',
		null
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
        where Topic = 'n/a' and Author = 'Khan Academy'
        order by ResourceID desc
        limit JSON_LENGTH(j, '$.videos')
    ) as r
    join JSON_TABLE(
		j, 
        '$.videos[*]' COLUMNS(value varchar(2048) PATH '$')
	) as jt;

    -- Insert each exercise as Website
    insert into Resource (Date, DateFor, Author, Topic, Keywords)
    select
        CURDATE(),
        CURDATE(),
        'Khan Academy',
        'Exercise',
        null
    from JSON_TABLE(
		j, 
        '$.exercises[*]' COLUMNS(value varchar(2048) PATH '$')
	) as jt;

    insert into Website (ResourceID, Link)
    select r.ResourceID, jt.value
    from (
        select ResourceID
        from Resource
        where Topic = 'Exercises' and Author = 'Khan Academy'
        order by ResourceID desc
        limit JSON_LENGTH(j, '$.exercises')
    ) as r
    join JSON_TABLE(
		j, 
        '$.exercises[*]' COLUMNS(value varchar(2048) PATH '$')
	) as jt;

    -- Insert resources for links
    insert into Resource (Date, DateFor, Author, Topic, Keywords)
    select
        CURDATE(),
        CURDATE(),
        'Khan Academy',
        'Website',
        null
    from JSON_TABLE(
		j, 
        '$.links[*]' COLUMNS(value varchar(2048) PATH '$')
	) as jt
    where jt.value regexp '^https?://';

    insert into Website (ResourceID, Link)
    select r.ResourceID, jt.value
    from(
        select ResourceID
        from Resource
        where Topic = 'n/a' and Author = 'Khan Academy'
        order by ResourceID desc
        limit(
            select COUNT(*)
            from JSON_TABLE(
				j, 
                '$.links[*]' COLUMNS(value varchar(2048) PATH '$')
			) as jt
            where jt.value regexp '^https?://'
        )
    ) as r
    join(
        select value from JSON_TABLE(
			j, 
            '$.links[*]' COLUMNS(value varchar(2048) PATH '$')
		) as jt
        where jt.value regexp '^https?://'
    ) as jt;

    -- Mark as imported
    update StageWebData set Imported = 1 where DataID = did;
end //
delimiter ;
