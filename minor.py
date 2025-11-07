import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import re

# ========== DATABASE SETUP ==========
def create_db():
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()

    # Students Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            uid INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            contact TEXT NOT NULL,
            email TEXT NOT NULL,
            age INTEGER NOT NULL
        )
    ''')

    # Courses Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            course_id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_name TEXT UNIQUE NOT NULL,
            duration TEXT,
            fee REAL
        )
    ''')

    # Enrollments Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS enrollments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            course_id INTEGER,
            FOREIGN KEY(student_id) REFERENCES students(uid),
            FOREIGN KEY(course_id) REFERENCES courses(course_id)
        )
    ''')

    # Default Courses (insert if table empty)
    cursor.execute('SELECT COUNT(*) FROM courses')
    if cursor.fetchone()[0] == 0:
        cursor.executemany('INSERT INTO courses (course_name, duration, fee) VALUES (?, ?, ?)', [
            ('Python Programming', '3 Months', 300),
            ('Data Science', '6 Months', 700),
            ('Web Development', '4 Months', 500),
            ('Machine Learning', '6 Months', 800)
        ])

    conn.commit()
    conn.close()

# ========== VALIDATION FUNCTIONS ==========
def validate_contact(contact):
    return re.match(r'^\d{10}$', contact) is not None

def validate_email(email):
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email) is not None

def validate_age(age):
    try:
        age_int = int(age)
        return 10 <= age_int <= 100
    except ValueError:
        return False

def validate_name(value):
    return len(value.strip()) > 0

def validate_uid(uid):
    try:
        int(uid)
        return True
    except ValueError:
        return False

# ========== CRUD FUNCTIONS ==========
def add_student():
    uid = uid_entry.get().strip()
    name = name_entry.get().strip()
    contact = contact_entry.get().strip()
    email = email_entry.get().strip()
    age = age_entry.get().strip()
    course_name = course_combo.get().strip()

    if not (validate_uid(uid) and validate_name(name) and validate_contact(contact)
            and validate_email(email) and validate_age(age) and course_name):
        messagebox.showerror("Error", "Invalid input. Please check all fields.")
        return

    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()

    try:
        cursor.execute('INSERT INTO students (uid, name, contact, email, age) VALUES (?, ?, ?, ?, ?)',
                       (int(uid), name, contact, email, int(age)))

        cursor.execute('SELECT course_id FROM courses WHERE course_name=?', (course_name,))
        course_id = cursor.fetchone()
        if course_id:
            cursor.execute('INSERT INTO enrollments (student_id, course_id) VALUES (?, ?)', (int(uid), course_id[0]))

        conn.commit()
        messagebox.showinfo("Success", "Student added successfully!")
        clear_fields()
        view_students()
        view_enrollments()
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "UID already exists.")
    conn.close()

def update_student():
    uid = uid_entry.get().strip()
    if not validate_uid(uid):
        messagebox.showerror("Error", "Enter a valid UID to update.")
        return

    name = name_entry.get().strip()
    contact = contact_entry.get().strip()
    email = email_entry.get().strip()
    age = age_entry.get().strip()
    course_name = course_combo.get().strip()

    if not (validate_name(name) and validate_contact(contact) and validate_email(email) and validate_age(age)):
        messagebox.showerror("Error", "Invalid input!")
        return

    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE students SET name=?, contact=?, email=?, age=? WHERE uid=?',
                   (name, contact, email, int(age), int(uid)))

    # Update enrollment
    cursor.execute('SELECT course_id FROM courses WHERE course_name=?', (course_name,))
    course_id = cursor.fetchone()
    if course_id:
        cursor.execute('UPDATE enrollments SET course_id=? WHERE student_id=?', (course_id[0], int(uid)))

    if cursor.rowcount == 0:
        messagebox.showerror("Error", "Student not found.")
    else:
        messagebox.showinfo("Success", "Student updated successfully!")

    conn.commit()
    conn.close()
    clear_fields()
    view_students()
    view_enrollments()

def delete_student():
    uid = uid_entry.get().strip()
    if not validate_uid(uid):
        messagebox.showerror("Error", "Enter a valid UID to delete.")
        return

    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM enrollments WHERE student_id=?', (int(uid),))
    cursor.execute('DELETE FROM students WHERE uid=?', (int(uid),))

    if cursor.rowcount == 0:
        messagebox.showerror("Error", "Student not found.")
    else:
        messagebox.showinfo("Success", "Student deleted successfully!")

    conn.commit()
    conn.close()
    clear_fields()
    view_students()
    view_enrollments()

def view_students():
    for row in student_tree.get_children():
        student_tree.delete(row)

    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM students')
    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        student_tree.insert('', tk.END, values=row)

def view_enrollments():
    for row in enroll_tree.get_children():
        enroll_tree.delete(row)

    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT s.uid, s.name, c.course_name, c.duration, c.fee
        FROM students s
        JOIN enrollments e ON s.uid = e.student_id
        JOIN courses c ON e.course_id = c.course_id
    ''')
    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        enroll_tree.insert('', tk.END, values=row)

def clear_fields():
    uid_entry.delete(0, tk.END)
    name_entry.delete(0, tk.END)
    contact_entry.delete(0, tk.END)
    email_entry.delete(0, tk.END)
    age_entry.delete(0, tk.END)
    course_combo.set('')

# ========== GUI SETUP ==========
create_db()
root = tk.Tk()
root.title("Advanced Student Management System")
root.geometry("1000x650")
root.configure(bg="#f8f8f8")

style = ttk.Style()
style.theme_use("clam")

# Notebook for Tabs
notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# --- STUDENTS TAB ---
student_tab = ttk.Frame(notebook)
notebook.add(student_tab, text="Students")

form_frame = ttk.LabelFrame(student_tab, text="Student Information", padding=10)
form_frame.pack(fill=tk.X, padx=10, pady=10)

# Fields
ttk.Label(form_frame, text="UID:").grid(row=0, column=0, sticky=tk.W, pady=5)
uid_entry = ttk.Entry(form_frame)
uid_entry.grid(row=0, column=1, padx=5)

ttk.Label(form_frame, text="Name:").grid(row=1, column=0, sticky=tk.W, pady=5)
name_entry = ttk.Entry(form_frame)
name_entry.grid(row=1, column=1, padx=5)

ttk.Label(form_frame, text="Contact:").grid(row=2, column=0, sticky=tk.W, pady=5)
contact_entry = ttk.Entry(form_frame)
contact_entry.grid(row=2, column=1, padx=5)

ttk.Label(form_frame, text="Email:").grid(row=3, column=0, sticky=tk.W, pady=5)
email_entry = ttk.Entry(form_frame)
email_entry.grid(row=3, column=1, padx=5)

ttk.Label(form_frame, text="Age:").grid(row=4, column=0, sticky=tk.W, pady=5)
age_entry = ttk.Entry(form_frame)
age_entry.grid(row=4, column=1, padx=5)

ttk.Label(form_frame, text="Course:").grid(row=5, column=0, sticky=tk.W, pady=5)
course_combo = ttk.Combobox(form_frame, state="readonly")
conn = sqlite3.connect('students.db')
cursor = conn.cursor()
cursor.execute('SELECT course_name FROM courses')
course_combo['values'] = [row[0] for row in cursor.fetchall()]
conn.close()
course_combo.grid(row=5, column=1, padx=5)

# Buttons
button_frame = ttk.Frame(form_frame)
button_frame.grid(row=6, column=0, columnspan=2, pady=10)
ttk.Button(button_frame, text="Add", command=add_student).grid(row=0, column=0, padx=5)
ttk.Button(button_frame, text="Update", command=update_student).grid(row=0, column=1, padx=5)
ttk.Button(button_frame, text="Delete", command=delete_student).grid(row=0, column=2, padx=5)
ttk.Button(button_frame, text="Clear", command=clear_fields).grid(row=0, column=3, padx=5)

# Student Table
student_tree = ttk.Treeview(student_tab, columns=("UID", "Name", "Contact", "Email", "Age"), show="headings")
for col in ("UID", "Name", "Contact", "Email", "Age"):
    student_tree.heading(col, text=col)
    student_tree.column(col, width=180)
student_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# --- ENROLLMENTS TAB ---
enroll_tab = ttk.Frame(notebook)
notebook.add(enroll_tab, text="Enrollments")

enroll_tree = ttk.Treeview(enroll_tab, columns=("UID", "Name", "Course", "Duration", "Fee"), show="headings")
for col in ("UID", "Name", "Course", "Duration", "Fee"):
    enroll_tree.heading(col, text=col)
    enroll_tree.column(col, width=180)
enroll_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Initial Load
view_students()
view_enrollments()

root.mainloop()
