/**
View_StudentEnrollments lists all students enrolled in based on a subject
@author Gage White
@Date: 5 December 2025
*/
CREATE OR REPLACE VIEW View_StudentEnrollments AS
SELECT 
    u.UserID,
    u.Name AS StudentName,
    u.Courses AS MajorOrSubject,
    c.CourseID,
    c.Subject,
    c.CatalogNumber
FROM User u
JOIN Course c ON u.Courses = c.Subject
WHERE (u.IsProfessor = FALSE OR u.IsProfessor IS NULL);
