-- Seed Data for Library Book Reservation System
-- Realistic books with various total copies and availability states

INSERT INTO books (id, title, author, total_copies, available_copies) VALUES
(1, 'Designing Data-Intensive Applications', 'Martin Kleppmann', 4, 3),
(2, 'Clean Code: A Handbook of Agile Software Craftsmanship', 'Robert C. Martin', 3, 2),
(3, 'The Pragmatic Programmer: Your Journey To Mastery', 'David Thomas, Andrew Hunt', 2, 1),
(4, 'Database Internals: A Deep Dive into Distributed Systems', 'Alex Petrov', 3, 3),
(5, 'Site Reliability Engineering', 'Betsy Beyer, Chris Jones, Niall Richard Murphy', 2, 0),
(6, 'Building Microservices: Designing Fine-Grained Systems', 'Sam Newman', 5, 5);

-- Seed reservations reflecting active and historical states
-- Note: Book 1 has 1 active reservation, total 4, available 3
INSERT INTO reservations (id, book_id, user_name, reservation_date, expires_at, status) VALUES
(1, 1, 'alice_smith', datetime('now', '-2 days'), datetime('now', '+5 days'), 'active');

-- Book 2 has 1 active reservation, total 3, available 2
INSERT INTO reservations (id, book_id, user_name, reservation_date, expires_at, status) VALUES
(2, 2, 'bob_johnson', datetime('now', '-1 day'), datetime('now', '+6 days'), 'active');

-- Book 3 has 1 active reservation, total 2, available 1
INSERT INTO reservations (id, book_id, user_name, reservation_date, expires_at, status) VALUES
(3, 3, 'charlie_brown', datetime('now', '-3 days'), datetime('now', '+4 days'), 'active');

-- Book 5 has 2 active reservations, total 2, available 0 (fully reserved)
INSERT INTO reservations (id, book_id, user_name, reservation_date, expires_at, status) VALUES
(4, 5, 'david_clark', datetime('now', '-4 days'), datetime('now', '+3 days'), 'active'),
(5, 5, 'eva_green', datetime('now', '-2 days'), datetime('now', '+5 days'), 'active');
