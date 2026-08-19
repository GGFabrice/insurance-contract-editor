from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Numeric,
    ForeignKey,
    Boolean,
    Text,
    DateTime,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from .database import Base


# ============================================================
# SOUSCRIPTEUR
# ============================================================

class Souscripteur(Base):
    __tablename__ = "souscripteurs"

    souscripteur_id = Column(Integer, primary_key=True)

    code_souscripteur = Column(
        String(50),
        nullable=False
    )

    raison_sociale = Column(
        String(255),
        nullable=False
    )

    adresse = Column(String(500))
    telephone = Column(String(50))
    email = Column(String(255))

    created_at = Column(
        DateTime,
        server_default=func.current_timestamp()
    )

    # --------------------------------------------------------
    # Relations
    # --------------------------------------------------------

    contrats = relationship(
        "Contrat",
        back_populates="souscripteur"
    )


# ============================================================
# CONTRAT
# ============================================================

class Contrat(Base):
    __tablename__ = "contrats"

    contrat_id = Column(
        Integer,
        primary_key=True
    )

    souscripteur_id = Column(
        Integer,
        ForeignKey("souscripteurs.souscripteur_id"),
        nullable=False
    )

    compagnie = Column(
        String(255),
        nullable=False
    )

    code_compagnie = Column(String(50))

    intermediaire = Column(String(255))
    code_intermediaire = Column(String(50))

    numero_compte = Column(String(100))

    numero_police = Column(
        String(100),
        nullable=False
    )

    nature_risque = Column(String(255))
    police = Column(String(255))

    numero_intermediaire_police = Column(
        String(100)
    )

    duree = Column(Integer)

    echeance_annuelle = Column(Date)

    fractionnement_prime = Column(
        String(50)
    )

    date_effet = Column(
        Date,
        nullable=False
    )

    date_fin = Column(
        Date,
        nullable=False
    )

    # --------------------------------------------------------
    # Ancienne prime conservée pour compatibilité
    # avec les données existantes
    # --------------------------------------------------------

    prime_nette_par_personne = Column(
        Numeric(18, 2),
        nullable=False
    )

    accessoire_taux = Column(
        Numeric(10, 4),
        default=0
    )

    taxe_taux = Column(
        Numeric(10, 4),
        default=0
    )

    actif = Column(
        Boolean,
        default=True
    )

    created_at = Column(
        DateTime,
        server_default=func.current_timestamp()
    )

    # --------------------------------------------------------
    # Relations
    # --------------------------------------------------------

    souscripteur = relationship(
        "Souscripteur",
        back_populates="contrats"
    )

    assures = relationship(
        "Assure",
        back_populates="contrat"
    )

    mouvements = relationship(
        "MouvementEffectif",
        back_populates="contrat"
    )

    colleges = relationship(
        "College",
        back_populates="contrat"
    )

    avenants = relationship(
        "Avenant",
        back_populates="contrat"
    )


# ============================================================
# COLLEGE
# ============================================================

class College(Base):
    __tablename__ = "colleges"

    college_id = Column(
        Integer,
        primary_key=True
    )

    contrat_id = Column(
        Integer,
        ForeignKey("contrats.contrat_id"),
        nullable=False
    )

    numero_college = Column(
        Integer,
        nullable=False
    )

    libelle = Column(
        String(255),
        nullable=False
    )

    prime_nette_par_personne = Column(
        Numeric(18, 2),
        nullable=False,
        default=0
    )

    actif = Column(
        Boolean,
        default=True
    )

    created_at = Column(
        DateTime,
        server_default=func.current_timestamp()
    )

    # --------------------------------------------------------
    # Relations
    # --------------------------------------------------------

    contrat = relationship(
        "Contrat",
        back_populates="colleges"
    )

    assures = relationship(
        "Assure",
        back_populates="college"
    )

    lignes_avenant = relationship(
        "LigneAvenant",
        back_populates="college"
    )


# ============================================================
# ASSURE
# ============================================================

class Assure(Base):
    __tablename__ = "assures"

    assure_id = Column(
        Integer,
        primary_key=True
    )

    contrat_id = Column(
        Integer,
        ForeignKey("contrats.contrat_id"),
        nullable=False
    )

    college_id = Column(
        Integer,
        ForeignKey("colleges.college_id"),
        nullable=True
    )

    numero_assure = Column(
        String(100),
        nullable=False,
        unique=True
    )

    nom = Column(
        String(100),
        nullable=False
    )

    prenom = Column(
        String(100)
    )

    date_naissance = Column(Date)

    sexe = Column(String(20))

    lien_parente = Column(String(100))

    date_entree = Column(
        Date,
        nullable=False
    )

    date_sortie = Column(Date)

    actif = Column(
        Boolean,
        default=True
    )

    created_at = Column(
        DateTime,
        server_default=func.current_timestamp()
    )

    # --------------------------------------------------------
    # Relations
    # --------------------------------------------------------

    contrat = relationship(
        "Contrat",
        back_populates="assures"
    )

    college = relationship(
        "College",
        back_populates="assures"
    )

    mouvements = relationship(
        "MouvementEffectif",
        back_populates="assure"
    )


# ============================================================
# AVENANT
# ============================================================

class Avenant(Base):
    __tablename__ = "avenants"

    avenant_id = Column(
        Integer,
        primary_key=True
    )

    contrat_id = Column(
        Integer,
        ForeignKey("contrats.contrat_id"),
        nullable=False
    )

    numero_avenant = Column(
        String(100),
        nullable=False
    )

    type_avenant = Column(
        String(50),
        nullable=False
    )

    periode_debut = Column(
        Date,
        nullable=False
    )

    periode_fin = Column(
        Date,
        nullable=False
    )

    date_effet = Column(
        Date,
        nullable=False
    )

    date_edition = Column(
        Date,
        server_default=func.current_date()
    )

    prime_nette = Column(
        Numeric(18, 2),
        nullable=False,
        default=0
    )

    accessoire = Column(
        Numeric(18, 2),
        nullable=False,
        default=0
    )

    taxe = Column(
        Numeric(18, 2),
        nullable=False,
        default=0
    )

    prime_totale = Column(
        Numeric(18, 2),
        nullable=False,
        default=0
    )

    statut = Column(
        String(30),
        nullable=False,
        default="BROUILLON"
    )

    commentaire = Column(Text)

    created_at = Column(
        DateTime,
        server_default=func.current_timestamp()
    )

    # --------------------------------------------------------
    # Relations
    # --------------------------------------------------------

    contrat = relationship(
        "Contrat",
        back_populates="avenants"
    )

    lignes = relationship(
        "LigneAvenant",
        back_populates="avenant"
    )

    mouvements = relationship(
        "MouvementEffectif",
        back_populates="avenant"
    )


# ============================================================
# MOUVEMENT EFFECTIF
# ============================================================

class MouvementEffectif(Base):
    __tablename__ = "mouvements_effectif"

    mouvement_id = Column(
        Integer,
        primary_key=True
    )

    contrat_id = Column(
        Integer,
        ForeignKey("contrats.contrat_id"),
        nullable=False
    )

    assure_id = Column(
        Integer,
        ForeignKey("assures.assure_id"),
        nullable=False
    )

    avenant_id = Column(
        Integer,
        ForeignKey("avenants.avenant_id"),
        nullable=True
    )

    type_mouvement = Column(
        String(30),
        nullable=False
    )

    date_mouvement = Column(
        Date,
        nullable=False
    )

    date_debut_periode = Column(Date)

    date_fin_periode = Column(Date)

    commentaire = Column(Text)

    created_at = Column(
        DateTime,
        server_default=func.current_timestamp()
    )

    # --------------------------------------------------------
    # Relations
    # --------------------------------------------------------

    contrat = relationship(
        "Contrat",
        back_populates="mouvements"
    )

    assure = relationship(
        "Assure",
        back_populates="mouvements"
    )

    avenant = relationship(
        "Avenant",
        back_populates="mouvements"
    )


# ============================================================
# LIGNE D'AVENANT
# ============================================================

class LigneAvenant(Base):
    __tablename__ = "lignes_avenant"

    ligne_avenant_id = Column(
        Integer,
        primary_key=True
    )

    avenant_id = Column(
        Integer,
        ForeignKey("avenants.avenant_id"),
        nullable=False
    )

    college_id = Column(
        Integer,
        ForeignKey("colleges.college_id"),
        nullable=False
    )

    nombre_personnes = Column(
        Integer,
        nullable=False,
        default=0
    )

    prime_nette_par_personne = Column(
        Numeric(18, 2),
        nullable=False,
        default=0
    )

    prime_nette = Column(
        Numeric(18, 2),
        nullable=False,
        default=0
    )

    accessoire = Column(
        Numeric(18, 2),
        nullable=False,
        default=0
    )

    taxe = Column(
        Numeric(18, 2),
        nullable=False,
        default=0
    )

    prime_totale = Column(
        Numeric(18, 2),
        nullable=False,
        default=0
    )

    created_at = Column(
        DateTime,
        server_default=func.current_timestamp()
    )

    # --------------------------------------------------------
    # Relations
    # --------------------------------------------------------

    avenant = relationship(
        "Avenant",
        back_populates="lignes"
    )

    college = relationship(
        "College",
        back_populates="lignes_avenant"
    )
