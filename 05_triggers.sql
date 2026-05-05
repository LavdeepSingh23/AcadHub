use acadhub;
DROP TRIGGER IF EXISTS trg_check_marks;
DROP TRIGGER IF EXISTS trg_auto_grade;
DROP TRIGGER IF EXISTS trg_student_performance_before_insert;

SHOW TRIGGERS LIKE 'STUDENT_PERFORMANCE';

DELIMITER $$

CREATE TRIGGER trg_student_performance_before_insert
BEFORE INSERT ON STUDENT_PERFORMANCE
FOR EACH ROW
BEGIN
    DECLARE v_total INT DEFAULT 0;

    SELECT total_marks INTO v_total
    FROM ASSESSMENT
    WHERE assessment_id = NEW.assessment_id
    LIMIT 1;

    IF v_total IS NULL THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid assessment_id';
    END IF;

    IF NEW.marks_obtained < 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Marks cannot be negative';
    END IF;

    IF NEW.marks_obtained > v_total THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Marks cannot exceed total marks';
    END IF;

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