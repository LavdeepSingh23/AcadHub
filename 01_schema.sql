CREATE DATABASE IF NOT EXISTS acadhub;
USE acadhub;

CREATE TABLE USERS (
    user_id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL
);

CREATE TABLE STUDENT (
    roll_no INT PRIMARY KEY,
    department VARCHAR(50) NOT NULL,
    branch VARCHAR(50) NOT NULL,
    semester INT NOT NULL,
    user_id INT UNIQUE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES USERS(user_id) ON DELETE CASCADE
);

CREATE TABLE FACULTY (
    faculty_id INT PRIMARY KEY,
    designation VARCHAR(50),
    department VARCHAR(50),
    user_id INT UNIQUE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES USERS(user_id) ON DELETE CASCADE
);

CREATE TABLE ADMIN (
    admin_id INT PRIMARY KEY,
    user_id INT UNIQUE NOT NULL,
    access_level VARCHAR(30) DEFAULT 'Full',
    FOREIGN KEY (user_id) REFERENCES USERS(user_id) ON DELETE CASCADE
);

CREATE TABLE COURSE (
    course_code VARCHAR(10) PRIMARY KEY,
    course_name VARCHAR(100) NOT NULL,
    credits INT DEFAULT 4,
    semester INT NOT NULL
);

CREATE TABLE ENROLLMENT (
    enrollment_id INT PRIMARY KEY,
    roll_no INT,
    course_code VARCHAR(10),
    UNIQUE (roll_no, course_code),
    FOREIGN KEY (roll_no) REFERENCES STUDENT(roll_no),
    FOREIGN KEY (course_code) REFERENCES COURSE(course_code)
);

CREATE TABLE FACULTY_COURSE (
    id INT PRIMARY KEY,
    faculty_id INT,
    course_code VARCHAR(10),
    FOREIGN KEY (faculty_id) REFERENCES FACULTY(faculty_id),
    FOREIGN KEY (course_code) REFERENCES COURSE(course_code)
);

CREATE TABLE PYQ (
    pyq_id INT PRIMARY KEY,
    course_code VARCHAR(10),
    question TEXT,
    year INT,
    exam_type VARCHAR(50),
    FOREIGN KEY (course_code) REFERENCES COURSE(course_code)
);

CREATE TABLE STUDY_MATERIAL (
    material_id INT PRIMARY KEY,
    course_code VARCHAR(10),
    faculty_id INT,
    title VARCHAR(100),
    material_type ENUM('Notes','Slides','Tutorials','Reference'),
    content TEXT,
    upload_date DATE,
    FOREIGN KEY (course_code) REFERENCES COURSE(course_code),
    FOREIGN KEY (faculty_id) REFERENCES FACULTY(faculty_id)
);

CREATE TABLE ASSESSMENT (
    assessment_id INT PRIMARY KEY,
    course_code VARCHAR(10),
    assessment_type VARCHAR(50),
    total_marks INT,
    FOREIGN KEY (course_code) REFERENCES COURSE(course_code)
);

CREATE TABLE STUDENT_PERFORMANCE (
    performance_id INT PRIMARY KEY,
    roll_no INT,
    assessment_id INT,
    marks_obtained INT,
    grade CHAR(2),
    UNIQUE (roll_no, assessment_id),
    FOREIGN KEY (roll_no) REFERENCES STUDENT(roll_no),
    FOREIGN KEY (assessment_id) REFERENCES ASSESSMENT(assessment_id)
);

CREATE TABLE ATTENDANCE (
    attendance_id INT PRIMARY KEY,
    roll_no INT,
    course_code VARCHAR(10),
    attendance_date DATE,
    status ENUM('Present','Absent'),
    remarks VARCHAR(100),
    FOREIGN KEY (roll_no) REFERENCES STUDENT(roll_no),
    FOREIGN KEY (course_code) REFERENCES COURSE(course_code)
);