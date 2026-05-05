use acadhub;

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
