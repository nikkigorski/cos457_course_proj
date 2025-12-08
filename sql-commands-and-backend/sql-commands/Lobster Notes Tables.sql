/*
Lobster Notes Tables
Gabrielle Akers
November 2, 2025
Edited on December 4, 2025
*/

-- Create database if it doesn't exist and use it
CREATE DATABASE IF NOT EXISTS lobsternotes;
USE lobsternotes;

create table subject(
	Code char(3),
    Name varchar(50) not null,
    primary key(Code)
);

create table user(
	UserID int unsigned auto_increment,
    Name varchar(50) not null unique,
    Courses varchar(50) null,
	Password varchar(50) not null,
    IsProfessor boolean null,
    primary key(UserID)
);

create table student(
	UserID int unsigned,
	primary key(UserID),
    foreign key(UserID) references user(UserID) on update cascade on delete cascade
);

create table professor(
	UserID int unsigned,
    Badge boolean null,
    primary key(UserID),
    foreign key(UserID) references user(UserID) on update cascade on delete cascade
);

create table course(
	CourseID int unsigned auto_increment,
    Section varchar(24) null check(REGEXP_LIKE(Section, '^[A-Za-z0-9]+$')),
    Name varchar(50) not null,
    Session varchar(6) not null check(Session in('Spring', 'Summer', 'Fall', 'Winter')),
    Year numeric(4,0) not null check(Year>2000),
    Subject char(3) not null,
    CatalogNumber numeric(3,0),
    ProfessorID int,
    primary key(CourseID),
    foreign key(Subject) references subject(Code) on update cascade on delete cascade
);

create table resource(
	ResourceID int unsigned auto_increment,
    Date date not null,
    DateFor date not null,
    Author varchar(50) not null,
    Topic varchar(25) not null,
    Keywords varchar(25) null,
    Rating numeric(2,1),
    Format varchar(7) not null check(Format in('Note', 'Video', 'Website', 'Pdf', 'Image')),
    isVerified boolean null,
    primary key(ResourceID),
    foreign key(Author) references user(Name) on update cascade on delete cascade
);

create table rating(
	RatingID int unsigned auto_increment,
    Poster varchar(50) not null,
    ResourceID int unsigned not null,
    Score numeric(2,1) not null check(Score >= 0.0 and Score <= 5.0),
    Date date not null,
    primary key(RatingID),
    foreign key(Poster) references user(Name) on update cascade on delete cascade,
    foreign key(ResourceID) references resource(ResourceID) on update cascade on delete cascade
);

create table note(
	ResourceID int unsigned,
    Body varchar(2048) not null,
    primary key(ResourceID),
    foreign key(ResourceID) references resource(ResourceID) on update cascade on delete cascade
);

create table pdf(
	ResourceID int unsigned,
    Body varchar(2048) null,
	Link varchar(2048) null check(Link regexp '\\.pdf$' and Link regexp '^https?://'),
    primary key(ResourceID),
    foreign key(ResourceID) references resource(ResourceID) on update cascade on delete cascade
);

create table image(
	ResourceID int unsigned,
    Size int unsigned not null check(Size > 0),
	Link varchar(2048) null check(Link regexp '\\.(jpg|jpeg|png|gif)$' and Link regexp '^https?://'),
    primary key(ResourceID),
    foreign key(ResourceID) references resource(ResourceID) on update cascade on delete cascade
);

create table video(
	ResourceID int unsigned,
    Duration int unsigned not null check(Duration > 0),
    Link varchar(2048) null check(Link is null or Link regexp '^https?://'),
    primary key(ResourceID),
    foreign key(ResourceID) references resource(ResourceID) on update cascade on delete cascade
);

create table website(
	ResourceID int unsigned,
    Link varchar(2048) not null check(Link regexp '^https?://'),
    primary key(ResourceID),
    foreign key(ResourceID) references resource(ResourceID) on update cascade on delete cascade
);

create table enrolled(
    StudentID int unsigned,
    CourseID int unsigned,
    primary key(StudentID, CourseID),
    foreign key(StudentID) references student(UserID) on update cascade on delete cascade,
    foreign key(CourseID) references course(CourseID) on update cascade on delete cascade
);
create table teaches(
	ProfessorID int unsigned,
	CourseID int unsigned,
	primary key(ProfessorID, CourseID),
	foreign key(ProfessorID) references professor(UserID) on update cascade on delete cascade,
    foreign key(CourseID) references course(CourseID) on update cascade on delete cascade
);

-- Average Rating attribute of Resource with Scores
-- STORED PROCEDURES AND TRIGGERS CANNOT BE LOADED VIA PIPE
-- Use /home/nikki.gorski/databases/cos457_course_proj/sql-commands-and-backend/load_procedures.py after init
-- create procedure AverageRating(in resID int)
-- begin
-- 	update Resource
-- 	set Rating = (
-- 		select round(avg(Score), 1)
--         from Rating
--         where ResourceID = resID
-- 	)
--     where ResourceID = resID;
-- end;

-- Update Rating attribute of Resource on insert
-- TRIGGERS DISABLED - Cannot pipe triggers to mysql
-- create trigger InsertRating
-- after insert on Rating
-- for each row
-- begin
-- 	call AverageRating(new.ResourceID);
-- end;

-- Update Rating using trigger
-- create trigger UpdateRating
-- after update on Rating
-- for each row
-- begin
-- 	call AverageRating(new.ResourceID);
-- end;






