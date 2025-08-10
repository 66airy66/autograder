INSERT INTO questions (id, prompt, max_score, due_date)
VALUES (1, 'Q1) Submit SQL to return name and email of all students from students table', 10, '2025-06-30');

INSERT INTO expected_answers (question_id, expected_sql, score) VALUES
(1, 'SELECT name FROM students', 5),
(1, 'SELECT email FROM students', 5),
(1, 'SELECT name,email FROM students', 10),
(1, 'SELECT name, email FROM students', 10);