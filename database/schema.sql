-- ============================================================
-- INSURANCE CONTRACT EDITOR
-- Schéma de la base de données
-- PostgreSQL
-- ============================================================

-- ============================================================
-- 1. SOUSCRIPTEURS
-- ============================================================

CREATE TABLE souscripteurs (
    souscripteur_id SERIAL PRIMARY KEY,
    code_souscripteur VARCHAR(50) UNIQUE NOT NULL,
    raison_sociale VARCHAR(255) NOT NULL,
    adresse VARCHAR(500),
    telephone VARCHAR(50),
    email VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
-- 2. GESTIONNAIRES
-- ============================================================

CREATE TABLE gestionnaires (
    gestionnaire_id SERIAL PRIMARY KEY,
    matricule VARCHAR(50) UNIQUE NOT NULL,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    attribution VARCHAR(100),
    actif BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
-- 3. CONTRATS
-- ============================================================

CREATE TABLE contrats (
    contrat_id SERIAL PRIMARY KEY,

    souscripteur_id INTEGER NOT NULL,

    compagnie VARCHAR(255) NOT NULL,
    code_compagnie VARCHAR(50),

    intermediaire VARCHAR(255),
    code_intermediaire VARCHAR(50),

    numero_compte VARCHAR(100),

    numero_police VARCHAR(100) NOT NULL,

    nature_risque VARCHAR(255),
    police VARCHAR(255),

    numero_intermediaire_police VARCHAR(100),

    duree INTEGER,

    echeance_annuelle DATE,

    fractionnement_prime VARCHAR(50),

    date_effet DATE NOT NULL,

    date_fin DATE NOT NULL,

    prime_nette_par_personne NUMERIC(18,2) NOT NULL DEFAULT 0,

    accessoire_taux NUMERIC(10,4) DEFAULT 0,

    taxe_taux NUMERIC(10,4) DEFAULT 0,

    actif BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_contrat_souscripteur
        FOREIGN KEY (souscripteur_id)
        REFERENCES souscripteurs(souscripteur_id),

    CONSTRAINT uk_numero_police
        UNIQUE (numero_police)
);


-- ============================================================
-- 4. ASSURES
-- ============================================================

CREATE TABLE assures (
    assure_id SERIAL PRIMARY KEY,

    contrat_id INTEGER NOT NULL,

    numero_assure VARCHAR(100) UNIQUE NOT NULL,

    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100),

    date_naissance DATE,

    sexe VARCHAR(20),

    lien_parente VARCHAR(100),

    date_entree DATE NOT NULL,

    date_sortie DATE,

    actif BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_assure_contrat
        FOREIGN KEY (contrat_id)
        REFERENCES contrats(contrat_id)
);


-- ============================================================
-- 5. MOUVEMENTS D'EFFECTIF
-- ============================================================

CREATE TABLE mouvements_effectif (
    mouvement_id SERIAL PRIMARY KEY,

    contrat_id INTEGER NOT NULL,

    assure_id INTEGER NOT NULL,

    type_mouvement VARCHAR(30) NOT NULL,

    date_mouvement DATE NOT NULL,

    date_debut_periode DATE,

    date_fin_periode DATE,

    commentaire TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_mouvement_contrat
        FOREIGN KEY (contrat_id)
        REFERENCES contrats(contrat_id),

    CONSTRAINT fk_mouvement_assure
        FOREIGN KEY (assure_id)
        REFERENCES assures(assure_id),

    CONSTRAINT chk_type_mouvement
        CHECK (
            type_mouvement IN (
                'INCORPORATION',
                'RETRAIT'
            )
        )
);


-- ============================================================
-- 6. EDITIONS DES CONTRATS
-- ============================================================

CREATE TABLE editions_contrats (
    edition_id SERIAL PRIMARY KEY,

    contrat_id INTEGER NOT NULL,

    gestionnaire_id INTEGER NOT NULL,

    type_contrat VARCHAR(50) NOT NULL,

    numero_avenant VARCHAR(100) NOT NULL,

    numero_quittance VARCHAR(100),

    date_edition TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    periode_debut DATE NOT NULL,

    periode_fin DATE NOT NULL,

    prime_nette NUMERIC(18,2) NOT NULL DEFAULT 0,

    accessoire NUMERIC(18,2) NOT NULL DEFAULT 0,

    taxe NUMERIC(18,2) NOT NULL DEFAULT 0,

    prime_totale NUMERIC(18,2) NOT NULL DEFAULT 0,

    prime_terme NUMERIC(18,2) NOT NULL DEFAULT 0,

    mode_calcul VARCHAR(30) NOT NULL,

    format_document VARCHAR(10) NOT NULL,

    statut VARCHAR(30) DEFAULT 'GENERE',

    CONSTRAINT fk_edition_contrat
        FOREIGN KEY (contrat_id)
        REFERENCES contrats(contrat_id),

    CONSTRAINT fk_edition_gestionnaire
        FOREIGN KEY (gestionnaire_id)
        REFERENCES gestionnaires(gestionnaire_id),

    CONSTRAINT chk_type_contrat
        CHECK (
            type_contrat IN (
                'AFFAIRE_NOUVELLE',
                'AVENANT_RENOUVELLEMENT',
                'AVENANT_MOUVEMENT_EFFECTIF'
            )
        ),

    CONSTRAINT chk_mode_calcul
        CHECK (
            mode_calcul IN (
                'ANNUEL',
                'PRORATA'
            )
        ),

    CONSTRAINT chk_format_document
        CHECK (
            format_document IN (
                'WORD',
                'PDF'
            )
        ),

    CONSTRAINT chk_statut_edition
        CHECK (
            statut IN (
                'GENERE',
                'ANNULE',
                'REEDITE'
            )
        )
);


-- ============================================================
-- 7. DOCUMENTS GENERES
-- ============================================================

CREATE TABLE documents_generes (
    document_id SERIAL PRIMARY KEY,

    edition_id INTEGER NOT NULL,

    nom_fichier VARCHAR(255) NOT NULL,

    chemin_fichier VARCHAR(500),

    format_document VARCHAR(10) NOT NULL,

    date_generation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_document_edition
        FOREIGN KEY (edition_id)
        REFERENCES editions_contrats(edition_id),

    CONSTRAINT chk_document_format
        CHECK (
            format_document IN (
                'WORD',
                'PDF'
            )
        )
);


-- ============================================================
-- INDEX
-- ============================================================

CREATE INDEX idx_souscripteurs_nom
    ON souscripteurs(raison_sociale);

CREATE INDEX idx_contrats_souscripteur
    ON contrats(souscripteur_id);

CREATE INDEX idx_contrats_police
    ON contrats(numero_police);

CREATE INDEX idx_assures_contrat
    ON assures(contrat_id);

CREATE INDEX idx_assures_nom
    ON assures(nom, prenom);

CREATE INDEX idx_mouvements_contrat
    ON mouvements_effectif(contrat_id);

CREATE INDEX idx_editions_contrat
    ON editions_contrats(contrat_id);

CREATE INDEX idx_editions_gestionnaire
    ON editions_contrats(gestionnaire_id);

CREATE INDEX idx_editions_date
    ON editions_contrats(date_edition);