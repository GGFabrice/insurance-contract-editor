-- ============================================================
-- MIGRATION 001
-- COLLEGES + AVENANTS + LIGNES D'AVENANT
-- ============================================================

BEGIN;


-- ============================================================
-- 1. COLLEGES
-- ============================================================

CREATE TABLE IF NOT EXISTS colleges (
    college_id SERIAL PRIMARY KEY,

    contrat_id INTEGER NOT NULL,

    numero_college INTEGER NOT NULL,

    libelle VARCHAR(255) NOT NULL,

    prime_nette_par_personne NUMERIC(18,2) NOT NULL DEFAULT 0,

    actif BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_college_contrat
        FOREIGN KEY (contrat_id)
        REFERENCES contrats(contrat_id),

    CONSTRAINT uk_college_contrat_numero
        UNIQUE (contrat_id, numero_college)
);


-- ============================================================
-- 2. AJOUT DU COLLEGE AUX ASSURES
-- ============================================================

ALTER TABLE assures
ADD COLUMN IF NOT EXISTS college_id INTEGER;


-- ============================================================
-- 3. COLLEGES PAR DEFAUT POUR LES CONTRATS EXISTANTS
-- ============================================================

INSERT INTO colleges (
    contrat_id,
    numero_college,
    libelle,
    prime_nette_par_personne
)
SELECT
    c.contrat_id,
    1,
    'College 1',
    c.prime_nette_par_personne
FROM contrats c
WHERE NOT EXISTS (
    SELECT 1
    FROM colleges col
    WHERE col.contrat_id = c.contrat_id
);


-- ============================================================
-- 4. RATTACHER LES ASSURES EXISTANTS AU COLLEGE 1
-- ============================================================

UPDATE assures a
SET college_id = c.college_id
FROM colleges c
WHERE c.contrat_id = a.contrat_id
  AND c.numero_college = 1
  AND a.college_id IS NULL;


-- ============================================================
-- 5. CONTRAINTE SUR ASSURES
-- ============================================================

ALTER TABLE assures
ADD CONSTRAINT fk_assure_college
FOREIGN KEY (college_id)
REFERENCES colleges(college_id);


-- ============================================================
-- 6. LIEN MOUVEMENT → AVENANT
-- ============================================================

ALTER TABLE mouvements_effectif
ADD COLUMN IF NOT EXISTS avenant_id INTEGER;


-- ============================================================
-- 7. TABLE AVENANTS
-- ============================================================

CREATE TABLE IF NOT EXISTS avenants (
    avenant_id SERIAL PRIMARY KEY,

    contrat_id INTEGER NOT NULL,

    numero_avenant VARCHAR(100) NOT NULL,

    type_avenant VARCHAR(50) NOT NULL,

    periode_debut DATE NOT NULL,

    periode_fin DATE NOT NULL,

    date_effet DATE NOT NULL,

    date_edition DATE DEFAULT CURRENT_DATE,

    prime_nette NUMERIC(18,2) NOT NULL DEFAULT 0,

    accessoire NUMERIC(18,2) NOT NULL DEFAULT 0,

    taxe NUMERIC(18,2) NOT NULL DEFAULT 0,

    prime_totale NUMERIC(18,2) NOT NULL DEFAULT 0,

    statut VARCHAR(30) NOT NULL DEFAULT 'BROUILLON',

    commentaire TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_avenant_contrat
        FOREIGN KEY (contrat_id)
        REFERENCES contrats(contrat_id),

    CONSTRAINT uk_avenant_numero
        UNIQUE (contrat_id, numero_avenant),

    CONSTRAINT chk_type_avenant
        CHECK (
            type_avenant IN (
                'AFFAIRE_NOUVELLE',
                'AVENANT_RENOUVELLEMENT',
                'AVENANT_INCORPORATION',
                'AVENANT_RETRAIT'
            )
        ),

    CONSTRAINT chk_statut_avenant
        CHECK (
            statut IN (
                'BROUILLON',
                'VALIDE',
                'GENERE',
                'ANNULE'
            )
        )
);


-- ============================================================
-- 8. AJOUT DE LA FK MOUVEMENT → AVENANT
-- ============================================================

ALTER TABLE mouvements_effectif
ADD CONSTRAINT fk_mouvement_avenant
FOREIGN KEY (avenant_id)
REFERENCES avenants(avenant_id);


-- ============================================================
-- 9. LIGNES D'AVENANT
-- ============================================================

CREATE TABLE IF NOT EXISTS lignes_avenant (
    ligne_avenant_id SERIAL PRIMARY KEY,

    avenant_id INTEGER NOT NULL,

    college_id INTEGER NOT NULL,

    nombre_personnes INTEGER NOT NULL DEFAULT 0,

    prime_nette_par_personne NUMERIC(18,2) NOT NULL DEFAULT 0,

    prime_nette NUMERIC(18,2) NOT NULL DEFAULT 0,

    accessoire NUMERIC(18,2) NOT NULL DEFAULT 0,

    taxe NUMERIC(18,2) NOT NULL DEFAULT 0,

    prime_totale NUMERIC(18,2) NOT NULL DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_ligne_avenant
        FOREIGN KEY (avenant_id)
        REFERENCES avenants(avenant_id),

    CONSTRAINT fk_ligne_college
        FOREIGN KEY (college_id)
        REFERENCES colleges(college_id)
);


-- ============================================================
-- 10. INDEX
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_colleges_contrat
    ON colleges(contrat_id);

CREATE INDEX IF NOT EXISTS idx_assures_college
    ON assures(college_id);

CREATE INDEX IF NOT EXISTS idx_avenants_contrat
    ON avenants(contrat_id);

CREATE INDEX IF NOT EXISTS idx_avenants_date
    ON avenants(date_edition);

CREATE INDEX IF NOT EXISTS idx_lignes_avenant
    ON lignes_avenant(avenant_id);

CREATE INDEX IF NOT EXISTS idx_lignes_college
    ON lignes_avenant(college_id);

CREATE INDEX IF NOT EXISTS idx_mouvements_avenant
    ON mouvements_effectif(avenant_id);


COMMIT;