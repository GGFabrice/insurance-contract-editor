-- ============================================================
-- INSURANCE CONTRACT EDITOR
-- DONNEES DE TEST
-- PostgreSQL
-- ============================================================

-- ============================================================
-- 1. SOUSCRIPTEURS
-- ============================================================

INSERT INTO souscripteurs
(code_souscripteur, raison_sociale, adresse, telephone, email)
VALUES
('CLI001', 'NSIA BANQUE COTE D''IVOIRE',
 'Abidjan, Plateau', '+225 27 20 30 40 50',
 'contact@nsiabanque.ci'),

('CLI002', 'ORANGE COTE D''IVOIRE',
 'Abidjan, Cocody', '+225 27 20 30 40 60',
 'contact@orange.ci'),

('CLI003', 'SOCIETE GENERALE COTE D''IVOIRE',
 'Abidjan, Plateau', '+225 27 20 30 40 70',
 'contact@sgci.ci'),

('CLI004', 'MOOV AFRICA COTE D''IVOIRE',
 'Abidjan, Marcory', '+225 27 20 30 40 80',
 'contact@moov-africa.ci'),

('CLI005', 'ENTREPRISE GENERALE DE SERVICES',
 'Abidjan, Deux Plateaux', '+225 27 20 30 40 90',
 'contact@egs.ci');


-- ============================================================
-- 2. GESTIONNAIRES
-- ============================================================

INSERT INTO gestionnaires
(matricule, nom, prenom, email, attribution)
VALUES
('GEST001', 'KOUASSI', 'Jean', 'jean.kouassi@assurance.ci', 'SANTE'),
('GEST002', 'YAO', 'Marie', 'marie.yao@assurance.ci', 'SANTE'),
('GEST003', 'KOFFI', 'Paul', 'paul.koffi@assurance.ci', 'SANTE'),
('GEST004', 'N''GUESSAN', 'Aline', 'aline.nguessan@assurance.ci', 'SANTE'),
('GEST005', 'KONE', 'Ibrahim', 'ibrahim.kone@assurance.ci', 'SANTE');


-- ============================================================
-- 3. CONTRATS
-- ============================================================

INSERT INTO contrats
(
    souscripteur_id,
    compagnie,
    code_compagnie,
    intermediaire,
    code_intermediaire,
    numero_compte,
    numero_police,
    nature_risque,
    police,
    numero_intermediaire_police,
    duree,
    echeance_annuelle,
    fractionnement_prime,
    date_effet,
    date_fin,
    prime_nette_par_personne,
    accessoire_taux,
    taxe_taux
)
VALUES

(
    1,
    'SANLAMALLIANZ ASSURANCES COTE D''IVOIRE',
    'SAA-CI',
    'ASCOMA COTE D''IVOIRE',
    'ASC001',
    'CPT001',
    'POL-SANTE-0001',
    'ASSURANCE SANTE COLLECTIVE',
    'SANTE',
    'ASC-POL-001',
    1,
    '2027-01-01',
    'ANNUEL',
    '2026-01-01',
    '2026-12-31',
    150000.00,
    0.03,
    0.14
),

(
    1,
    'SANLAMALLIANZ ASSURANCES COTE D''IVOIRE',
    'SAA-CI',
    'ASCOMA COTE D''IVOIRE',
    'ASC001',
    'CPT001',
    'POL-SANTE-0002',
    'ASSURANCE SANTE COLLECTIVE',
    'SANTE',
    'ASC-POL-002',
    1,
    '2027-01-01',
    'SEMESTRIEL',
    '2026-01-01',
    '2026-12-31',
    120000.00,
    0.03,
    0.14
),

(
    2,
    'SANLAMALLIANZ ASSURANCES COTE D''IVOIRE',
    'SAA-CI',
    'MARSH COTE D''IVOIRE',
    'MAR001',
    'CPT002',
    'POL-SANTE-0003',
    'ASSURANCE SANTE COLLECTIVE',
    'SANTE',
    'MAR-POL-003',
    1,
    '2027-01-01',
    'ANNUEL',
    '2026-01-01',
    '2026-12-31',
    175000.00,
    0.03,
    0.14
),

(
    3,
    'SANLAMALLIANZ ASSURANCES COTE D''IVOIRE',
    'SAA-CI',
    'AON COTE D''IVOIRE',
    'AON001',
    'CPT003',
    'POL-SANTE-0004',
    'ASSURANCE SANTE COLLECTIVE',
    'SANTE',
    'AON-POL-004',
    1,
    '2027-01-01',
    'ANNUEL',
    '2026-01-01',
    '2026-12-31',
    200000.00,
    0.03,
    0.14
),

(
    4,
    'SANLAMALLIANZ ASSURANCES COTE D''IVOIRE',
    'SAA-CI',
    'ASCOMA COTE D''IVOIRE',
    'ASC001',
    'CPT004',
    'POL-SANTE-0005',
    'ASSURANCE SANTE COLLECTIVE',
    'SANTE',
    'ASC-POL-005',
    1,
    '2027-01-01',
    'ANNUEL',
    '2026-01-01',
    '2026-12-31',
    135000.00,
    0.03,
    0.14
),

(
    5,
    'SANLAMALLIANZ ASSURANCES COTE D''IVOIRE',
    'SAA-CI',
    'MARSH COTE D''IVOIRE',
    'MAR001',
    'CPT005',
    'POL-SANTE-0006',
    'ASSURANCE SANTE COLLECTIVE',
    'SANTE',
    'MAR-POL-006',
    1,
    '2027-01-01',
    'ANNUEL',
    '2026-01-01',
    '2026-12-31',
    100000.00,
    0.03,
    0.14
),

(
    2,
    'SANLAMALLIANZ ASSURANCES COTE D''IVOIRE',
    'SAA-CI',
    'ASCOMA COTE D''IVOIRE',
    'ASC001',
    'CPT002',
    'POL-SANTE-0007',
    'ASSURANCE SANTE COLLECTIVE',
    'SANTE',
    'ASC-POL-007',
    1,
    '2027-01-01',
    'ANNUEL',
    '2026-01-01',
    '2026-12-31',
    160000.00,
    0.03,
    0.14
),

(
    3,
    'SANLAMALLIANZ ASSURANCES COTE D''IVOIRE',
    'SAA-CI',
    'AON COTE D''IVOIRE',
    'AON001',
    'CPT003',
    'POL-SANTE-0008',
    'ASSURANCE SANTE COLLECTIVE',
    'SANTE',
    'AON-POL-008',
    1,
    '2027-01-01',
    'ANNUEL',
    '2026-01-01',
    '2026-12-31',
    180000.00,
    0.03,
    0.14
);


-- ============================================================
-- 4. ASSURES
-- ============================================================

-- Contrat 1 : NSIA Banque
INSERT INTO assures
(contrat_id, numero_assure, nom, prenom, date_naissance,
 sexe, lien_parente, date_entree)
VALUES
(1, 'ASS001', 'KOUAME', 'Yannick', '1985-03-15',
 'M', 'PRINCIPAL', '2026-01-01'),

(1, 'ASS002', 'KOFFI', 'Marie', '1988-07-22',
 'F', 'PRINCIPAL', '2026-01-01'),

(1, 'ASS003', 'YAO', 'Serge', '1990-11-10',
 'M', 'PRINCIPAL', '2026-01-01'),

(1, 'ASS004', 'KONE', 'Aminata', '1992-05-18',
 'F', 'PRINCIPAL', '2026-01-01'),

(1, 'ASS005', 'TRAORE', 'Moussa', '1987-09-05',
 'M', 'PRINCIPAL', '2026-01-01'),

(1, 'ASS006', 'N''GUESSAN', 'Alice', '1991-02-12',
 'F', 'PRINCIPAL', '2026-01-01'),

(1, 'ASS007', 'KOUADIO', 'Franck', '1984-06-30',
 'M', 'PRINCIPAL', '2026-01-01'),

(1, 'ASS008', 'BLE', 'Carine', '1993-12-01',
 'F', 'PRINCIPAL', '2026-01-01'),

(1, 'ASS009', 'KOFFI', 'Didier', '1986-04-20',
 'M', 'PRINCIPAL', '2026-01-01'),

(1, 'ASS010', 'YAO', 'Estelle', '1994-08-14',
 'F', 'PRINCIPAL', '2026-01-01');


-- Contrat 2
INSERT INTO assures
(contrat_id, numero_assure, nom, prenom, date_naissance,
 sexe, lien_parente, date_entree)
VALUES
(2, 'ASS011', 'KOUASSI', 'Jean', '1983-01-12',
 'M', 'PRINCIPAL', '2026-01-01'),

(2, 'ASS012', 'YAO', 'Claudia', '1989-04-17',
 'F', 'PRINCIPAL', '2026-01-01'),

(2, 'ASS013', 'KOFFI', 'Richard', '1985-10-09',
 'M', 'PRINCIPAL', '2026-01-01'),

(2, 'ASS014', 'KONE', 'Fatou', '1990-06-21',
 'F', 'PRINCIPAL', '2026-01-01'),

(2, 'ASS015', 'TRAORE', 'Ibrahim', '1982-09-30',
 'M', 'PRINCIPAL', '2026-01-01');


-- Contrat 3
INSERT INTO assures
(contrat_id, numero_assure, nom, prenom, date_naissance,
 sexe, lien_parente, date_entree)
VALUES
(3, 'ASS016', 'KOUADIO', 'Michel', '1986-02-18',
 'M', 'PRINCIPAL', '2026-01-01'),

(3, 'ASS017', 'YAO', 'Sophie', '1991-07-08',
 'F', 'PRINCIPAL', '2026-01-01'),

(3, 'ASS018', 'KOFFI', 'Patrick', '1988-11-25',
 'M', 'PRINCIPAL', '2026-01-01'),

(3, 'ASS019', 'N''GUESSAN', 'Bernadette', '1993-03-14',
 'F', 'PRINCIPAL', '2026-01-01'),

(3, 'ASS020', 'KONE', 'Oumar', '1984-12-02',
 'M', 'PRINCIPAL', '2026-01-01');


-- Contrat 4
INSERT INTO assures
(contrat_id, numero_assure, nom, prenom, date_naissance,
 sexe, lien_parente, date_entree)
VALUES
(4, 'ASS021', 'KOUAME', 'Alain', '1981-05-20',
 'M', 'PRINCIPAL', '2026-01-01'),

(4, 'ASS022', 'KOFFI', 'Nadine', '1987-09-11',
 'F', 'PRINCIPAL', '2026-01-01'),

(4, 'ASS023', 'YAO', 'François', '1990-01-28',
 'M', 'PRINCIPAL', '2026-01-01'),

(4, 'ASS024', 'KONE', 'Awa', '1992-06-16',
 'F', 'PRINCIPAL', '2026-01-01'),

(4, 'ASS025', 'TRAORE', 'Issa', '1985-08-07',
 'M', 'PRINCIPAL', '2026-01-01');


-- Contrat 5
INSERT INTO assures
(contrat_id, numero_assure, nom, prenom, date_naissance,
 sexe, lien_parente, date_entree)
VALUES
(5, 'ASS026', 'YAO', 'Serge', '1989-01-15',
 'M', 'PRINCIPAL', '2026-01-01'),

(5, 'ASS027', 'KOUASSI', 'Aline', '1991-05-19',
 'F', 'PRINCIPAL', '2026-01-01'),

(5, 'ASS028', 'KOFFI', 'Boris', '1987-10-12',
 'M', 'PRINCIPAL', '2026-01-01'),

(5, 'ASS029', 'KONE', 'Mariame', '1994-02-26',
 'F', 'PRINCIPAL', '2026-01-01'),

(5, 'ASS030', 'BLE', 'Jean-Luc', '1983-07-04',
 'M', 'PRINCIPAL', '2026-01-01');


-- Contrat 6
INSERT INTO assures
(contrat_id, numero_assure, nom, prenom, date_naissance,
 sexe, lien_parente, date_entree)
VALUES
(6, 'ASS031', 'KOUADIO', 'Eric', '1988-04-09',
 'M', 'PRINCIPAL', '2026-01-01'),

(6, 'ASS032', 'YAO', 'Julie', '1990-09-22',
 'F', 'PRINCIPAL', '2026-01-01'),

(6, 'ASS033', 'KOFFI', 'Arnaud', '1986-12-18',
 'M', 'PRINCIPAL', '2026-01-01'),

(6, 'ASS034', 'KONE', 'Mariam', '1993-06-03',
 'F', 'PRINCIPAL', '2026-01-01'),

(6, 'ASS035', 'TRAORE', 'Adama', '1984-11-27',
 'M', 'PRINCIPAL', '2026-01-01');


-- Contrat 7
INSERT INTO assures
(contrat_id, numero_assure, nom, prenom, date_naissance,
 sexe, lien_parente, date_entree)
VALUES
(7, 'ASS036', 'KOUAME', 'Franck', '1985-03-08',
 'M', 'PRINCIPAL', '2026-01-01'),

(7, 'ASS037', 'KOFFI', 'Estelle', '1992-08-15',
 'F', 'PRINCIPAL', '2026-01-01'),

(7, 'ASS038', 'YAO', 'Patrick', '1987-05-23',
 'M', 'PRINCIPAL', '2026-01-01'),

(7, 'ASS039', 'KONE', 'Fatima', '1991-11-19',
 'F', 'PRINCIPAL', '2026-01-01'),

(7, 'ASS040', 'BLE', 'Armand', '1989-02-10',
 'M', 'PRINCIPAL', '2026-01-01');


-- Contrat 8
INSERT INTO assures
(contrat_id, numero_assure, nom, prenom, date_naissance,
 sexe, lien_parente, date_entree)
VALUES
(8, 'ASS041', 'KOUASSI', 'Paul', '1984-06-15',
 'M', 'PRINCIPAL', '2026-01-01'),

(8, 'ASS042', 'KOFFI', 'Carole', '1990-10-20',
 'F', 'PRINCIPAL', '2026-01-01'),

(8, 'ASS043', 'YAO', 'Didier', '1986-03-11',
 'M', 'PRINCIPAL', '2026-01-01'),

(8, 'ASS044', 'KONE', 'Aminata', '1993-07-09',
 'F', 'PRINCIPAL', '2026-01-01'),

(8, 'ASS045', 'TRAORE', 'Moussa', '1982-12-25',
 'M', 'PRINCIPAL', '2026-01-01');


-- ============================================================
-- 5. MOUVEMENTS D'EFFECTIF
-- ============================================================

-- Incorporations

INSERT INTO mouvements_effectif
(
    contrat_id,
    assure_id,
    type_mouvement,
    date_mouvement,
    date_debut_periode,
    date_fin_periode,
    commentaire
)
VALUES

(1, 1, 'INCORPORATION',
 '2026-03-01',
 '2026-03-01',
 '2026-12-31',
 'Incorporation test'),

(1, 2, 'INCORPORATION',
 '2026-04-01',
 '2026-04-01',
 '2026-12-31',
 'Incorporation test'),

(2, 11, 'INCORPORATION',
 '2026-02-15',
 '2026-02-15',
 '2026-12-31',
 'Incorporation test');


-- Retraits

INSERT INTO mouvements_effectif
(
    contrat_id,
    assure_id,
    type_mouvement,
    date_mouvement,
    date_debut_periode,
    date_fin_periode,
    commentaire
)
VALUES

(1, 3, 'RETRAIT',
 '2026-06-30',
 '2026-06-30',
 '2026-12-31',
 'Retrait test'),

(2, 12, 'RETRAIT',
 '2026-08-31',
 '2026-08-31',
 '2026-12-31',
 'Retrait test');


-- ============================================================
-- 6. EDITIONS DEJA EFFECTUEES
-- ============================================================

INSERT INTO editions_contrats
(
    contrat_id,
    gestionnaire_id,
    type_contrat,
    numero_avenant,
    numero_quittance,
    periode_debut,
    periode_fin,
    prime_nette,
    accessoire,
    taxe,
    prime_totale,
    prime_terme,
    mode_calcul,
    format_document,
    statut
)
VALUES

(
    1,
    1,
    'AFFAIRE_NOUVELLE',
    'AV-0001',
    'QT-0001',
    '2026-01-01',
    '2026-12-31',
    1500000.00,
    45000.00,
    216300.00,
    1761300.00,
    1761300.00,
    'ANNUEL',
    'PDF',
    'GENERE'
),

(
    1,
    2,
    'AVENANT_RENOUVELLEMENT',
    'AV-0002',
    'QT-0002',
    '2027-01-01',
    '2027-12-31',
    1800000.00,
    54000.00,
    259560.00,
    2113560.00,
    2113560.00,
    'ANNUEL',
    'WORD',
    'GENERE'
);


-- ============================================================
-- FIN DU SEED
-- ============================================================