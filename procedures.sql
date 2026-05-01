/* =========================
     STORED PROCEDURES
========================= */

use acadhub;

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