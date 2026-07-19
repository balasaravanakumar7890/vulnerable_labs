CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL
);

CREATE TABLE memories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id INTEGER REFERENCES users(id),
    content_url VARCHAR(255) NOT NULL,
    privacy INTEGER DEFAULT 0
);

-- Insert demo users
INSERT INTO users (username, password_hash) VALUES 
('victim_user', '$2b$12$e/Gk48iCg8bS1Vq1Z.jV6uy0G./u.nF8B4F9O9Ew6M4T2Fh5GZ7X6'), 
('attacker_user', '$2b$12$e/Gk48iCg8bS1Vq1Z.jV6uy0G./u.nF8B4F9O9Ew6M4T2Fh5GZ7X6');

-- Insert a private memory for the victim
INSERT INTO memories (user_id, content_url, privacy) VALUES
(1, 'https://placehold.co/400x400/FF0000/FFFFFF/png?text=Victims+Private+Memory', 0);
