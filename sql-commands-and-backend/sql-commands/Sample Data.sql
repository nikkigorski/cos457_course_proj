-- Quick sample data for testing
USE lobsternotes;

-- Add subjects
INSERT IGNORE INTO Subject (Code, Name) VALUES 
  ('CS', 'Computer Science'),
  ('MATH', 'Mathematics');

-- Add a professor user
INSERT INTO User (Name, Courses, IsProfessor) VALUES ('Dr. Test Professor', 'CS,MATH', TRUE);
SET @prof_id = LAST_INSERT_ID();
INSERT INTO Professor (UserID, Badge) VALUES (@prof_id, NULL);

-- Add courses for that professor  
INSERT INTO Course (Subject, CatalogNumber, Name, Section, Year, Session, ProfessorID)
VALUES 
  ('CS', 457, 'Database Systems', '01', 2025, 'Spring', @prof_id),
  ('CS', 450, 'Software Engineering', '02', 2025, 'Spring', @prof_id),
  ('MATH', 251, 'Calculus III', '01', 2025, 'Spring', @prof_id);

SELECT 'Sample data created. Professor ID:', @prof_id;
