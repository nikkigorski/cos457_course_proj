# cos457_course_proj
course project for usm class cos457 2025

team name: Lobster Notes

group members: Nikki Gorski(Nikki.Gorski@maine.edu), Gabrielle Akers(Gabrielle.Akers@maine.edu), Gage White(Gage.White@maine.edu) and Jove Emmons(Jove.Emmons@maine.edu)

team leader: Nikki Gorski

project topic: lobster notes

------------------------------------------------------------------------------------------------------------------------------------------------------
Part 2 Roles and Deliverable

Team Member (GitHub ID):	Primary Focus Area	Deliverables with Primary Ownership

Gabrielle (144271532):	Database Structure & Constraints,	D2 (Schema Scripts), D7 (README)

Gage (64271462):	Advanced Database Features,	D3 (Stored Procedures/Functions), D6 (Query Optimization)

Nikki (126693450):	Data Acquisition & Cleaning,	D4 (Scraping Scripts), D5 (Sample Data/Cleaning Docs)

Jove (144271740):	Integration & Presentation,	D1 (Video Demo), D7 (README - Editor)

------------------------------------------------------------------------------------------------------------------------------------------------------

		
1. Recorded Video Demonstration (.mp4 or .mov)		
Member	Contribution

Gabrielle:	Database Creation & Constraints: Present running the schema scripts and demonstrating one constraint violation.	

Gage:	Advanced Features: Discuss and demonstrate stored procedures, functions, and triggers in action, and explain indexing.	

Nikki:	Data Scraping & Cleaning: Present the scraping output, show the cleaning results, and demonstrate data loading.	

Jove:	Queries & Editing: Run illustrative queries, summarize the project, and is the primary video editor responsible for the 8-minute limit.	

------------------------------------------------------------------------------------------------------------------------------------------------------		
3. MySQL Database Schema Scripts (.sql)		

Member	Contribution	

Gabrielle (Owner):	Writing table creation scripts (CREATE TABLE), defining all PK, FK, UNIQUE, NOT NULL, and CHECK constraints.	

Gage:	Writing the index creation scripts and adding comments to justify the index choices (feeding into D6).	

Nikki & Jove:	Reviewing scripts for syntax and logic to ensure they run sequentially from scratch. Assisting with table and index scripts.

------------------------------------------------------------------------------------------------------------------------------------------------------

4. Stored Procedures and Functions		

Team Member	Primary Task (Owner: Gage)	

Gage (Owner):	Design & Code: Writes the core SQL code for stored procedures and functions.	

Gabrielle:	Integration: Confirms that the procedures/functions correctly reference the finalized table and constraint names (D2).	

Nikki:	Testing Data: Executes the procedures/functions against the scraped/cleaned data (D4/D5) to ensure they work with real-world input.	

Jove:	Query Development: Integrates the procedures/functions into the demonstration queries (D1) and tests their efficiency (feeding into D6).

------------------------------------------------------------------------------------------------------------------------------------------------------		

5. Data Scraping Scripts and Documentation		

Team Member	Primary Task (Owner: Nikki)	

Nikki (Owner):	Code & Execute: Writes the Python scraping code, executes it, and ensures output is a clean file (.csv/.json).	

Jove:	Documentation Review: Reviews the source documentation and sample outputs written by Nikki for clarity and completeness for the final submission.	

Gabrielle:	Structure Alignment: Creates the necessary staging/import table(s) in the database (D2) to receive the scraped data.	

Gage:	Validation Logic: Tests error handling and validation logic to be included in the Python script.

------------------------------------------------------------------------------------------------------------------------------------------------------

		
7. Sample Data and Data Cleaning Documentation		

Team Member	Primary Task (Owner: Nikki)	

Nikki (Owner):	Cleaning Documentation: Writes the formal document detailing the cleaning and validation steps for the scraped data (D4) and initial sample data.	

Gabrielle:	Data Loading Script: Writes the SQL script to load the final cleaned data (from the file created in D4/D5) into the production tables (D2).	

Gage:	Constraint Validation: Develops small queries to verify that the loaded data adheres to all defined constraints (e.g., uniqueness, foreign keys).	

Jove:	Sample Data Creation: Creates the initial, non-scraped sample data needed for critical use cases not covered by the scraping (edge cases).	

------------------------------------------------------------------------------------------------------------------------------------------------------

8. Query Optimization Analysis		

Team Member	Primary Task (Owner: Gage)	

Gage (Owner):	Analysis & Documentation: Runs the before/after optimization tests for the two selected queries and documents the performance results and justifications.	

Jove:	Query Selection: Provides the two most performance-critical or complex queries for the video demonstration (D1) for optimization.	

Gabrielle:	Index Implementation: Implements or modifies the index creation scripts (D2) based on Gage's optimization strategy and verifies their successful creation.	

Nikki:	Data Scalability: Ensures there is a sufficient volume of test data (D5) loaded to produce meaningful and realistic query performance results.

------------------------------------------------------------------------------------------------------------------------------------------------------
		
10. Comprehensive README file (.md)		

Team Member	Primary Task (Owner: Jove)	

Jove (Owner):	Review & Assembly: Gathers all sections, performs the final review, formatting, and ensures the complete, step-by-step recreation is documented.	

Gabrielle:	Database Section: Documents the process for running the schema scripts (D2) and loading initial data (D5), including any necessary MySQL setup notes.	

Nikki:	Data Acquisition Section: Documents the command/steps for running the web scraping script (D4) and importing the output into MySQL.	

Gage:	Advanced Feature Section: Documents how to load and test the stored procedures and functions (D3) and provides a brief summary of the indexing strategy (D6).

------------------------------------------------------------------------------------------------------------------------------------------------------

Task Order and Deadlines		

Deadline	Task Name	

Th Nov. 6	Writing table and index creation scripts (Gabrielle lead)	

Sat Nov. 8	Data scraping scripts (Nikki lead)	

Sat Nov. 8	Sample data and cleaning docs (Nikki lead)	

Mon Nov. 10	Stored procedures and functions (Gage lead)	

Th Nov. 10	Query Optimization Analysis (Gage lead)	
Fri Nov 14	ReadME (Jove lead)	
Fri Nov 14	Recorded Video (Jove lead)	
