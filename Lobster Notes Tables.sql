/*
Lobster Notes Tables
Gabrielle Akers
November 2, 2025
Edited by Gabrielle Akers on November 12, 2025
Edited by Jove Emmons on November 12, 2025, and November 13, 2025
*/

-- Create database statement.
CREATE DATABASE LobsterNotes;

-- Statement to choose LobsterNotes as the default database for SQL statement execution.
USE LobsterNotes;

create table User(
	UserID int unsigned auto_increment,
    Name varchar(50) not null unique,
    Courses varchar(50) null,
    IsProfessor boolean null,
    primary key(UserID)
);

create table Subject(
	Code char(3),
    Name varchar(50) not null,
    primary key(Code)
);

-- Section check is on a separate line.
-- Year check is a Trigger.
create table Course(
	CourseID int unsigned auto_increment,
    Section varchar(24) null,
    Name varchar(50) not null,
    Session varchar(6) not null check(Session in('Spring', 'Summer', 'Fall', 'Winter')),
    Year numeric(4,0) not null,
    Subject char(3) not null,
    CatalogNumber numeric(3,0),
    ProfessorID int,
    CONSTRAINT course_section_chk CHECK (REGEXP_LIKE(Section, '^[A-Za-z0-9]+$')),
    primary key(CourseID),
    foreign key(Subject) references Subject(Code) on update cascade
);

create table Resource(
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
    foreign key(Author) references User(Name) on update cascade
);

create table Note(
	ResourceID int unsigned,
    Body varchar(2048) not null,
    primary key(ResourceID),
    foreign key(ResourceID) references Resource(ResourceID) on update cascade
);

create table pdf(
	ResourceID int unsigned,
    Body varchar(2048) null,
	Link varchar(2048) null check(Link regexp '\\.pdf$' and Link regexp '^https?://'),
    primary key(ResourceID),
    foreign key(ResourceID) references Resource(ResourceID) on update cascade
);

create table Image(
	ResourceID int unsigned,
    Size int unsigned not null check(Size > 0),
	Link varchar(2048) null check(Link regexp '\\.(jpg|jpeg|png|gif)$' and Link regexp '^https?://'),
    primary key(ResourceID),
    foreign key(ResourceID) references Resource(ResourceID) on update cascade
);

create table Video(
	ResourceID int unsigned,
    Duration int unsigned not null check(Duration > 0),
    Link varchar(2048) null check(Link is null or Link regexp '^https?://'),
    primary key(ResourceID),
    foreign key(ResourceID) references Resource(ResourceID) on update cascade
);

create table Website(
	ResourceID int unsigned,
    Link varchar(2048) not null check(Link regexp '^https?://'),
    primary key(ResourceID),
    foreign key(ResourceID) references Resource(ResourceID) on update cascade
);

create table Student(
	UserID int unsigned,
	primary key(UserID),
    foreign key(UserID) references User(UserID) on update cascade
);

/*	I think the Poster foreign key will need to be referencing a User, rather than a Student
	The Student relation doesn't contain the Name attribute, so the only way we can reference a Name is by referencing User
    We can make sure that the poster is a Student through triggers
*/
create table Rating(
	RatingID int unsigned auto_increment,
    Poster varchar(50) not null,
    ResourceID int unsigned not null,
    Score numeric(2,1) not null check(Score >= 0.0 and Score <= 5.0),
    Date date not null,
    primary key(RatingID),
    foreign key(Poster) references User(Name) on update cascade,
    foreign key(ResourceID) references Resource(ResourceID) on update cascade
);

-- Average Rating attribute of Resource with Scores
delimiter $$
create procedure AverageRating(in resID int)
begin
	update Resource
	set Rating = (
		select round(avg(Score), 1)
        from Rating
        where ResourceID = resID
	)
    where ResourceID = resID;
end $$
delimiter ; 

-- Update Rating attribute of Resource on insert
delimiter $$
create trigger InsertRating
after insert on Rating
for each row
begin
	call AverageRating(new.ResourceID);
end $$
delimiter ;

-- Update Rating using trigger
delimiter $$
create trigger UpdateRating
after update on Rating
for each row
begin
	call AverageRating(new.ResourceID);
end $$
delimiter ;

create table Professor(
	UserID int unsigned,
    Badge boolean null,
    primary key(UserID),
    foreign key(UserID) references User(UserID) on update cascade
);


-- To make sure that the Year input for a new instance in Course is valid.
delimiter $$
CREATE TRIGGER new_course_year_chk
BEFORE INSERT ON `Course`
FOR EACH ROW
BEGIN
	IF (new.Year<2000 OR new.Year<=year(curdate())) THEN
		SIGNAL SQLSTATE "45000";
	END IF;
END $$
delimiter ;


/*
    WIP
	To make sure that the user posting a rating is a student
    Send signal if the UserID associated with the Name inserted is not in Student
*/
delimiter $$
CREATE TRIGGER rating_poster_chk
BEFORE INSERT ON Rating
FOR EACH ROW
BEGIN
	if(SELECT UserID
		FROM User natural join Student as Student_Name
        where new.Poster = Student_Name.Name LIMIT 1) then
			SIGNAL SQLSTATE "45000";
	END IF;
END $$
delimiter ;