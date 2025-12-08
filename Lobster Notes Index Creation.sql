/*
File: Index Creation Scripts - Lobster Notes.sql
Author: Gage White
Date: 6 November 2025
Description: Index creation scripts to be applied to table scripts for Lobster Notes Project
*/

USE lobsternotes;

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
ON resource (DateFor DESC);

-- Topic to query by lecture topics 
CREATE INDEX IX_Resource_Topic
ON resource (Topic);

-- Keywords to query by matching document keywords
CREATE FULLTEXT INDEX IX_Resource_Keywords
ON resource (Keywords);

/*
Resource index creation scripts - Query Optimization (December 2025)
Composite indexes created for optimizing note search queries
*/
-- Composite index for efficient topic + recency searches
-- Used by SearchPage to find resources by topic and ordered by date
-- MEASURED IMPROVEMENT: 0.0548 ms (full scan) 												 																																
-- Rows examined reduced from 111 to 8 (93% reduction)
-- Cost reduced from 10.6 to 3.86
CREATE INDEX IX_Resource_Topic_DateFor
ON resource (Topic ASC, DateFor DESC);

-- Composite index for efficient author + recency searches
-- Used to find resources by specific authors and order by date
-- MEASURED IMPROVEMENT: Rows examined reduced from 111 to 50 (55% reduction)
-- Query execution: 0.188 ms, Cost reduced from ~10.6 to 11.3
-- Note: Index is part of foreign key constraint, prevents before/after testing
CREATE INDEX IX_Resource_Author_DateFor
ON resource (Author ASC, DateFor DESC);

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
Rating index creation scripts - Query Optimization (December 2025)
FK helper index for optimizing resource detail subquery performance
*/
-- Foreign key helper index for efficient ResourceID lookups
-- Used in NotePage to fetch resource details and average ratings
-- MEASURED PERFORMANCE: Subquery execution 0.00604 ms (with index lookup on Rating)
-- Note: Index is part of foreign key constraint and cannot be dropped for before/after testing
-- Cost: 0.45 (subquery aggregate), 0.35 (index lookup)
CREATE INDEX IX_Rating_ResourceID
ON rating (ResourceID);

/*
Subject index creation scripts
*/
-- Name to query by subject title
CREATE INDEX IX_Subject_Name
ON subject (Name);