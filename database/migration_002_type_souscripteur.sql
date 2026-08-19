-- ============================================================
-- MIGRATION 002
-- TYPE DE SOUSCRIPTEUR
-- ============================================================

BEGIN;

ALTER TABLE souscripteurs
ADD COLUMN IF NOT EXISTS type_souscripteur VARCHAR(30);

ALTER TABLE souscripteurs
ADD CONSTRAINT chk_type_souscripteur
CHECK (
    type_souscripteur IN (
        'ENTREPRISE',
        'PARTICULIER'
    )
);

-- Les données de test actuelles sont des souscripteurs
-- d'entreprise. Cette valeur pourra être modifiée ensuite
-- souscripteur par souscripteur.
UPDATE souscripteurs
SET type_souscripteur = 'ENTREPRISE'
WHERE type_souscripteur IS NULL;

CREATE INDEX IF NOT EXISTS idx_souscripteurs_type
    ON souscripteurs(type_souscripteur);

COMMIT;