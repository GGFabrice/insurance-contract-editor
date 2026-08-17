
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
    code_souscripteur = Column(String(50), nullable=False)
    raison_sociale = Column(String(255), nullable=False)
    adresse = Column(String(500))
    telephone = Column(String(50))
    email = Column(String(255))
    created_at = Column(
        DateTime,
        server_default=func.current_timestamp()
    )

    contrats = relationship(
        "Contrat",
        back_populates="souscripteur"
    )


# ============================================================
# CONTRAT
# ============================================================

class Contrat(Base):
    __tablename__ = "contrats"

    contrat_id = Column(Integer, primary_key=True)

    souscripteur_id = Column(
        Integer,
        ForeignKey("souscripteurs.souscripteur_id"),
        nullable=False
    )

    compagnie = Column(String(255), nullable=False)
    code_compagnie = Column(String(50))
    intermediaire = Column(String(255))
    code_intermediaire = Column(String(50))

    numero_compte = Column(String(100))
    numero_police = Column(String(100), nullable=False)
    nature_risque = Column(String(255))
    police = Column(String(255))
    numero_intermediaire_police = Column(String(100))

    duree = Column(Integer)
    echeance_annuelle = Column(Date)
    fractionnement_prime = Column(String(50))

    date_effet = Column(Date, nullable=False)
    date_fin = Column(Date, nullable=False)

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


# ============================================================
# ASSURE
# ============================================================

class Assure(Base):
    __tablename__ = "assures"

    assure_id = Column(Integer, primary_key=True)

    contrat_id = Column(
        Integer,
        ForeignKey("contrats.contrat_id"),
        nullable=False
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

    mouvements = relationship(
        "MouvementEffectif",
        back_populates="assure"
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