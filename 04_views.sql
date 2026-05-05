use acadhub;
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