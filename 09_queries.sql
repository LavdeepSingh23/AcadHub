use acadhub;
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