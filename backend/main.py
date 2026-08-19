from fastapi import FastAPI, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from .database import get_db

from .models import (
    Souscripteur,
    Contrat,
    College,
    Assure,
    MouvementEffectif,
    Avenant,
    LigneAvenant,
)

from .calculs import (
    calculer_prime_incorporation,
    calculer_ristourne_retrait,
)


# ============================================================
# APPLICATION
# ============================================================

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
            "raison_sociale": s.raison_sociale,
            "adresse": s.adresse,
            "telephone": s.telephone,
            "email": s.email,
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
            "actif": c.actif,
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
        .order_by(
            Assure.nom,
            Assure.prenom
        )
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
            "actif": a.actif,
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
            "commentaire": m.commentaire,
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
            "commentaire": m.commentaire,
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
    # --------------------------------------------------------
    # Vérification du type de mouvement
    # --------------------------------------------------------

    if type_mouvement not in [
        "INCORPORATION",
        "RETRAIT"
    ]:
        raise HTTPException(
            status_code=400,
            detail=(
                "Le type de mouvement doit être "
                "INCORPORATION ou RETRAIT."
            )
        )

    # --------------------------------------------------------
    # Vérifier que le contrat existe
    # --------------------------------------------------------

    contrat = (
        db.query(Contrat)
        .filter(
            Contrat.contrat_id == contrat_id
        )
        .first()
    )

    if not contrat:
        raise HTTPException(
            status_code=404,
            detail="Contrat introuvable."
        )

    # --------------------------------------------------------
    # Vérifier que l'assuré existe
    # --------------------------------------------------------

    assure = (
        db.query(Assure)
        .filter(
            Assure.assure_id == assure_id
        )
        .first()
    )

    if not assure:
        raise HTTPException(
            status_code=404,
            detail="Assuré introuvable."
        )

    # --------------------------------------------------------
    # Vérifier que l'assuré appartient au contrat
    # --------------------------------------------------------

    if assure.contrat_id != contrat_id:
        raise HTTPException(
            status_code=400,
            detail="L'assuré n'appartient pas à ce contrat."
        )

    # --------------------------------------------------------
    # Vérification des dates
    # --------------------------------------------------------

    if date_mouvement < contrat.date_effet:
        raise HTTPException(
            status_code=400,
            detail=(
                "La date du mouvement ne peut pas être "
                "antérieure à la date d'effet du contrat."
            )
        )

    if date_mouvement > contrat.date_fin:
        raise HTTPException(
            status_code=400,
            detail=(
                "La date du mouvement ne peut pas être "
                "postérieure à la date de fin du contrat."
            )
        )

    # --------------------------------------------------------
    # Création du mouvement
    # --------------------------------------------------------

    mouvement = MouvementEffectif(
        contrat_id=contrat_id,
        assure_id=assure_id,
        type_mouvement=type_mouvement,
        date_mouvement=date_mouvement,
        date_debut_periode=date_debut_periode,
        date_fin_periode=date_fin_periode,
        commentaire=commentaire,
    )

    db.add(mouvement)
    db.commit()
    db.refresh(mouvement)

    # --------------------------------------------------------
    # CALCUL FINANCIER
    # --------------------------------------------------------

    if type_mouvement == "INCORPORATION":

        calcul = calculer_prime_incorporation(
            float(contrat.prime_nette_par_personne),
            date_mouvement,
            contrat.date_fin,
        )

    else:

        calcul = calculer_ristourne_retrait(
            float(contrat.prime_nette_par_personne),
            date_mouvement,
            contrat.date_fin,
        )

        # Une ristourne doit être négative
        calcul["montant_ristourne"] = -abs(
            calcul["montant_ristourne"]
        )

    # --------------------------------------------------------
    # Réponse
    # --------------------------------------------------------

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
            "commentaire": mouvement.commentaire,
        },

        "calcul": calcul,
    }


# ============================================================
# DETAIL D'UN MOUVEMENT
# ============================================================

@app.get("/api/mouvements/{mouvement_id}")
def detail_mouvement(
    mouvement_id: int,
    db: Session = Depends(get_db)
):
    # --------------------------------------------------------
    # Récupérer le mouvement
    # --------------------------------------------------------

    mouvement = (
        db.query(MouvementEffectif)
        .filter(
            MouvementEffectif.mouvement_id == mouvement_id
        )
        .first()
    )

    if not mouvement:
        raise HTTPException(
            status_code=404,
            detail="Mouvement introuvable."
        )

    # --------------------------------------------------------
    # Récupérer l'assuré
    # --------------------------------------------------------

    assure = (
        db.query(Assure)
        .filter(
            Assure.assure_id == mouvement.assure_id
        )
        .first()
    )

    if not assure:
        raise HTTPException(
            status_code=404,
            detail="Assuré introuvable."
        )

    # --------------------------------------------------------
    # Récupérer le contrat
    # --------------------------------------------------------

    contrat = (
        db.query(Contrat)
        .filter(
            Contrat.contrat_id == mouvement.contrat_id
        )
        .first()
    )

    if not contrat:
        raise HTTPException(
            status_code=404,
            detail="Contrat introuvable."
        )

    # --------------------------------------------------------
    # Récupérer le souscripteur
    # --------------------------------------------------------

    souscripteur = (
        db.query(Souscripteur)
        .filter(
            Souscripteur.souscripteur_id
            == contrat.souscripteur_id
        )
        .first()
    )

    if not souscripteur:
        raise HTTPException(
            status_code=404,
            detail="Souscripteur introuvable."
        )

    # --------------------------------------------------------
    # CALCUL FINANCIER
    # --------------------------------------------------------

    if mouvement.type_mouvement == "INCORPORATION":

        calcul = calculer_prime_incorporation(
            float(contrat.prime_nette_par_personne),
            mouvement.date_mouvement,
            contrat.date_fin,
        )

    else:

        calcul = calculer_ristourne_retrait(
            float(contrat.prime_nette_par_personne),
            mouvement.date_mouvement,
            contrat.date_fin,
        )

        # Une ristourne doit apparaître comme une valeur négative
        calcul["montant_ristourne"] = -abs(
            calcul["montant_ristourne"]
        )

    # --------------------------------------------------------
    # Réponse détaillée
    # --------------------------------------------------------

    return {
        "mouvement": {
            "id": mouvement.mouvement_id,
            "type_mouvement": mouvement.type_mouvement,
            "date_mouvement": mouvement.date_mouvement,
            "date_debut_periode": mouvement.date_debut_periode,
            "date_fin_periode": mouvement.date_fin_periode,
            "commentaire": mouvement.commentaire,
        },

        "assure": {
            "id": assure.assure_id,
            "numero_assure": assure.numero_assure,
            "nom": assure.nom,
            "prenom": assure.prenom,
            "date_naissance": assure.date_naissance,
            "sexe": assure.sexe,
            "lien_parente": assure.lien_parente,
            "date_entree": assure.date_entree,
            "date_sortie": assure.date_sortie,
            "actif": assure.actif,
        },

        "contrat": {
            "id": contrat.contrat_id,
            "numero_police": contrat.numero_police,
            "compagnie": contrat.compagnie,
            "code_compagnie": contrat.code_compagnie,
            "intermediaire": contrat.intermediaire,
            "code_intermediaire": contrat.code_intermediaire,
            "numero_compte": contrat.numero_compte,
            "nature_risque": contrat.nature_risque,
            "police": contrat.police,
            "numero_intermediaire_police":
                contrat.numero_intermediaire_police,
            "duree": contrat.duree,
            "echeance_annuelle": contrat.echeance_annuelle,
            "fractionnement_prime":
                contrat.fractionnement_prime,
            "date_effet": contrat.date_effet,
            "date_fin": contrat.date_fin,
            "prime_nette_par_personne":
                contrat.prime_nette_par_personne,
            "accessoire_taux": contrat.accessoire_taux,
            "taxe_taux": contrat.taxe_taux,
            "actif": contrat.actif,
        },

        "souscripteur": {
            "id": souscripteur.souscripteur_id,
            "code_souscripteur":
                souscripteur.code_souscripteur,
            "raison_sociale":
                souscripteur.raison_sociale,
            "adresse": souscripteur.adresse,
            "telephone": souscripteur.telephone,
            "email": souscripteur.email,
        },

        "calcul": calcul,
    }

# ============================================================
# PREPARATION DES DONNEES DE L'AVENANT
# ============================================================

@app.get("/api/mouvements/{mouvement_id}/avenant")
def preparer_avenant(
    mouvement_id: int,
    db: Session = Depends(get_db)
):
    # --------------------------------------------------------
    # RECUPERER LE MOUVEMENT
    # --------------------------------------------------------

    mouvement = (
        db.query(MouvementEffectif)
        .filter(
            MouvementEffectif.mouvement_id == mouvement_id
        )
        .first()
    )

    if not mouvement:
        raise HTTPException(
            status_code=404,
            detail="Mouvement introuvable."
        )

    # --------------------------------------------------------
    # RECUPERER L'ASSURE
    # --------------------------------------------------------

    assure = (
        db.query(Assure)
        .filter(
            Assure.assure_id == mouvement.assure_id
        )
        .first()
    )

    if not assure:
        raise HTTPException(
            status_code=404,
            detail="Assuré introuvable."
        )

    # --------------------------------------------------------
    # RECUPERER LE CONTRAT
    # --------------------------------------------------------

    contrat = (
        db.query(Contrat)
        .filter(
            Contrat.contrat_id == mouvement.contrat_id
        )
        .first()
    )

    if not contrat:
        raise HTTPException(
            status_code=404,
            detail="Contrat introuvable."
        )

    # --------------------------------------------------------
    # RECUPERER LE SOUSCRIPTEUR
    # --------------------------------------------------------

    souscripteur = (
        db.query(Souscripteur)
        .filter(
            Souscripteur.souscripteur_id
            == contrat.souscripteur_id
        )
        .first()
    )

    if not souscripteur:
        raise HTTPException(
            status_code=404,
            detail="Souscripteur introuvable."
        )

    # --------------------------------------------------------
    # CALCUL FINANCIER
    # --------------------------------------------------------

    if mouvement.type_mouvement == "INCORPORATION":

        calcul = calculer_prime_incorporation(
            float(contrat.prime_nette_par_personne),
            mouvement.date_mouvement,
            contrat.date_fin
        )

        montant = calcul["montant"]

    else:

        calcul = calculer_ristourne_retrait(
            float(contrat.prime_nette_par_personne),
            mouvement.date_mouvement,
            contrat.date_fin
        )

        # La ristourne est toujours négative
        calcul["montant_ristourne"] = -abs(
            calcul["montant_ristourne"]
        )

        montant = calcul["montant_ristourne"]

    # --------------------------------------------------------
    # PREPARATION DE L'AVENANT
    # --------------------------------------------------------

    return {
        "avenant": {
            "type_mouvement": mouvement.type_mouvement,
            "date_mouvement": mouvement.date_mouvement,
            "date_effet": mouvement.date_mouvement,
            "numero_mouvement": mouvement.mouvement_id
        },

        "souscripteur": {
            "id": souscripteur.souscripteur_id,
            "code": souscripteur.code_souscripteur,
            "raison_sociale": souscripteur.raison_sociale,
            "adresse": souscripteur.adresse,
            "telephone": souscripteur.telephone,
            "email": souscripteur.email
        },

        "contrat": {
            "id": contrat.contrat_id,
            "numero_police": contrat.numero_police,
            "compagnie": contrat.compagnie,
            "code_compagnie": contrat.code_compagnie,
            "intermediaire": contrat.intermediaire,
            "code_intermediaire": contrat.code_intermediaire,
            "numero_compte": contrat.numero_compte,
            "nature_risque": contrat.nature_risque,
            "police": contrat.police,
            "date_effet": contrat.date_effet,
            "date_fin": contrat.date_fin,
            "fractionnement_prime":
                contrat.fractionnement_prime
        },

        "assure": {
            "id": assure.assure_id,
            "numero_assure": assure.numero_assure,
            "nom": assure.nom,
            "prenom": assure.prenom,
            "date_naissance": assure.date_naissance,
            "sexe": assure.sexe,
            "lien_parente": assure.lien_parente,
            "date_entree": assure.date_entree,
            "date_sortie": assure.date_sortie
        },

        "mouvement": {
            "id": mouvement.mouvement_id,
            "type": mouvement.type_mouvement,
            "date": mouvement.date_mouvement,
            "date_debut_periode":
                mouvement.date_debut_periode,
            "date_fin_periode":
                mouvement.date_fin_periode,
            "commentaire": mouvement.commentaire
        },

        "calcul": {
            "prime_annuelle":
                float(contrat.prime_nette_par_personne),

            "prime_mensuelle":
                calcul["prime_mensuelle"],

            "nombre_mois":
                calcul.get(
                    "nombre_mois",
                    calcul.get("nombre_mois_ristourne", 0)
                ),

            "montant": montant
        }
    }

# ============================================================
# COLLEGES D'UN CONTRAT
# ============================================================

@app.get("/api/contrats/{contrat_id}/colleges")
def colleges_contrat(
    contrat_id: int,
    db: Session = Depends(get_db)
):
    colleges = (
        db.query(College)
        .filter(
            College.contrat_id == contrat_id
        )
        .order_by(
            College.numero_college
        )
        .all()
    )

    return [
        {
            "id": c.college_id,
            "contrat_id": c.contrat_id,
            "numero_college": c.numero_college,
            "libelle": c.libelle,
            "prime_nette_par_personne":
                c.prime_nette_par_personne,
            "actif": c.actif,
        }
        for c in colleges
    ]


# ============================================================
# ASSURES D'UN COLLEGE
# ============================================================

@app.get("/api/colleges/{college_id}/assures")
def assures_college(
    college_id: int,
    db: Session = Depends(get_db)
):
    assures = (
        db.query(Assure)
        .filter(
            Assure.college_id == college_id
        )
        .order_by(
            Assure.nom,
            Assure.prenom
        )
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
            "actif": a.actif,
            "college_id": a.college_id,
        }
        for a in assures
    ]


