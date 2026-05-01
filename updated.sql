-- LMS Database Project
-- UCS310 - DBMS
-- Group: Lavdeep Singh(1024030107), Kriti(1024030111), Ramneek Kaur(1024030113)
-- Lab Instructor: Mrs. Vibhuti Sharma
-- 2025-2026




-- TABLE CREATION

CREATE TABLE USERS (
    user_id  INT PRIMARY KEY,
    name     VARCHAR(100) NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    role     VARCHAR(20) NOT NULL CHECK (role IN ('Admin','Faculty','Student'))
);

CREATE TABLE STUDENT (
    roll_no    INT PRIMARY KEY,
    department VARCHAR(50) NOT NULL,
    branch     VARCHAR(50) NOT NULL,
    semester   INT NOT NULL CHECK (semester BETWEEN 1 AND 8),
    user_id    INT UNIQUE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES USERS(user_id) ON DELETE CASCADE
);

CREATE TABLE FACULTY (
    faculty_id  INT PRIMARY KEY,
    designation VARCHAR(50),
    department  VARCHAR(50),
    user_id     INT UNIQUE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES USERS(user_id) ON DELETE CASCADE
);

CREATE TABLE ADMIN (
    admin_id     INT PRIMARY KEY,
    user_id      INT UNIQUE NOT NULL,
    access_level VARCHAR(30) DEFAULT 'Full',
    FOREIGN KEY (user_id) REFERENCES USERS(user_id) ON DELETE CASCADE
);

CREATE TABLE COURSE (
    course_code VARCHAR(10) PRIMARY KEY,
    course_name VARCHAR(100) NOT NULL,
    credits     INT DEFAULT 4,
    semester    INT NOT NULL
);

-- M:N student-course
CREATE TABLE ENROLLMENT (
    enrollment_id INT PRIMARY KEY,
    roll_no       INT NOT NULL,
    course_code   VARCHAR(10) NOT NULL,
    UNIQUE (roll_no, course_code),
    FOREIGN KEY (roll_no)     REFERENCES STUDENT(roll_no) ON DELETE CASCADE,
    FOREIGN KEY (course_code) REFERENCES COURSE(course_code) ON DELETE CASCADE
);

-- M:N faculty-course
CREATE TABLE FACULTY_COURSE (
    id          INT PRIMARY KEY,
    faculty_id  INT NOT NULL,
    course_code VARCHAR(10) NOT NULL,
    FOREIGN KEY (faculty_id)  REFERENCES FACULTY(faculty_id) ON DELETE CASCADE,
    FOREIGN KEY (course_code) REFERENCES COURSE(course_code) ON DELETE CASCADE
);

CREATE TABLE PYQ (
    pyq_id      INT PRIMARY KEY,
    course_code VARCHAR(10) NOT NULL,
    question    TEXT NOT NULL,
    year        INT,
    exam_type   VARCHAR(50),
    FOREIGN KEY (course_code) REFERENCES COURSE(course_code) ON DELETE CASCADE
);

CREATE TABLE STUDY_MATERIAL (
    material_id   INT PRIMARY KEY,
    course_code   VARCHAR(10) NOT NULL,
    faculty_id    INT NOT NULL,
    title         VARCHAR(100),
    material_type ENUM('Notes','Slides','Tutorials','Reference') DEFAULT 'Notes',
    content       TEXT,
    upload_date   DATE,
    FOREIGN KEY (course_code) REFERENCES COURSE(course_code) ON DELETE CASCADE,
    FOREIGN KEY (faculty_id)  REFERENCES FACULTY(faculty_id) ON DELETE CASCADE
);

CREATE TABLE ASSESSMENT (
    assessment_id   INT PRIMARY KEY,
    course_code     VARCHAR(10) NOT NULL,
    assessment_type VARCHAR(50),
    total_marks     INT CHECK (total_marks > 0),
    FOREIGN KEY (course_code) REFERENCES COURSE(course_code) ON DELETE CASCADE
);

CREATE TABLE STUDENT_PERFORMANCE (
    performance_id INT PRIMARY KEY,
    roll_no        INT NOT NULL,
    assessment_id  INT NOT NULL,
    marks_obtained INT CHECK (marks_obtained >= 0),
    UNIQUE (roll_no, assessment_id),
    FOREIGN KEY (roll_no)       REFERENCES STUDENT(roll_no) ON DELETE CASCADE,
    FOREIGN KEY (assessment_id) REFERENCES ASSESSMENT(assessment_id) ON DELETE CASCADE
);

CREATE TABLE ATTENDANCE (
    attendance_id   INT PRIMARY KEY,
    roll_no         INT NOT NULL,
    course_code     VARCHAR(10) NOT NULL,
    attendance_date DATE NOT NULL,
    status          ENUM('Present','Absent') NOT NULL,
    FOREIGN KEY (roll_no)     REFERENCES STUDENT(roll_no) ON DELETE CASCADE,
    FOREIGN KEY (course_code) REFERENCES COURSE(course_code) ON DELETE CASCADE
);

-- ALTER TABLE

ALTER TABLE USERS ADD COLUMN phone VARCHAR(15) DEFAULT NULL;
ALTER TABLE STUDENT ADD COLUMN cgpa DECIMAL(4,2) DEFAULT 0.00;
ALTER TABLE STUDENT_PERFORMANCE ADD COLUMN grade CHAR(2) DEFAULT NULL;
ALTER TABLE ASSESSMENT ADD COLUMN passing_marks INT DEFAULT 20;
ALTER TABLE ATTENDANCE ADD COLUMN remarks VARCHAR(100) DEFAULT NULL;
ALTER TABLE COURSE ADD COLUMN description VARCHAR(255) DEFAULT NULL;

-- DATA INSERTION

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

-- VIEWS

CREATE OR REPLACE VIEW student_performance_report AS
SELECT s.roll_no, u.name, c.course_name, a.assessment_type,
       sp.marks_obtained, a.total_marks,
       (sp.marks_obtained * 100 / a.total_marks) AS percentage
FROM STUDENT s
JOIN USERS u   ON s.user_id = u.user_id
JOIN ENROLLMENT e ON s.roll_no = e.roll_no
JOIN COURSE c  ON e.course_code = c.course_code
JOIN ASSESSMENT a ON c.course_code = a.course_code
JOIN STUDENT_PERFORMANCE sp ON sp.roll_no = s.roll_no AND sp.assessment_id = a.assessment_id;

CREATE OR REPLACE VIEW attendance_summary AS
SELECT s.roll_no, u.name, a.course_code,
       COUNT(*) AS total_classes,
       SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END) AS present_count,
       ROUND(SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END)*100.0/COUNT(*),2) AS attendance_pct
FROM ATTENDANCE a
JOIN STUDENT s ON a.roll_no = s.roll_no
JOIN USERS u   ON s.user_id = u.user_id
GROUP BY s.roll_no, u.name, a.course_code;

CREATE OR REPLACE VIEW faculty_course_view AS
SELECT u.name AS faculty_name, f.designation, c.course_code, c.course_name
FROM FACULTY_COURSE fc
JOIN FACULTY f ON fc.faculty_id  = f.faculty_id
JOIN USERS u   ON f.user_id      = u.user_id
JOIN COURSE c  ON fc.course_code = c.course_code;

-- TRIGGERS

/* =========================
        TRIGGERS
========================= */

DELIMITER $$

CREATE TRIGGER trg_check_marks
BEFORE INSERT ON STUDENT_PERFORMANCE
FOR EACH ROW
BEGIN
    DECLARE v_total INT;

    SELECT total_marks INTO v_total
    FROM ASSESSMENT
    WHERE assessment_id = NEW.assessment_id;

    IF NEW.marks_obtained < 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Marks cannot be negative';
    END IF;

    IF NEW.marks_obtained > v_total THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Marks cannot exceed total marks';
    END IF;
END $$
DELIMITER ;

DELIMITER $$
CREATE TRIGGER trg_auto_grade
BEFORE INSERT ON STUDENT_PERFORMANCE
FOR EACH ROW
BEGIN
    SET NEW.grade = CASE
        WHEN NEW.marks_obtained >= 90 THEN 'O'
        WHEN NEW.marks_obtained >= 80 THEN 'A+'
        WHEN NEW.marks_obtained >= 70 THEN 'A'
        WHEN NEW.marks_obtained >= 60 THEN 'B+'
        WHEN NEW.marks_obtained >= 50 THEN 'B'
        WHEN NEW.marks_obtained >= 40 THEN 'C'
        ELSE 'F'
    END;
END $$

DELIMITER ;



/* =========================
     STORED PROCEDURES
========================= */



DROP PROCEDURE IF EXISTS proc_safe_insert_student;

DELIMITER $$

CREATE PROCEDURE proc_safe_insert_student(
    IN p_roll INT,
    IN p_dept VARCHAR(50),
    IN p_branch VARCHAR(50),
    IN p_sem INT,
    IN p_uid INT
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SELECT 'Error: student not inserted' AS message;
    END;

    START TRANSACTION;

    INSERT INTO STUDENT (roll_no, department, branch, semester, user_id)
    VALUES (p_roll, p_dept, p_branch, p_sem, p_uid);

    COMMIT;

    SELECT 'Student inserted successfully' AS message;
END $$

DELIMITER ;
DROP PROCEDURE IF EXISTS proc_update_marks;

DELIMITER $$

CREATE PROCEDURE proc_update_marks(
    IN p_roll INT,
    IN p_asmt INT,
    IN p_marks INT
)
BEGIN
    DECLARE v_total INT DEFAULT NULL;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SELECT 'Update failed' AS message;
    END;

    START TRANSACTION;

    -- get total marks
    SELECT total_marks INTO v_total
    FROM ASSESSMENT
    WHERE assessment_id = p_asmt;

    -- check if assessment exists
    IF v_total IS NULL THEN
        ROLLBACK;
        SELECT 'Assessment not found' AS message;

    ELSEIF p_marks < 0 OR p_marks > v_total THEN
        ROLLBACK;
        SELECT 'Invalid marks entered' AS message;

    ELSE
        UPDATE STUDENT_PERFORMANCE
        SET marks_obtained = p_marks
        WHERE roll_no = p_roll AND assessment_id = p_asmt;

        COMMIT;

        SELECT 'Marks updated' AS message;
    END IF;

END $$

DELIMITER ;
DROP PROCEDURE IF EXISTS proc_add_user;

DELIMITER $$

CREATE PROCEDURE proc_add_user(
    IN p_id INT,
    IN p_name VARCHAR(100),
    IN p_uname VARCHAR(50),
    IN p_pass VARCHAR(100),
    IN p_role VARCHAR(20)
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SELECT 'User creation failed' AS message;
    END;

    START TRANSACTION;

    INSERT INTO USERS (user_id, name, username, password, role)
    VALUES (p_id, p_name, p_uname, p_pass, p_role);

    COMMIT;

    SELECT CONCAT(p_name, ' added as ', p_role) AS message;
END $$

DELIMITER ;


/* =========================
         FUNCTIONS
========================= */

DELIMITER $$

CREATE FUNCTION fn_attendance_percentage(
    p_roll INT,
    p_code VARCHAR(10)
)
RETURNS DECIMAL(5,2)
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE total INT DEFAULT 0;
    DECLARE present INT DEFAULT 0;

    SELECT COUNT(*) INTO total
    FROM ATTENDANCE
    WHERE roll_no = p_roll AND course_code = p_code;

    SELECT COUNT(*) INTO present
    FROM ATTENDANCE
    WHERE roll_no = p_roll AND course_code = p_code AND status = 'Present';

    IF total = 0 THEN RETURN 0.00; END IF;

    RETURN ROUND(present * 100.0 / total, 2);
END $$
DELIMITER ;

DELIMITER $$
CREATE FUNCTION fn_total_marks(p_roll INT)
RETURNS INT
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE v INT DEFAULT 0;

    SELECT COALESCE(SUM(marks_obtained),0)
    INTO v
    FROM STUDENT_PERFORMANCE
    WHERE roll_no = p_roll;

    RETURN v;
END $$

DELIMITER ;



/* =========================
          CURSORS
========================= */

DELIMITER $$

CREATE PROCEDURE proc_generate_report()
BEGIN
    DECLARE done INT DEFAULT 0;
    DECLARE v_roll INT;
    DECLARE v_name VARCHAR(100);
    DECLARE v_marks INT;

    DECLARE cur CURSOR FOR
        SELECT sp.roll_no, u.name, sp.marks_obtained
        FROM STUDENT_PERFORMANCE sp
        JOIN STUDENT s ON sp.roll_no = s.roll_no
        JOIN USERS u ON s.user_id = u.user_id
        ORDER BY sp.roll_no;

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

    OPEN cur;

    loop1: LOOP
        FETCH cur INTO v_roll, v_name, v_marks;
        IF done THEN LEAVE loop1; END IF;

        SELECT v_roll AS Roll_No, v_name AS Name, v_marks AS Marks;
    END LOOP;

    CLOSE cur;
END $$

DELIMITER ;
DELIMITER $$
CREATE PROCEDURE proc_low_attendance()
BEGIN
    DECLARE done INT DEFAULT 0;
    DECLARE v_roll INT;
    DECLARE v_name VARCHAR(100);
    DECLARE v_course VARCHAR(10);
    DECLARE v_pct DECIMAL(5,2);

    DECLARE cur CURSOR FOR
        SELECT s.roll_no, u.name, a.course_code,
               ROUND(SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END)*100.0/COUNT(*),2)
        FROM ATTENDANCE a
        JOIN STUDENT s ON a.roll_no = s.roll_no
        JOIN USERS u ON s.user_id = u.user_id
        GROUP BY s.roll_no, u.name, a.course_code
        HAVING (SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END)*100.0/COUNT(*)) < 75;

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

    OPEN cur;

    loop2: LOOP
        FETCH cur INTO v_roll, v_name, v_course, v_pct;
        IF done THEN LEAVE loop2; END IF;

        SELECT v_roll AS Roll_No, v_name AS Name, v_course AS Course, v_pct AS Att_Pct;
    END LOOP;

    CLOSE cur;
END $$

DELIMITER ;



/* =========================
           QUERIES
========================= */

-- Performance report
SELECT s.roll_no, u.name, c.course_name, a.assessment_type,
       sp.marks_obtained, sp.grade,
       ROUND(sp.marks_obtained*100.0/a.total_marks,2) AS percentage
FROM STUDENT s
JOIN USERS u ON s.user_id = u.user_id
JOIN STUDENT_PERFORMANCE sp ON sp.roll_no = s.roll_no
JOIN ASSESSMENT a ON sp.assessment_id = a.assessment_id
JOIN COURSE c ON a.course_code = c.course_code
ORDER BY s.roll_no;

-- Topper
SELECT u.name, s.roll_no, sp.marks_obtained
FROM STUDENT_PERFORMANCE sp
JOIN STUDENT s ON sp.roll_no = s.roll_no
JOIN USERS u ON s.user_id = u.user_id
WHERE sp.marks_obtained = (SELECT MAX(marks_obtained) FROM STUDENT_PERFORMANCE);

-- Below 40
SELECT u.name, s.roll_no, c.course_name, sp.marks_obtained
FROM STUDENT_PERFORMANCE sp
JOIN STUDENT s ON sp.roll_no = s.roll_no
JOIN USERS u ON s.user_id = u.user_id
JOIN ASSESSMENT a ON sp.assessment_id = a.assessment_id
JOIN COURSE c ON a.course_code = c.course_code
WHERE sp.marks_obtained < 40;


SELECT 
    s.roll_no,
    u.name,
    a.course_code,
    COUNT(*) AS total_classes,
    
    SUM(CASE 
        WHEN a.status = 'Present' THEN 1 
        ELSE 0 
    END) AS present_count,
    
    ROUND(
        SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) * 100.0 
        / COUNT(*), 2
    ) AS attendance_percentage,

    CASE 
        WHEN (SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) >= 75 
        THEN 'Good'
        ELSE 'Low Attendance'
    END AS status

FROM ATTENDANCE a
JOIN STUDENT s ON a.roll_no = s.roll_no
JOIN USERS u ON s.user_id = u.user_id

GROUP BY s.roll_no, u.name, a.course_code
ORDER BY attendance_percentage DESC;
/* =========================
           DROPS
========================= */
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS ATTENDANCE;
DROP TABLE IF EXISTS STUDENT_PERFORMANCE;
DROP TABLE IF EXISTS ASSESSMENT;
DROP TABLE IF EXISTS STUDY_MATERIAL;
DROP TABLE IF EXISTS PYQ;
DROP TABLE IF EXISTS FACULTY_COURSE;
DROP TABLE IF EXISTS ENROLLMENT;
DROP TABLE IF EXISTS COURSE;
DROP TABLE IF EXISTS ADMIN;
DROP TABLE IF EXISTS STUDENT;
DROP TABLE IF EXISTS FACULTY;
DROP TABLE IF EXISTS USERS;

DROP VIEW IF EXISTS student_performance_report;
DROP VIEW IF EXISTS attendance_summary;
DROP VIEW IF EXISTS faculty_course_view;

DROP TRIGGER IF EXISTS trg_before_insert_performance;

DROP PROCEDURE IF EXISTS proc_safe_insert_student;
DROP PROCEDURE IF EXISTS proc_update_marks;
DROP PROCEDURE IF EXISTS proc_add_user;
DROP PROCEDURE IF EXISTS proc_generate_report;
DROP PROCEDURE IF EXISTS proc_low_attendance;

DROP FUNCTION IF EXISTS fn_attendance_percentage;
DROP FUNCTION IF EXISTS fn_total_marks;

SET FOREIGN_KEY_CHECKS = 1;