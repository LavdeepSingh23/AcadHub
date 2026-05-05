use acadhub;

USE acadhub;

/* ================================================================
   SECTION 11 – DROP EVERYTHING (cleanup / reset)
   ================================================================ */

SET FOREIGN_KEY_CHECKS = 0;

-- 🔹 Drop triggers (ALL used ones)
DROP TRIGGER IF EXISTS trg_sp_before_insert;
DROP TRIGGER IF EXISTS trg_sp_before_update;
DROP TRIGGER IF EXISTS trg_sp_after_insert;
DROP TRIGGER IF EXISTS trg_check_marks;
DROP TRIGGER IF EXISTS trg_auto_grade;

-- 🔹 Drop views
DROP VIEW IF EXISTS student_performance_report;
DROP VIEW IF EXISTS attendance_summary;
DROP VIEW IF EXISTS faculty_course_view;

-- 🔹 Drop procedures
DROP PROCEDURE IF EXISTS proc_safe_insert_student;
DROP PROCEDURE IF EXISTS proc_update_marks;
DROP PROCEDURE IF EXISTS proc_add_user;
DROP PROCEDURE IF EXISTS proc_enroll_student;
DROP PROCEDURE IF EXISTS proc_record_attendance;
DROP PROCEDURE IF EXISTS proc_mark_performance_safe;
DROP PROCEDURE IF EXISTS proc_generate_report;
DROP PROCEDURE IF EXISTS proc_low_attendance;

-- 🔹 Drop functions
DROP FUNCTION IF EXISTS fn_attendance_percentage;
DROP FUNCTION IF EXISTS fn_total_marks;
DROP FUNCTION IF EXISTS fn_student_grade_letter;
DROP FUNCTION IF EXISTS fn_course_avg_marks;
DROP FUNCTION IF EXISTS fn_is_eligible_for_exam;

-- 🔹 Drop tables (including log table)
DROP TABLE IF EXISTS performance_log;
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

SET FOREIGN_KEY_CHECKS = 1;