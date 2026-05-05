import mysql.connector
import streamlit as st
import pandas as pd


def get_connection():
    cfg = st.secrets["mysql"]
    return mysql.connector.connect(
        host=cfg["host"],
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"],
        port=cfg.get("port", 3306),
        autocommit=False,
    )


def run_query(sql: str, params=None) -> pd.DataFrame:
    conn = get_connection()
    try:
        df = pd.read_sql(sql, conn, params=params)
        return df
    finally:
        conn.close()


def run_procedure(proc_name: str, args: tuple):
    conn = get_connection()
    cur = conn.cursor()
    messages = []
    try:
        cur.callproc(proc_name, args)
        conn.commit()
        for result in cur.stored_results():
            rows = result.fetchall()
            if rows:
                messages.append(rows[0][0])
    except mysql.connector.Error as e:
        conn.rollback()
        messages.append(f"Error: {e.msg}")
    finally:
        cur.close()
        conn.close()
    return messages


def run_write(sql: str, params=None):
    conn = get_connection()
    cur = conn.cursor()
    msg = "Success"
    try:
        cur.execute(sql, params or ())
        conn.commit()
    except mysql.connector.Error as e:
        conn.rollback()
        msg = f"Error: {e.msg}"
    finally:
        cur.close()
        conn.close()
    return msg


def authenticate(username: str, password: str):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(
            "SELECT user_id, name, role FROM USERS WHERE username=%s AND password=%s",
            (username, password),
        )
        return cur.fetchone()
    finally:
        cur.close()
        conn.close()


def get_student_by_user(user_id: int):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT * FROM STUDENT WHERE user_id=%s", (user_id,))
        return cur.fetchone()
    finally:
        cur.close()
        conn.close()


def get_faculty_by_user(user_id: int):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT * FROM FACULTY WHERE user_id=%s", (user_id,))
        return cur.fetchone()
    finally:
        cur.close()
        conn.close()
