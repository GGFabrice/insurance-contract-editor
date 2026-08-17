
from fastapi import FastAPI, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from datetime import date

from .database import get_db
from .models import Souscripteur, Contrat, Assure, MouvementEffectif


app = FastAPI(
    title="Insurance Contract Editor",
    description="Application d'édition des contrats d'assurance santé",
    version="1.0.0"
)


# ============================================================
# ACCUEIL
# ============================================================

@app.get("/")
def accueil():
    return {
        "application": "Insurance Contract Editor",
        "status": "OK"
    }


# ============================================================
# SOUSCRIPTEURS
# ============================================================

@app.get("/api/souscripteurs/recherche")
def rechercher_souscripteurs(
    nom: str = Query(..., min_length=2),
    db: Session = Depends(get_db)
):
    souscripteurs = (
        db.query(Souscripteur)
        .filter(
            Souscripteur.raison_sociale.ilike(f"%{nom}%")
        )
        .order_by(Souscripteur.raison_sociale)
        .limit(20)
        .all()
    )

    return [
        {
            "id": s.souscripteur_id,
            "code_souscripteur": s.code_souscripteur,
            "raison_sociale": s.raison_sociale
        }
        for s in souscripteurs
    ]


# ============================================================
# CONTRATS D'UN SOUSCRIPTEUR
# ============================================================

@app.get("/api/souscripteurs/{souscripteur_id}/contrats")
def contrats_souscripteur(
    souscripteur_id: int,
    db: Session = Depends(get_db)
):
    contrats = (
        db.query(Contrat)
        .filter(
            Contrat.souscripteur_id == souscripteur_id
        )
        .order_by(Contrat.numero_police)
        .all()
    )

    return [
        {
            "id": c.contrat_id,
            "numero_police": c.numero_police,
            "compagnie": c.compagnie,
            "code_compagnie": c.code_compagnie,
            "intermediaire": c.intermediaire,
            "code_intermediaire": c.code_intermediaire,
            "numero_compte": c.numero_compte,
            "nature_risque": c.nature_risque,
            "police": c.police,
            "numero_intermediaire_police": c.numero_intermediaire_police,
            "duree": c.duree,
            "echeance_annuelle": c.echeance_annuelle,
            "fractionnement_prime": c.fractionnement_prime,
            "date_effet": c.date_effet,
            "date_fin": c.date_fin,
            "prime_nette_par_personne": c.prime_nette_par_personne,
            "accessoire_taux": c.accessoire_taux,
            "taxe_taux": c.taxe_taux,
            "actif": c.actif
        }
        for c in contrats
    ]


# ============================================================
# ASSURES D'UN CONTRAT
# ============================================================

@app.get("/api/contrats/{contrat_id}/assures")
def assures_contrat(
    contrat_id: int,
    db: Session = Depends(get_db)
):
    assures = (
        db.query(Assure)
        .filter(
            Assure.contrat_id == contrat_id
        )
        .order_by(Assure.nom, Assure.prenom)
        .all()
    )

    return [
        {
            "id": a.assure_id,
            "numero_assure": a.numero_assure,
            "nom": a.nom,
            "prenom": a.prenom,
            "date_naissance": a.date_naissance,
            "sexe": a.sexe,
            "lien_parente": a.lien_parente,
            "date_entree": a.date_entree,
            "date_sortie": a.date_sortie,
            "actif": a.actif
        }
        for a in assures
    ]


# ============================================================
# MOUVEMENTS D'EFFECTIF D'UN CONTRAT
# ============================================================

@app.get("/api/contrats/{contrat_id}/mouvements")
def mouvements_contrat(
    contrat_id: int,
    db: Session = Depends(get_db)
):
    mouvements = (
        db.query(MouvementEffectif)
        .filter(
            MouvementEffectif.contrat_id == contrat_id
        )
        .order_by(
            MouvementEffectif.date_mouvement.desc()
        )
        .all()
    )

    return [
        {
            "id": m.mouvement_id,
            "contrat_id": m.contrat_id,
            "assure_id": m.assure_id,
            "type_mouvement": m.type_mouvement,
            "date_mouvement": m.date_mouvement,
            "date_debut_periode": m.date_debut_periode,
            "date_fin_periode": m.date_fin_periode,
            "commentaire": m.commentaire
        }
        for m in mouvements
    ]


# ============================================================
# MOUVEMENTS D'UN ASSURE
# ============================================================

@app.get("/api/assures/{assure_id}/mouvements")
def mouvements_assure(
    assure_id: int,
    db: Session = Depends(get_db)
):
    mouvements = (
        db.query(MouvementEffectif)
        .filter(
            MouvementEffectif.assure_id == assure_id
        )
        .order_by(
            MouvementEffectif.date_mouvement.desc()
        )
        .all()
    )

    return [
        {
            "id": m.mouvement_id,
            "contrat_id": m.contrat_id,
            "assure_id": m.assure_id,
            "type_mouvement": m.type_mouvement,
            "date_mouvement": m.date_mouvement,
            "date_debut_periode": m.date_debut_periode,
            "date_fin_periode": m.date_fin_periode,
            "commentaire": m.commentaire
        }
        for m in mouvements
    ]


# ============================================================
# CREER UN MOUVEMENT D'EFFECTIF
# ============================================================

@app.post("/api/mouvements")
def creer_mouvement(
    contrat_id: int,
    assure_id: int,
    type_mouvement: str,
    date_mouvement: date,
    date_debut_periode: date | None = None,
    date_fin_periode: date | None = None,
    commentaire: str | None = None,
    db: Session = Depends(get_db)
):
    # Vérification du type de mouvement
    if type_mouvement not in ["INCORPORATION", "RETRAIT"]:
        raise HTTPException(
            status_code=400,
            detail="Le type de mouvement doit être INCORPORATION ou RETRAIT."
        )

    # Vérifier que le contrat existe
    contrat = (
        db.query(Contrat)
        .filter(Contrat.contrat_id == contrat_id)
        .first()
    )

    if not contrat:
        raise HTTPException(
            status_code=404,
            detail="Contrat introuvable."
        )

    # Vérifier que l'assuré existe
    assure = (
        db.query(Assure)
        .filter(Assure.assure_id == assure_id)
        .first()
    )

    if not assure:
        raise HTTPException(
            status_code=404,
            detail="Assuré introuvable."
        )

    # Vérifier que l'assuré appartient bien au contrat
    if assure.contrat_id != contrat_id:
        raise HTTPException(
            status_code=400,
            detail="L'assuré n'appartient pas à ce contrat."
        )

    # Création du mouvement
    mouvement = MouvementEffectif(
        contrat_id=contrat_id,
        assure_id=assure_id,
        type_mouvement=type_mouvement,
        date_mouvement=date_mouvement,
        date_debut_periode=date_debut_periode,
        date_fin_periode=date_fin_periode,
        commentaire=commentaire
    )

    db.add(mouvement)
    db.commit()
    db.refresh(mouvement)

    return {
        "message": "Mouvement créé avec succès.",
        "mouvement": {
            "id": mouvement.mouvement_id,
            "contrat_id": mouvement.contrat_id,
            "assure_id": mouvement.assure_id,
            "type_mouvement": mouvement.type_mouvement,
            "date_mouvement": mouvement.date_mouvement,
            "date_debut_periode": mouvement.date_debut_periode,
            "date_fin_periode": mouvement.date_fin_periode,
            "commentaire": mouvement.commentaire
        }
    }