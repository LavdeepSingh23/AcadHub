
INSERT INTO USERS (user_id, name, username, password, role, phone) VALUES
(1, 'Krish',   'krish01', 'pass123', 'Student', '9876501001'),
(2, 'Lara',    'lara01',  'pass123', 'Student', '9876501002'),
(3, 'Rumneek', 'rum01',   'pass123', 'Faculty', '9876501003'),
(4, 'Aman',    'aman01',  'pass123', 'Student', '9876501004'),
(5, 'Simran',  'sim01',   'pass123', 'Student', '9876501005'),
(6, 'Raj',     'raj01',   'pass123', 'Faculty', '9876501006'),
(7, 'Admin1',  'admin01', 'adm@123', 'Admin',   '9876501007');

INSERT INTO STUDENT (roll_no, department, branch, semester, user_id, cgpa) VALUES
(101, 'CSE', 'COE', 4, 1, 8.5),
(102, 'CSE', 'COE', 4, 2, 7.8),
(103, 'CSE', 'COE', 4, 4, 9.1),
(104, 'CSE', 'COE', 4, 5, 6.9);

INSERT INTO FACULTY VALUES (201,'Professor','CSE',3), (202,'Asst. Professor','CSE',6);
INSERT INTO ADMIN (admin_id, user_id) VALUES (301, 7);

INSERT INTO COURSE (course_code, course_name, credits, semester, description) VALUES
('CS101', 'Database Management Systems', 4, 4, 'Covers SQL, normalization, transactions and DB design'),
('CS102', 'Operating Systems',           4, 4, 'Covers processes, memory management, scheduling and deadlock'),
('CS103', 'Computer Networks',           4, 4, 'Covers OSI model, TCP/IP, routing and network security');

INSERT INTO ENROLLMENT (enrollment_id, roll_no, course_code) VALUES
(1,101,'CS101'),(2,102,'CS101'),(3,103,'CS101'),(4,104,'CS101'),
(5,101,'CS102'),(6,102,'CS102'),(7,103,'CS103'),(8,104,'CS103');

INSERT INTO FACULTY_COURSE VALUES (1,201,'CS101'),(2,202,'CS102'),(3,201,'CS103');

INSERT INTO PYQ (pyq_id, course_code, question, year, exam_type) VALUES
(1,'CS101','Explain normalization up to 3NF with example.',  2023,'End Term'),
(2,'CS101','Write SQL query to find the class topper.',      2022,'Mid Term'),
(3,'CS102','Explain deadlock and prevention techniques.',    2023,'End Term'),
(4,'CS103','Draw ER diagram for a student-course system.',   2021,'Mid Term');

INSERT INTO STUDY_MATERIAL (material_id, course_code, faculty_id, title, material_type, content, upload_date) VALUES
(1,'CS101',201,'Normalization Notes','Notes','1NF, 2NF, 3NF explained with examples.','2025-04-10'),
(2,'CS101',201,'SQL Joins','Tutorials','INNER, LEFT, RIGHT JOIN with examples.','2025-04-11'),
(3,'CS102',202,'Deadlock Notes','Notes','Deadlock: processes wait indefinitely for resources.','2025-04-12'),
(4,'CS103',201,'ER Diagram Guide','Slides','Entities, attributes, relationships explained.','2025-04-13');

INSERT INTO ASSESSMENT (assessment_id, course_code, assessment_type, total_marks, passing_marks) VALUES
(1,'CS101','Mid Term', 50, 20),
(2,'CS101','End Term',100, 40),
(3,'CS102','Mid Term', 50, 20),
(4,'CS103','Mid Term', 50, 20);

INSERT INTO STUDENT_PERFORMANCE (performance_id, roll_no, assessment_id, marks_obtained, grade) VALUES
(1,101,1,42,'C'),(2,102,1,35,'F'),(3,103,1,48,'C'),(4,104,1,28,'F'),
(5,101,2,78,'A'),(6,102,2,65,'B+'),(7,103,2,88,'A+'),(8,104,2,40,'C'),
(9,101,3,38,'F'),(10,102,3,45,'C'),
(11,103,4,46,'A'),(12,104,4,40,'B+');

INSERT INTO ATTENDANCE (attendance_id, roll_no, course_code, attendance_date, status, remarks) VALUES
(1,101,'CS101','2025-04-01','Present',NULL),
(2,101,'CS101','2025-04-02','Absent','sick leave'),
(3,101,'CS101','2025-04-03','Present',NULL),
(4,102,'CS101','2025-04-01','Present',NULL),
(5,102,'CS101','2025-04-02','Present',NULL),
(6,102,'CS101','2025-04-03','Absent',NULL),
(7,103,'CS101','2025-04-01','Present',NULL),
(8,103,'CS101','2025-04-02','Present',NULL),
(9,103,'CS101','2025-04-03','Present',NULL),
(10,104,'CS101','2025-04-01','Absent','not informed'),
(11,104,'CS101','2025-04-02','Present',NULL),
(12,104,'CS101','2025-04-03','Absent',NULL);

-- UPDATE & DELETE


START TRANSACTION;
UPDATE STUDENT_PERFORMANCE SET marks_obtained = 45 WHERE roll_no = 104 AND assessment_id = 1;
COMMIT;

-- updating simran's cgpa after re-evaluation
START TRANSACTION;
UPDATE STUDENT SET cgpa = 7.2 WHERE roll_no = 104;
COMMIT;

-- updating grade for a student whose marks were corrected
UPDATE STUDENT_PERFORMANCE SET grade = 'C' WHERE roll_no = 104 AND assessment_id = 1;

-- savepoint demo
START TRANSACTION;
SAVEPOINT before_delete;
DELETE FROM ATTENDANCE WHERE roll_no = 104 AND attendance_date = '2025-04-03';
COMMIT;