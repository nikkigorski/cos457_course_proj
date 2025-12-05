/*
Lobster Notes Import Data
Gabrielle Akers
November 12, 2025
Gage White And Nikki Gorski
November 14, 2025
Jove Emmons
November 15, 2025
Jove Emmons
November 27, 2025
*/
create table if not exists StageWebData(
	DataID int unsigned auto_increment primary key,
    WebData JSON not null,
    Imported int default 0
);

-- Import data scraped from Khan Academy
delimiter //
create procedure ImportData(in did int)
this_proc:begin
    -- Load JSON
    declare j JSON;
    declare resourceCount int unsigned;
    declare noteCount int unsigned;
    declare websiteCount int unsigned;
    declare pdfCount int unsigned;
    declare imageCount int unsigned;
    declare videoCount int unsigned;

    declare lecture_date date; -- done
    declare author_of varchar(50); -- done
    declare lecture_topic varchar(25); -- done
    declare resource_keywords varchar(25); -- done
    declare format_of varchar(7); -- done
    declare note_body varchar(2048);
    declare web_address varchar(2048);
    declare video_duration int unsigned;
    declare image_size int unsigned;
    
    set j = null;
    
    select WebData into j from StageWebData where DataID = did and Imported = 0;

    if j is null then
        leave this_proc;
    end if;



    -- Ensure canonical fallback author exists so FK on Resource.Author won't fail
    insert ignore into User(Name) values('Web Scraped',"",True);

    

    set resourceCount = 0;
    set noteCount = 0;
    set websiteCount = 0;
    set pdfCount = 0;
    set imageCount = 0;
    set videoCount = 0;
    /*
        -while loop over resource array
        -get the info we can from the resource entry
            -check the format value
        -based on the value, check the format arrays
        -get the values we need from that
        -call sp_resource_create with those values, others as dummy values - still within the formats case
    repeat


    need a counter of formats so we can tell which one to use from array
    start at 0, go up by 1 each time we get a format inst
    use that with for ordinality column in json_table to get the right one

    */


    set resource_keywords = null;

    while resourceCount < json_length(j,'$.Resource') do
        set resourceCount = resourceCount + 1;

        select COALESCE(rjt.rdatefor,CURDATE()),
        COALESCE(rjt.rauthor, 'Web Scraped'),
        COALESCE(rjt.rtopic, 'n/a'),
        rjt.rFormat
        into lecture_date, author_of, lecture_topic, format_of
        from json_table(
            cast(j as json),
            '$.Resource[*]' COLUMNS(
                Count for ordinality,
                rdatefor date PATH '$.DateFor',
                rauthor varchar(50) path '$.Author',
                rtopic varchar(25) path '$.Topic',
                rFormat varchar(7) path '$.Format'
                )
        ) as rjt
        where rjt.Count = resourceCount;
        
        case format_of
            when 'Note' then -- needs body
                set noteCount = noteCount + 1;
                select njt.nbody into note_body
                from json_table(
                    cast(j as json),
                    '$.Note[*]' COLUMNS(
                        Count for ordinality,
                        nbody varchar(2048) path '$.Body'
                    )
                ) as njt
                where njt.Count = noteCount;
                call SP_Resource_Create(lecture_date,author_of,lecture_topic,
                    resource_keywords,format_of,note_body,"",
                    0,0);

            when 'Website' then -- needs link
                set websiteCount = websiteCount + 1;
                select wjt.wlink into web_address
                from json_table(
                    cast(j as json),
                    '$.Website[*]' COLUMNS(
                        Count for ordinality,
                        wlink varchar(2048) path '$.Link'
                    )
                )as wjt
                where wjt.Count = websiteCount;
                call SP_Resource_Create(lecture_date,author_of,lecture_topic,
                    resource_keywords,format_of,"",web_address,
                    0,0);

            when 'pdf' then -- needs body, link
                set pdfCount = pdfCount + 1;
                select pjt.pbody, pjt.plink
                into note_body, web_address
                from json_table(
                    cast(j as json),
                    '$.pdf[*]' COLUMNS(
                        Count for ordinality,
                        pbody varchar(2048) path '$.Body',
                        plink varchar(2048) path '$.Link'
                    )
                )as pjt
                where pjt.Count = pdfCount;
                call SP_Resource_Create(lecture_date,author_of,lecture_topic,
                    resource_keywords,format_of,note_body,web_address,
                    0,0);

            when 'Image' then -- needs size, link
                set imageCount = imageCount + 1;
                select ijt.isize, ijt.ilink
                into image_size, web_address
                from json_table(
                    cast(j as json),
                    '$.Image[*]' COLUMNS(
                        Count for ordinality,
                        isize int unsigned path '$.Size',
                        ilink varchar(2048) path '$.Link'
                    )
                )as ijt
                where ijt.Count = imageCount;
                call SP_Resource_Create(lecture_date,author_of,lecture_topic,
                    resource_keywords,format_of,"",web_address,
                    0,image_size);

            when 'Video' then -- needs duration, link
                set videoCount = videoCount + 1;
                select vjt.vduration, vjt.vlink
                into video_duration, web_address
                from json_table(
                    cast(j as json),
                    '$.Video[*]' COLUMNS(
                        Count for ordinality,
                        vlink varchar(2048) path '$.Link',
                        vduration int unsigned path '$.Duration'
                    )
                )as vjt
                where vjt.Count = videoCount;
                call SP_Resource_Create(lecture_date,author_of,lecture_topic,
                    resource_keywords,format_of,"",web_address,
                    video_duration,0);

        end case;
        

    end while;

    update StageWebData set Imported = 1 where DataID = did;




end//
delimiter ;
