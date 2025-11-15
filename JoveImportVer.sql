/*
Lobster Notes Import Data
Gabrielle Akers
November 12, 2025

Edits by Jove Emmons on November 14, 2025
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
    
    declare v_start_id int;
    declare i_start_id int;
    declare p_start_id int;
    declare e_start_id int;
    declare w_start_id int;
    declare n_start_id int;
    
    select WebData into j from StageWebData where DataID = did and Imported = 0;

	create temporary table if not exists NewResourceIDs
		(
			ResourceID int unsigned,
			format varchar(7),
			sequence_num int unsigned auto_increment primary key
        );
        
    -- Insert main URL
    insert into Resource (Date, DateFor, Author, Topic, Keywords, Format)
    values(CURDATE(), CURDATE(), 'Web Scraped', 'Main Page', null, 'Website');
    set @MainResourceID = LAST_INSERT_ID();
    
    insert into Website(ResourceID, Link)
    values(
        @MainResourceID,
        JSON_UNQUOTE(JSON_EXTRACT(j, '$.Website[0].Link'))
    );

    -- Insert resources for videos --------------------------------------------------------------------------------------------------------
    if JSON_LENGTH(j, '$.Video') > 0 then
        
        set v_start_id = (select max(ResourceID) from Resource) +1;
        
        
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
			'$.Video[*]' COLUMNS(Link varchar(2048) PATH '$.Link')
		) as jt;
        
        /*
        WIP alternative to the above starting at "JSON_TABLE(..."
        JSON_TABLE(
			cast(j as JSON),
			'$.Resource[*]' COLUMNS(Format varchar(7) PATH '$.Format',Topic varchar(25) PATH '$.Topic')
		) as jt
        where jt.format = "Video";
        -- then we can insert the topic for each scraped resource instance via jt.Topic, rather than just 'n/a'
        -- similar thing should be done with the other formats if its done here
        
        */
        
        
        
        
		
        insert into NewResourceIDs (ResourceID, Format)
        select ResourceID, Format
        from Resource
        where ResourceID >= v_start_id and Format = 'Video'
        order by ResourceID ASC;
        
		-- Insert into Video table
		insert into Video (ResourceID, Duration, Link)
		select 
			nri.ResourceID, 
			null, 
			jt.Link
		from NewResourceIDs as nri          -- get duration to not be null
		join(
			select jt_vid.Link,jt_vid.Duration,
				row_number() over () as sequence_num
			from json_table
            (
				j,
                '$.Video[*]' COLUMNS(Link varchar(2048) path '$.Link',Duration int unsigned path '$.Duration')
			) as jt_vid
            )as jt
		on nri.sequence_num = jt.sequence_num -- this matches only if nri was empty before this procedure call. it definitely won't work for the next formats
        -- to fix: maybe delete everything from nri before/after each format? but do it in a way that resets the auto increment, since some ways don't
        where nri.Format = 'Video';
    end if;

	-- Insert resources for images -------------------------------------------------------------------------------------------------
    if JSON_LENGTH(j, '$.Image') > 0 then
    
	set i_start_id = (select max(ResourceID) from Resource) + 1;
    
		insert into Resource (Date, DateFor, Author, Topic, Keywords, Format)
        select
			CURDATE(),
            CURDATE(),
            'Web Scraped',
            'n/a',
            null,
            'Image'
		from JSON_TABLE(j, '$.Image[*]' columns(link_value varchar(2048) path '$.Link')
		) as jt
        where jt.link_value regexp '\\.(jpg|jpeg|png|gif|svg)$';
        
        insert into Image (ResourceID, Size, Link)
        select nri.ResourceID, jt.img_size, jt.link_value
		from NewResourceIDs as nri
		join (
            select
                jt_img.link_value,
                jt_img.img_size,
                row_number() over () as sequence_num
            from JSON_TABLE(
                j,
                '$.Image[*]' COLUMNS(link_value varchar(2048) PATH '$.Link', img_size int unsigned path '$.Size')
            ) as jt_img
        where jt_img.link_value regexp '\\.(jpg|jpeg|png|gif|svg)$'
       )as jt
       on nri.sequence_num = jt.sequence_num
       where nri.Format = 'Image';
    end if;
    
    -- Insert resources for pdf files ------------------------------------------------------------------------------------------
    if JSON_LENGTH(j, '$.pdf') > 0 then
    
		set p_start_id = (select max(ResourceID) from Resource) + 1;
    
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
			'$.pdf[*]' COLUMNS(Link varchar(2048) path '$.Link')
		) as jt;
        
        insert into pdf (ResourceID, Body, Link)
        select nri.ResourceID, null, jt.Link
		from NewResourceIDs as nri
        join (
            select 
                jt_pdf.Link,
                row_number () over () as sequence_num
            from JSON_TABLE(
            j,
            '$.pdf[*]' COLUMNS(Link varchar(2048) path '$.Link')
        ) as jt_pdf
        where jt_pdf.Link regexp '\\.(pdf|Pdf|PDF)$'
        )as jt
        on nri.sequence_num = jt.sequence_num
        where nri.format = 'pdf';
        
    end if;
    
    -- Insert each exercise as Website -----------------------------------------------------------------------------------------------------------
    if JSON_LENGTH(j, '$.exercises') > 0 then
    
		set e_start_id = (select max(ResourceID) from Resource) + 1;
    
		insert into Resource(Date, DateFor, Author, Topic, Keywords, Format)
		select
			CURDATE(),
			CURDATE(),
			'Web Scraped',
			'Exercises',
			null,
            'Website'
		from JSON_TABLE(
			j, 
			'$.exercises[*]' COLUMNS(Link varchar(2048) path '$.Link')
		) as jt;


		insert into NewResourceIDs (ResourceID, Format)
        select ResourceID, format
        from Resource
        where ResourceID >= e_start_id and Topic = 'Exercises'
        order by ResourceID;
        
        insert into Website (ResourceID, Link)
		select nri.ResourceID, jt.Link
		from NewResourceIDs as nri
		
        join(
			select jt_ex.Link,
				row_number () over () as sequence_num
            from json_table(
			j, 
			'$.exercises[*]' COLUMNS(Link varchar(2048) path '$.Link')
		) as jt_ex
        )as jt
        on nri.sequence_num = jt.sequence_num
        where nri.Topic = 'Exercises';
        
    end if;
    
    if json_length(j, '$.Website') > 1 then
		set w_start_id = (select max(ResourceID) from Resource) + 1;
	
    -- Insert resources for web links ------------------------------------------------------------------------------------------------------
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
        '$.website[*]' COLUMNS(Link varchar(2048) PATH '$.Link', seq_num for ordinality)
	) as jt
    where jt.sequence_num > 1 regexp '^https?://';

	insert into NewResourceIDs (ResourceID, Format)
    select ResourceID, Format
    from Resource
    where ResourceID >= w_start_id and Topic = 'n/a' and Format = 'Website'
    order by ResourceID;


    insert into Website (ResourceID, Link)
    select nri.ResourceID, jt.Link
    from NewResourceIDs as nri
        join (
            select 
                jt_web.Link,
                row_number () over () as sequence_num
            from JSON_TABLE(
                j, 
                '$.Website[*]' COLUMNS(Link varchar(2048) PATH '$.Link', seq_num for ordinality)
            ) as jt_web
            where jt_web.seq_num > 1 and jt_web.Link regexp '^https?://'
        ) as jt
        on nri.sequence_num = jt.sequence_num
        where nri.Topic = 'n/a' AND nri.Format = 'Website';
	end if;
    
    -- Insert resources for notes -----------------------------------------------------------------------------------------------------
    if JSON_LENGTH(j, '$.Note') > 0 then
    
		set n_start_id = (select max(ResourceID) from Resource) + 1;
    
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
			'$.Note[*]' COLUMNS(note_body varchar(2048) path '$.Body')
		) as jt;
        
	insert into NewResourceIDs (ResourceID, Format)
    select ResourceID, Format
    from Resource
    where ResourceID >= n_start_id and Format = 'Note'
    order by ResourceID;
    
        insert into Note (ResourceID, Body)
        select nri.ResourceID, jt.note_body
        from NewResourceIDs as nri
		join (
            select
                jt_note.note_body,
                row_number () over () as sequence_num
            from json_table(
                j, '$.Note[*]' COLUMNS(note_body varchar(2048) path '$.Body')
            ) as jt_note
        ) as jt
        on nri.sequence_num = jt.sequence_num
        where nri.format = 'Note';

	end if;
    
    drop temporary table if exists NewResourceIDs;

    -- Mark as imported
    update StageWebData set Imported = 1 where DataID = did;
end//
delimiter ;