/*
File: Index Creation Scripts - Lobster Notes.sql
Author: Gage White
Date: 6 November 2025
Description: Index creation scripts to be applied to table scripts for Lobster Notes Project
*/

USE LobsterNotes;

/*
User index creation scripts
*/

-- Name to query by username
CREATE UNIQUE INDEX UK_User_Name
ON user (Name);


/*
Course index creation scripts
*/
-- References Professor teaching course
CREATE INDEX IX_Course_ProfessorID
ON course (ProfessorID);

-- Name to query by course
CREATE INDEX IX_Course_Name
ON course (Name);

-- Year to query by year class is offered
CREATE INDEX IX_Course_Year
ON course (Year DESC);

-- Connects Course with CatalogNumber since they will likely be queried together
CREATE INDEX IX_Course_Subject_CatalogNumber
ON course (Subject, CatalogNumber ASC);

/*
Resource index creation scripts
*/
-- DateFor to query by class date the note is for
CREATE INDEX IX_Resource_DateFor
ON Resource (DateFor DESC);

-- Topic to query by lecture topics 
CREATE INDEX IX_Resource_Topic
ON resource (Topic);

-- Keywords to query by matching document keywords
CREATE FULLTEXT INDEX IX_Resource_Keywords
ON Resource (Keywords);

/*
Rating index creation scripts
*/

-- Date to query by date rated
CREATE INDEX IX_Rating_Date
ON rating (Date DESC);

-- Poster to create index for FK and query poster
CREATE INDEX IX_Rating_Poster
ON rating (Poster);

/*
Subject index creation scripts
*/
-- Name to query by subject title
CREATE INDEX IX_Subject_Name
ON subject (Name);