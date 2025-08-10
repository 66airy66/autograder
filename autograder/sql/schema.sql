CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    prompt TEXT,
    max_score INT,
    due_date DATE
);

CREATE TABLE expected_answers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question_id INT,
    expected_sql TEXT,
    score INT,
    FOREIGN KEY (question_id) REFERENCES questions(id)
);

CREATE TABLE submissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    question_id INT,
    submitted_sql TEXT,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    score INT,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (question_id) REFERENCES questions(id)
);