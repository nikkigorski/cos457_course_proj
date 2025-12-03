export const sampleNotes = [
  { ResourceID: 1,Title: "Computational music theory" ,Author: "mit ocw, lobster notes web scraper", Rating: "5", Date: "2025-11-15", Format: "Video", Url:"https://ocw.mit.edu/courses/21m-383-computational-music-theory-and-analysis-spring-2023/21m383-s23-video1a_tutorial_360p_16_9.mp4" },
  { ResourceID: 2,Title: "Computational Music teory and Analysis QUIZ 1" ,Author: "mit ocw, lobster notes web scraper", Rating: "4", Date: "2025-11-15", Format: "PDF", Url:"https://ocw.mit.edu/courses/21m-383-computational-music-theory-and-analysis-spring-2023/mit21m383s23_quiz_1.pdf" },
  { ResourceID: 3,Title: "Male northern cardinal in Central Park" ,Author: "khan accademy, lobster notes web scraper", Rating: "3", Date: "2025-11-11", Format: "Image", Url:"https://upload.wikimedia.org/wikipedia/commons/6/60/Male_northern_cardinal_in_Central_Park_%2852598%29.jpg" },
  { ResourceID: 4,Title: "text note" ,Author: "Nikki", Rating: "2", Date: "2025-11-27", Format: "Note", Body: "This is a sample text note created by Nikki in Lobster Notes application." },
  { ResourceID: 5,Title: "website note" ,Author: "Author5", Rating: "4", Date: "2024-05-05", Format: "Website", Url: "https://www.example.com" },
  { ResourceID: 6,Title: "test title6" ,Author: "Odo", Rating: "3", Date: "2024-06-15", Format: "PDF" },
  { ResourceID: 7,Title: "test title7" , Author: "William Riker", Rating: "5", Date: "2024-07-22", Format: "PDF" },
  { ResourceID: 8,Title: "test title8" ,Author: "Avery Brooks", Rating: "4", Date: "2024-08-30", Format: "PDF" },
  { ResourceID: 9,Title: "test title9" ,Author: "Diana Prince", Rating: "3", Date: "2024-09-15", Format: "PDF" },
  { ResourceID: 10,Title: "test title10" ,Author: "Author10", Rating: "4", Date: "2024-10-10", Format: "PDF" }
  
];

export const sampleResources = [
  { ResourceID: 1, CourseID: 457, Type: "PDF", Title: "Syllabus" },
  { ResourceID: 2, CourseID: 457, Type: "Video", Title: "Intro" },
  { ResourceID: 3, CourseID: 152, Type: "Website", Title: "Calc Help" },
  { ResourceID: 4, CourseID: 457, Type: "Note", Title: "Exam Review" },
];

export const sampleCourses = [
  { CourseID: 457, Section: "1", Name: "Database Systems", Session: "Fall", Year: 2025, Subject: "COS", CatalogNumber: 457, ProfessorID: 241},
  { CourseID: 152, Section: "1", Name: "Calculus II", Session: "Spring", Year: 2025, Subject: "MAT", CatalogNumber: 152, ProfessorID: 458},
  { CourseID: 360, Section: "1", Name: "Programming Languages", Session: "Summer", Year: 2025, Subject: "COS", CatalogNumber: 360, ProfessorID: 1925}
];

export const sampleStudents = [
  { UserID: 123, Name: "William Riker", Courses: "COS", IsProfessor: "False" },
  { UserID: 241, Name: "Avrey Brooks", Courses: "MAT", IsProfessor: "True" },
  { UserID: 351, Name: "Nana Vistor", Courses: "COS", IsProfessor: "False" },
  { UserID: 422, Name: "Diana Prince", Courses: "COS", IsProfessor: "False" },
  { UserID: 458, Name: "Odo", Courses: "MAT", IsProfessor: "True" }
];