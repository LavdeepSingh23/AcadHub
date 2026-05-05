use acadhub;
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