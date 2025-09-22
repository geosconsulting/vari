-- PostgreSQL Tables with Foreign Key

-- Create the ruoli (roles) table
CREATE TABLE ruoli (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descrizione TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the persone (people) table if it doesn't exist
-- If the table already exists, you would use ALTER TABLE instead
CREATE TABLE IF NOT EXISTS persone (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    cognome VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE,
    ruolo_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add the foreign key constraint to persone table referencing ruoli
ALTER TABLE persone
ADD CONSTRAINT fk_ruolo
FOREIGN KEY (ruolo_id) REFERENCES ruoli(id)
ON DELETE SET NULL;  -- When a role is deleted, set ruolo_id to NULL in persone table

-- Add an index on the foreign key for better performance
CREATE INDEX idx_persone_ruolo ON persone(ruolo_id);

Inserimento dati di esempio nelle tabelle

-- Inserimento dati nella tabella ruoli
INSERT INTO ruoli (nome, descrizione) VALUES
('Amministratore', 'Accesso completo a tutte le funzionalità del sistema'),
('Direttore', 'Gestione del personale e dei progetti aziendali'),
('Responsabile HR', 'Gestione delle risorse umane e dei processi di selezione'),
('Sviluppatore', 'Programmazione e sviluppo software'),
('Analista', 'Analisi dei dati e reporting'),
('Designer', 'Progettazione grafica e UI/UX'),
('Contabile', 'Gestione della contabilità e delle finanze'),
('Commerciale', 'Vendite e relazioni con i clienti');

-- Inserimento dati nella tabella persone
INSERT INTO persone (nome, cognome, email, ruolo_id) VALUES
('Marco', 'Rossi', 'marco.rossi@esempio.it', 1),
('Giulia', 'Bianchi', 'giulia.bianchi@esempio.it', 2),
('Alessandro', 'Verdi', 'alessandro.verdi@esempio.it', 3),
('Francesca', 'Neri', 'francesca.neri@esempio.it', 4),
('Lorenzo', 'Ferrari', 'lorenzo.ferrari@esempio.it', 4),
('Valentina', 'Esposito', 'valentina.esposito@esempio.it', 5),
('Davide', 'Romano', 'davide.romano@esempio.it', 6),
('Chiara', 'Colombo', 'chiara.colombo@esempio.it', 7),
('Matteo', 'Ricci', 'matteo.ricci@esempio.it', 8),
('Sofia', 'Marino', 'sofia.marino@esempio.it', 4),
('Andrea', 'Greco', 'andrea.greco@esempio.it', 5),
('Elena', 'Bruno', 'elena.bruno@esempio.it', 6),
('Luca', 'Gallo', 'luca.gallo@esempio.it', 8),
('Laura', 'Costa', 'laura.costa@esempio.it', 3),
('Roberto', 'Fontana', 'roberto.fontana@esempio.it', 4);

-- Query di verifica per visualizzare le persone con i loro ruoli
SELECT p.id, p.nome, p.cognome, p.email, r.nome as ruolo, r.descrizione
FROM persone p
JOIN ruoli r ON p.ruolo_id = r.id
ORDER BY p.id;


-- Query base per verificare le relazioni tra persone e ruoli
SELECT 
    p.id AS persona_id,
    p.nome,
    p.cognome,
    p.ruolo_id,
    r.id AS id_ruolo,
    r.nome AS nome_ruolo
FROM 
    persone p
JOIN 
    ruoli r ON p.ruolo_id = r.id
ORDER BY 
    p.id;

-- Conteggio persone per ruolo
SELECT 
    r.id AS id_ruolo,
    r.nome AS nome_ruolo,
    COUNT(p.id) AS numero_persone
FROM 
    ruoli r
LEFT JOIN 
    persone p ON r.id = p.ruolo_id
GROUP BY 
    r.id, r.nome
ORDER BY 
    numero_persone DESC;

-- Verifica della struttura della foreign key
SELECT
    tc.table_schema, 
    tc.constraint_name, 
    tc.table_name, 
    kcu.column_name, 
    ccu.table_schema AS foreign_table_schema,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name 
FROM 
    information_schema.table_constraints AS tc 
JOIN 
    information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN 
    information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
    AND ccu.table_schema = tc.table_schema
WHERE 
    tc.constraint_type = 'FOREIGN KEY' 
    AND tc.table_name = 'persone';


