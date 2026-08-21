from datetime import date
from typing import List

from fastapi import FastAPI, Depends, Query, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

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
    calculer_taxe,
)


# ============================================================
# APPLICATION
# ============================================================

app = FastAPI(
    title="Insurance Contract Editor",
    description="Application d'édition des contrats d'assurance santé",
    version="1.0.0",
)


# ============================================================
# SCHEMAS
# ============================================================

class IncorporationAvenantRequest(BaseModel):
    contrat_id: int
    mouvement_ids: List[int]
    periode_debut: date
    periode_fin: date
    commentaire: str | None = None


class RetraitAvenantRequest(BaseModel):
    contrat_id: int
    mouvement_ids: List[int]
    periode_debut: date
    periode_fin: date
    commentaire: str | None = None


# ============================================================
# FONCTIONS UTILITAIRES
# ============================================================

def get_contrat_or_404(
    contrat_id: int,
    db: Session,
) -> Contrat:

    contrat = (
        db.query(Contrat)
        .filter(Contrat.contrat_id == contrat_id)
        .first()
    )

    if not contrat:
        raise HTTPException(
            status_code=404,
            detail="Contrat introuvable.",
        )

    return contrat


def get_souscripteur_or_404(
    souscripteur_id: int,
    db: Session,
) -> Souscripteur:

    souscripteur = (
        db.query(Souscripteur)
        .filter(
            Souscripteur.souscripteur_id
            == souscripteur_id
        )
        .first()
    )

    if not souscripteur:
        raise HTTPException(
            status_code=404,
            detail="Souscripteur introuvable.",
        )

    return souscripteur


def get_assure_or_404(
    assure_id: int,
    db: Session,
) -> Assure:

    assure = (
        db.query(Assure)
        .filter(Assure.assure_id == assure_id)
        .first()
    )

    if not assure:
        raise HTTPException(
            status_code=404,
            detail="Assuré introuvable.",
        )

    return assure


def get_college_or_404(
    college_id: int,
    db: Session,
) -> College:

    college = (
        db.query(College)
        .filter(College.college_id == college_id)
        .first()
    )

    if not college:
        raise HTTPException(
            status_code=404,
            detail="Collège introuvable.",
        )

    return college


def get_mouvement_or_404(
    mouvement_id: int,
    db: Session,
) -> MouvementEffectif:

    mouvement = (
        db.query(MouvementEffectif)
        .filter(
            MouvementEffectif.mouvement_id
            == mouvement_id
        )
        .first()
    )

    if not mouvement:
        raise HTTPException(
            status_code=404,
            detail="Mouvement introuvable.",
        )

    return mouvement


def float_or_zero(value) -> float:
    return float(value or 0)


def valider_periode_avenant(
    contrat: Contrat,
    periode_debut: date,
    periode_fin: date,
):
    if periode_debut > periode_fin:
        raise HTTPException(
            status_code=400,
            detail=(
                "La date de début de période "
                "doit être antérieure ou égale "
                "à la date de fin."
            ),
        )

    if periode_debut < contrat.date_effet:
        raise HTTPException(
            status_code=400,
            detail=(
                "La période de début ne peut pas "
                "être antérieure à la date d'effet "
                "du contrat."
            ),
        )

    if periode_fin > contrat.date_fin:
        raise HTTPException(
            status_code=400,
            detail=(
                "La période de fin ne peut pas "
                "être postérieure à la fin du contrat."
            ),
        )


def obtenir_prime_assure(
    assure: Assure,
    contrat: Contrat,
    db: Session,
):
    college = None

    if assure.college_id is not None:
        college = get_college_or_404(
            assure.college_id,
            db,
        )

    if college is not None:
        prime_annuelle = float(
            college.prime_nette_par_personne
        )
    else:
        prime_annuelle = float(
            contrat.prime_nette_par_personne or 0
        )

    return college, prime_annuelle


def calculer_mouvement(
    mouvement: MouvementEffectif,
    contrat: Contrat,
    prime_annuelle: float,
):
    if mouvement.type_mouvement == "INCORPORATION":

        return calculer_prime_incorporation(
            prime_annuelle=prime_annuelle,
            date_effet=mouvement.date_mouvement,
            date_fin_contrat=contrat.date_fin,
        )

    calcul = calculer_ristourne_retrait(
        prime_annuelle=prime_annuelle,
        date_retrait=mouvement.date_mouvement,
        date_fin_contrat=contrat.date_fin,
    )

    calcul["montant_ristourne"] = -abs(
        calcul["montant_ristourne"]
    )

    return calcul


def obtenir_nouveau_numero_avenant(
    contrat_id: int,
    db: Session,
) -> str:

    avenants = (
        db.query(Avenant)
        .filter(Avenant.contrat_id == contrat_id)
        .all()
    )

    numeros_utilises = set()

    for avenant_existant in avenants:

        try:
            numeros_utilises.add(
                int(avenant_existant.numero_avenant)
            )

        except (ValueError, TypeError):
            continue

    numero = 1

    while numero in numeros_utilises:
        numero += 1

    return str(numero)


def charger_mouvements(
    mouvement_ids: List[int],
    db: Session,
):
    ids_uniques = list(dict.fromkeys(mouvement_ids))

    if not ids_uniques:
        raise HTTPException(
            status_code=400,
            detail="Aucun mouvement sélectionné.",
        )

    mouvements = (
        db.query(MouvementEffectif)
        .filter(
            MouvementEffectif.mouvement_id.in_(
                ids_uniques
            )
        )
        .all()
    )

    mouvements_par_id = {
        mouvement.mouvement_id: mouvement
        for mouvement in mouvements
    }

    mouvements_manquants = [
        mouvement_id
        for mouvement_id in ids_uniques
        if mouvement_id not in mouvements_par_id
    ]

    if mouvements_manquants:
        raise HTTPException(
            status_code=404,
            detail={
                "message": (
                    "Un ou plusieurs mouvements "
                    "sont introuvables."
                ),
                "mouvements_manquants": mouvements_manquants,
            },
        )

    return [
        mouvements_par_id[mouvement_id]
        for mouvement_id in ids_uniques
    ]


def valider_mouvements_avenant(
    mouvements,
    contrat_id: int,
    type_mouvement: str,
    periode_debut: date,
    periode_fin: date,
    verifier_avenant: bool = False,
):
    erreurs = []

    for mouvement in mouvements:

        if mouvement.contrat_id != contrat_id:

            erreurs.append(
                {
                    "id": mouvement.mouvement_id,
                    "erreur": "Contrat incorrect",
                }
            )

            continue

        if mouvement.type_mouvement != type_mouvement:

            erreurs.append(
                {
                    "id": mouvement.mouvement_id,
                    "erreur": (
                        f"Le mouvement n'est pas "
                        f"un {type_mouvement.lower()}"
                    ),
                }
            )

            continue

        if not (
            periode_debut
            <= mouvement.date_mouvement
            <= periode_fin
        ):

            erreurs.append(
                {
                    "id": mouvement.mouvement_id,
                    "erreur": (
                        "Le mouvement est en dehors "
                        "de la période"
                    ),
                }
            )

            continue

        if (
            verifier_avenant
            and mouvement.avenant_id is not None
        ):

            erreurs.append(
                {
                    "id": mouvement.mouvement_id,
                    "erreur": (
                        "Le mouvement est déjà "
                        "rattaché à un avenant"
                    ),
                }
            )

    if erreurs:
        raise HTTPException(
            status_code=400,
            detail={
                "message": (
                    "Certains mouvements ne peuvent "
                    "pas être utilisés."
                ),
                "mouvements_invalides": erreurs,
            },
        )


def construire_lignes_mouvements(
    mouvements,
    contrat: Contrat,
    db: Session,
):
    lignes_par_college = {}
    assures_deja_vus = set()

    for mouvement in mouvements:

        assure = get_assure_or_404(
            mouvement.assure_id,
            db,
        )

        if assure.assure_id in assures_deja_vus:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"L'assuré "
                    f"{assure.numero_assure} "
                    "apparaît plusieurs fois "
                    "dans cet avenant."
                ),
            )

        assures_deja_vus.add(
            assure.assure_id
        )

        if assure.college_id is None:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"L'assuré "
                    f"{assure.numero_assure} "
                    "n'est affecté à aucun collège."
                ),
            )

        college = get_college_or_404(
            assure.college_id,
            db,
        )

        if college.contrat_id != contrat.contrat_id:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Le collège de l'assuré "
                    f"{assure.numero_assure} "
                    "n'appartient pas au contrat."
                ),
            )

        prime_annuelle = float(
            college.prime_nette_par_personne
        )

        calcul = calculer_mouvement(
            mouvement,
            contrat,
            prime_annuelle,
        )

        if mouvement.type_mouvement == "INCORPORATION":
            montant = calcul["montant"]
        else:
            montant = calcul["montant_ristourne"]

        college_id = college.college_id

        if college_id not in lignes_par_college:

            lignes_par_college[college_id] = {
                "college_id": college.college_id,
                "numero_college": college.numero_college,
                "libelle": college.libelle,
                "prime_nette_par_personne": prime_annuelle,
                "nombre_personnes": 0,
                "prime_nette": 0.0,
                "personnes": [],
            }

        ligne = lignes_par_college[college_id]

        ligne["nombre_personnes"] += 1
        ligne["prime_nette"] += montant

        personne = {
            "mouvement_id": mouvement.mouvement_id,
            "assure_id": assure.assure_id,
            "numero_assure": assure.numero_assure,
            "nom": assure.nom,
            "prenom": assure.prenom,
            "college_id": college.college_id,
            "numero_college": college.numero_college,
            "date_effet": (
                mouvement.date_mouvement
                if mouvement.type_mouvement
                == "INCORPORATION"
                else None
            ),
            "date_retrait": (
                mouvement.date_mouvement
                if mouvement.type_mouvement == "RETRAIT"
                else None
            ),
            "nombre_mois": calcul.get(
                "nombre_mois",
                calcul.get("nombre_mois_ristourne", 0),
            ),
            "prime_mensuelle": calcul.get(
                "prime_mensuelle",
                0,
            ),
        }

        if mouvement.type_mouvement == "INCORPORATION":
            personne["prime_incorporation"] = montant
        else:
            personne["ristourne"] = montant

        ligne["personnes"].append(personne)

    return lignes_par_college


def calculer_totaux_avenant(
    lignes_par_college,
    contrat: Contrat,
    souscripteur: Souscripteur,
):
    prime_nette_totale = sum(
        ligne["prime_nette"]
        for ligne in lignes_par_college.values()
    )

    # Pour un retrait, on conserve un accessoire positif.
    if prime_nette_totale < 0:
        base_accessoire = abs(prime_nette_totale)
    else:
        base_accessoire = prime_nette_totale

    accessoire = (
        base_accessoire
        * float(contrat.accessoire_taux or 0)
    )

    resultat_taxe = calculer_taxe(
        prime_nette_totale=prime_nette_totale,
        accessoire=accessoire,
        type_souscripteur=souscripteur.type_souscripteur,
    )

    return {
        "prime_nette_totale": prime_nette_totale,
        "accessoire": accessoire,
        "resultat_taxe": resultat_taxe,
    }


def colleges_resultat(
    lignes_par_college,
):
    return sorted(
        lignes_par_college.values(),
        key=lambda ligne: ligne["numero_college"],
    )


# ============================================================
# ACCUEIL
# ============================================================

@app.get("/")
def accueil():
    return {
        "application": "Insurance Contract Editor",
        "status": "OK",
    }


# ============================================================
# SOUSCRIPTEURS
# ============================================================

@app.get("/api/souscripteurs/recherche")
def rechercher_souscripteurs(
    nom: str = Query(..., min_length=2),
    db: Session = Depends(get_db),
):
    souscripteurs = (
        db.query(Souscripteur)
        .filter(
            Souscripteur.raison_sociale.ilike(
                f"%{nom}%"
            )
        )
        .order_by(
            Souscripteur.raison_sociale
        )
        .limit(20)
        .all()
    )

    return [
        {
            "id": s.souscripteur_id,
            "code_souscripteur": s.code_souscripteur,
            "raison_sociale": s.raison_sociale,
            "type_souscripteur": s.type_souscripteur,
            "adresse": s.adresse,
            "telephone": s.telephone,
            "email": s.email,
        }
        for s in souscripteurs
    ]


# ============================================================
# MODIFIER LE TYPE DE SOUSCRIPTEUR
# ============================================================

@app.put("/api/souscripteurs/{souscripteur_id}/type")
def modifier_type_souscripteur(
    souscripteur_id: int,
    type_souscripteur: str,
    db: Session = Depends(get_db),
):
    types_autorises = {
        "ENTREPRISE",
        "PARTICULIER",
    }

    if type_souscripteur not in types_autorises:
        raise HTTPException(
            status_code=400,
            detail=(
                "Le type de souscripteur doit être "
                "ENTREPRISE ou PARTICULIER."
            ),
        )

    souscripteur = get_souscripteur_or_404(
        souscripteur_id,
        db,
    )

    souscripteur.type_souscripteur = (
        type_souscripteur
    )

    db.commit()
    db.refresh(souscripteur)

    return {
        "message": (
            "Type de souscripteur "
            "modifié avec succès."
        ),
        "souscripteur": {
            "id": souscripteur.souscripteur_id,
            "code_souscripteur": (
                souscripteur.code_souscripteur
            ),
            "raison_sociale": (
                souscripteur.raison_sociale
            ),
            "type_souscripteur": (
                souscripteur.type_souscripteur
            ),
        },
    }


# ============================================================
# CONTRATS D'UN SOUSCRIPTEUR
# ============================================================

@app.get("/api/souscripteurs/{souscripteur_id}/contrats")
def contrats_souscripteur(
    souscripteur_id: int,
    db: Session = Depends(get_db),
):
    get_souscripteur_or_404(
        souscripteur_id,
        db,
    )

    contrats = (
        db.query(Contrat)
        .filter(
            Contrat.souscripteur_id
            == souscripteur_id
        )
        .order_by(
            Contrat.numero_police
        )
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
            "numero_intermediaire_police": (
                c.numero_intermediaire_police
            ),
            "duree": c.duree,
            "echeance_annuelle": c.echeance_annuelle,
            "fractionnement_prime": c.fractionnement_prime,
            "date_effet": c.date_effet,
            "date_fin": c.date_fin,
            "prime_nette_par_personne": (
                c.prime_nette_par_personne
            ),
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
    db: Session = Depends(get_db),
):
    get_contrat_or_404(
        contrat_id,
        db,
    )

    assures = (
        db.query(Assure)
        .filter(
            Assure.contrat_id == contrat_id
        )
        .order_by(
            Assure.nom,
            Assure.prenom,
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


# ============================================================
# COLLEGES D'UN CONTRAT
# ============================================================

@app.get("/api/contrats/{contrat_id}/colleges")
def colleges_contrat(
    contrat_id: int,
    db: Session = Depends(get_db),
):
    get_contrat_or_404(
        contrat_id,
        db,
    )

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
            "prime_nette_par_personne": float(
                c.prime_nette_par_personne
            ),
            "actif": c.actif,
        }
        for c in colleges
    ]


# ============================================================
# CALCUL DE LA PRIME D'UN CONTRAT
# ============================================================

@app.get("/api/contrats/{contrat_id}/calcul-prime")
def calcul_prime_contrat(
    contrat_id: int,
    db: Session = Depends(get_db),
):
    contrat = get_contrat_or_404(
        contrat_id,
        db,
    )

    souscripteur = get_souscripteur_or_404(
        contrat.souscripteur_id,
        db,
    )

    colleges = (
        db.query(College)
        .filter(
            College.contrat_id == contrat_id,
            College.actif.is_(True),
        )
        .order_by(
            College.numero_college
        )
        .all()
    )

    if not colleges:
        raise HTTPException(
            status_code=404,
            detail=(
                "Aucun collège actif trouvé "
                "pour ce contrat."
            ),
        )

    details_colleges = []
    prime_nette_totale = 0.0

    for college in colleges:

        nombre_personnes = (
            db.query(Assure)
            .filter(
                Assure.contrat_id == contrat_id,
                Assure.college_id
                == college.college_id,
                Assure.actif.is_(True),
            )
            .count()
        )

        prime_nette_par_personne = float(
            college.prime_nette_par_personne
        )

        prime_nette_college = (
            nombre_personnes
            * prime_nette_par_personne
        )

        prime_nette_totale += (
            prime_nette_college
        )

        details_colleges.append(
            {
                "college_id": college.college_id,
                "numero_college": (
                    college.numero_college
                ),
                "libelle": college.libelle,
                "nombre_personnes": nombre_personnes,
                "prime_nette_par_personne": (
                    prime_nette_par_personne
                ),
                "prime_nette_college": (
                    prime_nette_college
                ),
            }
        )

    accessoire = (
        prime_nette_totale
        * float(contrat.accessoire_taux or 0)
    )

    resultat_taxe = calculer_taxe(
        prime_nette_totale=prime_nette_totale,
        accessoire=accessoire,
        type_souscripteur=(
            souscripteur.type_souscripteur
        ),
    )

    return {
        "souscripteur": {
            "id": souscripteur.souscripteur_id,
            "code_souscripteur": (
                souscripteur.code_souscripteur
            ),
            "raison_sociale": (
                souscripteur.raison_sociale
            ),
            "type_souscripteur": (
                souscripteur.type_souscripteur
            ),
        },
        "contrat": {
            "id": contrat.contrat_id,
            "numero_police": contrat.numero_police,
            "date_effet": contrat.date_effet,
            "date_fin": contrat.date_fin,
        },
        "colleges": details_colleges,
        "totaux": {
            "prime_nette_totale": prime_nette_totale,
            "accessoire_taux": float(
                contrat.accessoire_taux or 0
            ),
            "accessoire": accessoire,
            "base_taxable": (
                resultat_taxe["base_taxable"]
            ),
            "taxe_taux": (
                resultat_taxe["taux_taxe"]
            ),
            "taxe": resultat_taxe["taxe"],
            "prime_ttc": resultat_taxe["prime_ttc"],
        },
    }


# ============================================================
# CREER UN COLLEGE
# ============================================================

@app.post("/api/contrats/{contrat_id}/colleges")
def creer_college(
    contrat_id: int,
    numero_college: int,
    libelle: str,
    prime_nette_par_personne: float,
    db: Session = Depends(get_db),
):
    get_contrat_or_404(
        contrat_id,
        db,
    )

    if numero_college <= 0:
        raise HTTPException(
            status_code=400,
            detail=(
                "Le numéro du collège "
                "doit être supérieur à 0."
            ),
        )

    if not libelle.strip():
        raise HTTPException(
            status_code=400,
            detail="Le libellé du collège est obligatoire.",
        )

    if prime_nette_par_personne < 0:
        raise HTTPException(
            status_code=400,
            detail=(
                "La prime nette par personne "
                "ne peut pas être négative."
            ),
        )

    college_existant = (
        db.query(College)
        .filter(
            College.contrat_id == contrat_id,
            College.numero_college
            == numero_college,
        )
        .first()
    )

    if college_existant:
        raise HTTPException(
            status_code=400,
            detail=(
                "Ce numéro de collège existe déjà "
                "pour ce contrat."
            ),
        )

    college = College(
        contrat_id=contrat_id,
        numero_college=numero_college,
        libelle=libelle.strip(),
        prime_nette_par_personne=(
            prime_nette_par_personne
        ),
        actif=True,
    )

    db.add(college)
    db.commit()
    db.refresh(college)

    return {
        "message": "Collège créé avec succès.",
        "college": {
            "id": college.college_id,
            "contrat_id": college.contrat_id,
            "numero_college": college.numero_college,
            "libelle": college.libelle,
            "prime_nette_par_personne": float(
                college.prime_nette_par_personne
            ),
            "actif": college.actif,
        },
    }


# ============================================================
# ASSURES D'UN COLLEGE
# ============================================================

@app.get("/api/colleges/{college_id}/assures")
def assures_college(
    college_id: int,
    db: Session = Depends(get_db),
):
    get_college_or_404(
        college_id,
        db,
    )

    assures = (
        db.query(Assure)
        .filter(
            Assure.college_id == college_id
        )
        .order_by(
            Assure.nom,
            Assure.prenom,
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


# ============================================================
# AFFECTER UN ASSURE A UN COLLEGE
# ============================================================

@app.put("/api/assures/{assure_id}/college")
def affecter_assure_college(
    assure_id: int,
    college_id: int,
    db: Session = Depends(get_db),
):
    assure = get_assure_or_404(
        assure_id,
        db,
    )

    college = get_college_or_404(
        college_id,
        db,
    )

    if college.contrat_id != assure.contrat_id:
        raise HTTPException(
            status_code=400,
            detail=(
                "Le collège n'appartient pas "
                "au contrat de l'assuré."
            ),
        )

    assure.college_id = college_id

    db.commit()
    db.refresh(assure)

    return {
        "message": (
            "Assuré affecté au collège avec succès."
        ),
        "assure": {
            "id": assure.assure_id,
            "numero_assure": assure.numero_assure,
            "nom": assure.nom,
            "prenom": assure.prenom,
            "college_id": assure.college_id,
        },
    }


# ============================================================
# MOUVEMENTS D'EFFECTIF D'UN CONTRAT
# ============================================================

@app.get("/api/contrats/{contrat_id}/mouvements")
def mouvements_contrat(
    contrat_id: int,
    db: Session = Depends(get_db),
):
    get_contrat_or_404(
        contrat_id,
        db,
    )

    mouvements = (
        db.query(MouvementEffectif)
        .filter(
            MouvementEffectif.contrat_id
            == contrat_id
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
            "avenant_id": m.avenant_id,
            "type_mouvement": m.type_mouvement,
            "date_mouvement": m.date_mouvement,
            "date_debut_periode": (
                m.date_debut_periode
            ),
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
    db: Session = Depends(get_db),
):
    get_assure_or_404(
        assure_id,
        db,
    )

    mouvements = (
        db.query(MouvementEffectif)
        .filter(
            MouvementEffectif.assure_id
            == assure_id
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
            "avenant_id": m.avenant_id,
            "type_mouvement": m.type_mouvement,
            "date_mouvement": m.date_mouvement,
            "date_debut_periode": (
                m.date_debut_periode
            ),
            "date_fin_periode": m.date_fin_periode,
            "commentaire": m.commentaire,
        }
        for m in mouvements
    ]


# ============================================================
# CREER UN MOUVEMENT
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
    db: Session = Depends(get_db),
):
    types_autorises = {
        "INCORPORATION",
        "RETRAIT",
    }

    if type_mouvement not in types_autorises:
        raise HTTPException(
            status_code=400,
            detail=(
                "Le type de mouvement doit être "
                "INCORPORATION ou RETRAIT."
            ),
        )

    contrat = get_contrat_or_404(
        contrat_id,
        db,
    )

    assure = get_assure_or_404(
        assure_id,
        db,
    )

    if assure.contrat_id != contrat_id:
        raise HTTPException(
            status_code=400,
            detail=(
                "L'assuré n'appartient pas "
                "à ce contrat."
            ),
        )

    if date_mouvement < contrat.date_effet:
        raise HTTPException(
            status_code=400,
            detail=(
                "La date du mouvement ne peut pas "
                "être antérieure à la date d'effet "
                "du contrat."
            ),
        )

    if date_mouvement > contrat.date_fin:
        raise HTTPException(
            status_code=400,
            detail=(
                "La date du mouvement ne peut pas "
                "être postérieure à la date de fin "
                "du contrat."
            ),
        )

    if assure.college_id is None:
        raise HTTPException(
            status_code=400,
            detail=(
                "L'assuré doit être affecté à un "
                "collège avant la création "
                "du mouvement."
            ),
        )

    college = get_college_or_404(
        assure.college_id,
        db,
    )

    if college.contrat_id != contrat_id:
        raise HTTPException(
            status_code=400,
            detail=(
                "Le collège de l'assuré n'est pas "
                "rattaché à ce contrat."
            ),
        )

    if date_fin_periode is None:
        date_fin_periode = contrat.date_fin

    mouvement = MouvementEffectif(
        contrat_id=contrat_id,
        assure_id=assure_id,
        type_mouvement=type_mouvement,
        date_mouvement=date_mouvement,
        date_debut_periode=date_debut_periode,
        date_fin_periode=date_fin_periode,
        commentaire=commentaire,
    )

    try:

        db.add(mouvement)
        db.commit()
        db.refresh(mouvement)

    except Exception:
        db.rollback()
        raise

    calcul = calculer_mouvement(
        mouvement,
        contrat,
        float(
            college.prime_nette_par_personne
        ),
    )

    return {
        "message": "Mouvement créé avec succès.",
        "mouvement": {
            "id": mouvement.mouvement_id,
            "contrat_id": mouvement.contrat_id,
            "assure_id": mouvement.assure_id,
            "avenant_id": mouvement.avenant_id,
            "college_id": assure.college_id,
            "type_mouvement": mouvement.type_mouvement,
            "date_mouvement": mouvement.date_mouvement,
            "date_debut_periode": (
                mouvement.date_debut_periode
            ),
            "date_fin_periode": (
                mouvement.date_fin_periode
            ),
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
    db: Session = Depends(get_db),
):
    mouvement = get_mouvement_or_404(
        mouvement_id,
        db,
    )

    assure = get_assure_or_404(
        mouvement.assure_id,
        db,
    )

    contrat = get_contrat_or_404(
        mouvement.contrat_id,
        db,
    )

    souscripteur = get_souscripteur_or_404(
        contrat.souscripteur_id,
        db,
    )

    college, prime_annuelle = obtenir_prime_assure(
        assure,
        contrat,
        db,
    )

    calcul = calculer_mouvement(
        mouvement,
        contrat,
        prime_annuelle,
    )

    return {
        "mouvement": {
            "id": mouvement.mouvement_id,
            "type_mouvement": mouvement.type_mouvement,
            "avenant_id": mouvement.avenant_id,
            "college_id": assure.college_id,
            "date_mouvement": mouvement.date_mouvement,
            "date_debut_periode": (
                mouvement.date_debut_periode
            ),
            "date_fin_periode": (
                mouvement.date_fin_periode
            ),
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
        "college": (
            {
                "id": college.college_id,
                "numero_college": college.numero_college,
                "libelle": college.libelle,
                "prime_nette_par_personne": float(
                    college.prime_nette_par_personne
                ),
                "actif": college.actif,
            }
            if college
            else None
        ),
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
            "numero_intermediaire_police": (
                contrat.numero_intermediaire_police
            ),
            "duree": contrat.duree,
            "echeance_annuelle": (
                contrat.echeance_annuelle
            ),
            "fractionnement_prime": (
                contrat.fractionnement_prime
            ),
            "date_effet": contrat.date_effet,
            "date_fin": contrat.date_fin,
            "prime_nette_par_personne": (
                contrat.prime_nette_par_personne
            ),
            "accessoire_taux": contrat.accessoire_taux,
            "taxe_taux": contrat.taxe_taux,
            "actif": contrat.actif,
        },
        "souscripteur": {
            "id": souscripteur.souscripteur_id,
            "code_souscripteur": (
                souscripteur.code_souscripteur
            ),
            "raison_sociale": (
                souscripteur.raison_sociale
            ),
            "type_souscripteur": (
                souscripteur.type_souscripteur
            ),
            "adresse": souscripteur.adresse,
            "telephone": souscripteur.telephone,
            "email": souscripteur.email,
        },
        "calcul": calcul,
    }


# ============================================================
# PREPARER UN AVENANT INDIVIDUEL
# ============================================================

@app.get("/api/mouvements/{mouvement_id}/avenant")
def preparer_avenant(
    mouvement_id: int,
    db: Session = Depends(get_db),
):
    mouvement = get_mouvement_or_404(
        mouvement_id,
        db,
    )

    assure = get_assure_or_404(
        mouvement.assure_id,
        db,
    )

    contrat = get_contrat_or_404(
        mouvement.contrat_id,
        db,
    )

    souscripteur = get_souscripteur_or_404(
        contrat.souscripteur_id,
        db,
    )

    college, prime_annuelle = obtenir_prime_assure(
        assure,
        contrat,
        db,
    )

    calcul = calculer_mouvement(
        mouvement,
        contrat,
        prime_annuelle,
    )

    if mouvement.type_mouvement == "INCORPORATION":
        montant = calcul["montant"]
    else:
        montant = calcul["montant_ristourne"]

    return {
        "avenant": {
            "type_mouvement": mouvement.type_mouvement,
            "date_mouvement": mouvement.date_mouvement,
            "date_effet": mouvement.date_mouvement,
            "numero_mouvement": mouvement.mouvement_id,
        },
        "souscripteur": {
            "id": souscripteur.souscripteur_id,
            "code": souscripteur.code_souscripteur,
            "raison_sociale": (
                souscripteur.raison_sociale
            ),
            "type_souscripteur": (
                souscripteur.type_souscripteur
            ),
            "adresse": souscripteur.adresse,
            "telephone": souscripteur.telephone,
            "email": souscripteur.email,
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
            "fractionnement_prime": (
                contrat.fractionnement_prime
            ),
        },
        "college": (
            {
                "id": college.college_id,
                "numero_college": college.numero_college,
                "libelle": college.libelle,
                "prime_nette_par_personne": float(
                    college.prime_nette_par_personne
                ),
            }
            if college
            else None
        ),
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
        },
        "mouvement": {
            "id": mouvement.mouvement_id,
            "type": mouvement.type_mouvement,
            "date": mouvement.date_mouvement,
            "date_debut_periode": (
                mouvement.date_debut_periode
            ),
            "date_fin_periode": (
                mouvement.date_fin_periode
            ),
            "commentaire": mouvement.commentaire,
        },
        "calcul": {
            "prime_annuelle": prime_annuelle,
            "prime_mensuelle": calcul.get(
                "prime_mensuelle",
                0,
            ),
            "nombre_mois": calcul.get(
                "nombre_mois",
                calcul.get(
                    "nombre_mois_ristourne",
                    0,
                ),
            ),
            "montant": montant,
        },
    }


# ============================================================
# PREVIEW INCORPORATION
# ============================================================

@app.post("/api/avenants/incorporation/preview")
def preview_avenant_incorporation(
    request: IncorporationAvenantRequest,
    db: Session = Depends(get_db),
):
    contrat = get_contrat_or_404(
        request.contrat_id,
        db,
    )

    valider_periode_avenant(
        contrat,
        request.periode_debut,
        request.periode_fin,
    )

    mouvements = charger_mouvements(
        request.mouvement_ids,
        db,
    )

    valider_mouvements_avenant(
        mouvements=mouvements,
        contrat_id=request.contrat_id,
        type_mouvement="INCORPORATION",
        periode_debut=request.periode_debut,
        periode_fin=request.periode_fin,
        verifier_avenant=False,
    )

    souscripteur = get_souscripteur_or_404(
        contrat.souscripteur_id,
        db,
    )

    lignes_par_college = construire_lignes_mouvements(
        mouvements,
        contrat,
        db,
    )

    totaux = calculer_totaux_avenant(
        lignes_par_college,
        contrat,
        souscripteur,
    )

    resultat_colleges = colleges_resultat(
        lignes_par_college
    )

    return {
        "type_avenant": "AVENANT_INCORPORATION",
        "mode": "PREVIEW",
        "contrat": {
            "id": contrat.contrat_id,
            "numero_police": contrat.numero_police,
            "date_effet": contrat.date_effet,
            "date_fin": contrat.date_fin,
        },
        "souscripteur": {
            "id": souscripteur.souscripteur_id,
            "code_souscripteur": (
                souscripteur.code_souscripteur
            ),
            "raison_sociale": (
                souscripteur.raison_sociale
            ),
            "type_souscripteur": (
                souscripteur.type_souscripteur
            ),
        },
        "periode": {
            "debut": request.periode_debut,
            "fin": request.periode_fin,
        },
        "nombre_mouvements": len(mouvements),
        "colleges": resultat_colleges,
        "totaux": {
            "prime_nette_totale": (
                totaux["prime_nette_totale"]
            ),
            "accessoire_taux": float(
                contrat.accessoire_taux or 0
            ),
            "accessoire": totaux["accessoire"],
            "base_taxable": (
                totaux["resultat_taxe"]["base_taxable"]
            ),
            "taxe_taux": (
                totaux["resultat_taxe"]["taux_taxe"]
            ),
            "taxe": (
                totaux["resultat_taxe"]["taxe"]
            ),
            "prime_ttc": (
                totaux["resultat_taxe"]["prime_ttc"]
            ),
        },
        "commentaire": request.commentaire,
    }


# ============================================================
# CREATION AVENANT INCORPORATION
# ============================================================

@app.post("/api/avenants/incorporation")
def creer_avenant_incorporation(
    request: IncorporationAvenantRequest,
    db: Session = Depends(get_db),
):
    try:

        contrat = get_contrat_or_404(
            request.contrat_id,
            db,
        )

        valider_periode_avenant(
            contrat,
            request.periode_debut,
            request.periode_fin,
        )

        mouvements = charger_mouvements(
            request.mouvement_ids,
            db,
        )

        valider_mouvements_avenant(
            mouvements=mouvements,
            contrat_id=request.contrat_id,
            type_mouvement="INCORPORATION",
            periode_debut=request.periode_debut,
            periode_fin=request.periode_fin,
            verifier_avenant=True,
        )

        souscripteur = get_souscripteur_or_404(
            contrat.souscripteur_id,
            db,
        )

        lignes_par_college = (
            construire_lignes_mouvements(
                mouvements,
                contrat,
                db,
            )
        )

        totaux = calculer_totaux_avenant(
            lignes_par_college,
            contrat,
            souscripteur,
        )

        resultat_taxe = totaux["resultat_taxe"]

        numero = obtenir_nouveau_numero_avenant(
            request.contrat_id,
            db,
        )

        date_effet = min(
            mouvement.date_mouvement
            for mouvement in mouvements
        )

        avenant = Avenant(
            contrat_id=request.contrat_id,
            numero_avenant=numero,
            type_avenant="AVENANT_INCORPORATION",
            periode_debut=request.periode_debut,
            periode_fin=request.periode_fin,
            date_effet=date_effet,
            prime_nette=(
                totaux["prime_nette_totale"]
            ),
            accessoire=totaux["accessoire"],
            taxe=resultat_taxe["taxe"],
            prime_totale=resultat_taxe["prime_ttc"],
            statut="VALIDE",
            commentaire=request.commentaire,
        )

        db.add(avenant)
        db.flush()

        for ligne in sorted(
            lignes_par_college.values(),
            key=lambda item: item["numero_college"],
        ):

            prime_nette_college = (
                ligne["prime_nette"]
            )

            accessoire_college = (
                prime_nette_college
                * float(
                    contrat.accessoire_taux or 0
                )
            )

            resultat_taxe_college = calculer_taxe(
                prime_nette_totale=(
                    prime_nette_college
                ),
                accessoire=accessoire_college,
                type_souscripteur=(
                    souscripteur.type_souscripteur
                ),
            )

            ligne_avenant = LigneAvenant(
                avenant_id=avenant.avenant_id,
                college_id=ligne["college_id"],
                nombre_personnes=(
                    ligne["nombre_personnes"]
                ),
                prime_nette_par_personne=(
                    ligne[
                        "prime_nette_par_personne"
                    ]
                ),
                prime_nette=(
                    prime_nette_college
                ),
                accessoire=(
                    accessoire_college
                ),
                taxe=(
                    resultat_taxe_college["taxe"]
                ),
                prime_totale=(
                    resultat_taxe_college["prime_ttc"]
                ),
            )

            db.add(ligne_avenant)

        for mouvement in mouvements:
            mouvement.avenant_id = (
                avenant.avenant_id
            )

        db.commit()
        db.refresh(avenant)

        lignes_creees = (
            db.query(LigneAvenant)
            .filter(
                LigneAvenant.avenant_id
                == avenant.avenant_id
            )
            .order_by(
                LigneAvenant.ligne_avenant_id
            )
            .all()
        )

        return {
            "message": (
                "Avenant d'incorporation "
                "créé avec succès."
            ),
            "avenant": {
                "id": avenant.avenant_id,
                "numero_avenant": (
                    avenant.numero_avenant
                ),
                "type_avenant": (
                    avenant.type_avenant
                ),
                "contrat_id": avenant.contrat_id,
                "periode_debut": (
                    avenant.periode_debut
                ),
                "periode_fin": (
                    avenant.periode_fin
                ),
                "date_effet": avenant.date_effet,
                "statut": avenant.statut,
                "prime_nette": float(
                    avenant.prime_nette
                ),
                "accessoire": float(
                    avenant.accessoire
                ),
                "taxe": float(
                    avenant.taxe
                ),
                "prime_totale": float(
                    avenant.prime_totale
                ),
            },
            "souscripteur": {
                "id": souscripteur.souscripteur_id,
                "raison_sociale": (
                    souscripteur.raison_sociale
                ),
                "type_souscripteur": (
                    souscripteur.type_souscripteur
                ),
            },
            "lignes": [
                {
                    "id": ligne.ligne_avenant_id,
                    "college_id": ligne.college_id,
                    "nombre_personnes": (
                        ligne.nombre_personnes
                    ),
                    "prime_nette_par_personne": (
                        float(
                            ligne.prime_nette_par_personne
                        )
                    ),
                    "prime_nette": float(
                        ligne.prime_nette
                    ),
                    "accessoire": float(
                        ligne.accessoire
                    ),
                    "taxe": float(
                        ligne.taxe
                    ),
                    "prime_totale": float(
                        ligne.prime_totale
                    ),
                }
                for ligne in lignes_creees
            ],
            "mouvements": [
                {
                    "id": mouvement.mouvement_id,
                    "assure_id": mouvement.assure_id,
                    "avenant_id": mouvement.avenant_id,
                }
                for mouvement in mouvements
            ],
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Erreur lors de la création "
                "de l'avenant : "
                f"{str(exc)}"
            ),
        )


# ============================================================
# PREVIEW RETRAIT
# ============================================================

@app.post("/api/avenants/retrait/preview")
def preview_avenant_retrait(
    request: RetraitAvenantRequest,
    db: Session = Depends(get_db),
):
    contrat = get_contrat_or_404(
        request.contrat_id,
        db,
    )

    valider_periode_avenant(
        contrat,
        request.periode_debut,
        request.periode_fin,
    )

    mouvements = charger_mouvements(
        request.mouvement_ids,
        db,
    )

    valider_mouvements_avenant(
        mouvements=mouvements,
        contrat_id=request.contrat_id,
        type_mouvement="RETRAIT",
        periode_debut=request.periode_debut,
        periode_fin=request.periode_fin,
        verifier_avenant=True,
    )

    souscripteur = get_souscripteur_or_404(
        contrat.souscripteur_id,
        db,
    )

    lignes_par_college = construire_lignes_mouvements(
        mouvements,
        contrat,
        db,
    )

    totaux = calculer_totaux_avenant(
        lignes_par_college,
        contrat,
        souscripteur,
    )

    resultat_taxe = totaux["resultat_taxe"]

    return {
        "type_avenant": "AVENANT_RETRAIT",
        "mode": "PREVIEW",
        "contrat": {
            "id": contrat.contrat_id,
            "numero_police": contrat.numero_police,
            "date_effet": contrat.date_effet,
            "date_fin": contrat.date_fin,
        },
        "souscripteur": {
            "id": souscripteur.souscripteur_id,
            "code_souscripteur": (
                souscripteur.code_souscripteur
            ),
            "raison_sociale": (
                souscripteur.raison_sociale
            ),
            "type_souscripteur": (
                souscripteur.type_souscripteur
            ),
        },
        "periode": {
            "debut": request.periode_debut,
            "fin": request.periode_fin,
        },
        "nombre_mouvements": len(mouvements),
        "colleges": colleges_resultat(
            lignes_par_college
        ),
        "totaux": {
            "prime_nette_totale": (
                totaux["prime_nette_totale"]
            ),
            "accessoire_taux": float(
                contrat.accessoire_taux or 0
            ),
            "accessoire": totaux["accessoire"],
            "base_taxable": (
                resultat_taxe["base_taxable"]
            ),
            "taxe_taux": (
                resultat_taxe["taux_taxe"]
            ),
            "taxe": resultat_taxe["taxe"],
            "prime_ttc": resultat_taxe["prime_ttc"],
        },
        "commentaire": request.commentaire,
    }


# ============================================================
# CREATION AVENANT RETRAIT
# ============================================================

@app.post("/api/avenants/retrait")
def creer_avenant_retrait(
    request: RetraitAvenantRequest,
    db: Session = Depends(get_db),
):
    try:

        contrat = get_contrat_or_404(
            request.contrat_id,
            db,
        )

        valider_periode_avenant(
            contrat,
            request.periode_debut,
            request.periode_fin,
        )

        mouvements = charger_mouvements(
            request.mouvement_ids,
            db,
        )

        valider_mouvements_avenant(
            mouvements=mouvements,
            contrat_id=request.contrat_id,
            type_mouvement="RETRAIT",
            periode_debut=request.periode_debut,
            periode_fin=request.periode_fin,
            verifier_avenant=True,
        )

        souscripteur = get_souscripteur_or_404(
            contrat.souscripteur_id,
            db,
        )

        lignes_par_college = (
            construire_lignes_mouvements(
                mouvements,
                contrat,
                db,
            )
        )

        totaux = calculer_totaux_avenant(
            lignes_par_college,
            contrat,
            souscripteur,
        )

        resultat_taxe = totaux["resultat_taxe"]

        numero = obtenir_nouveau_numero_avenant(
            request.contrat_id,
            db,
        )

        date_effet = min(
            mouvement.date_mouvement
            for mouvement in mouvements
        )

        avenant = Avenant(
            contrat_id=request.contrat_id,
            numero_avenant=numero,
            type_avenant="AVENANT_RETRAIT",
            periode_debut=request.periode_debut,
            periode_fin=request.periode_fin,
            date_effet=date_effet,
            prime_nette=(
                totaux["prime_nette_totale"]
            ),
            accessoire=totaux["accessoire"],
            taxe=resultat_taxe["taxe"],
            prime_totale=resultat_taxe["prime_ttc"],
            statut="VALIDE",
            commentaire=request.commentaire,
        )

        db.add(avenant)
        db.flush()

        for ligne in sorted(
            lignes_par_college.values(),
            key=lambda item: item["numero_college"],
        ):

            prime_nette_college = (
                ligne["prime_nette"]
            )

            accessoire_college = (
                abs(prime_nette_college)
                * float(
                    contrat.accessoire_taux or 0
                )
            )

            resultat_taxe_college = calculer_taxe(
                prime_nette_totale=(
                    prime_nette_college
                ),
                accessoire=accessoire_college,
                type_souscripteur=(
                    souscripteur.type_souscripteur
                ),
            )

            ligne_avenant = LigneAvenant(
                avenant_id=avenant.avenant_id,
                college_id=ligne["college_id"],
                nombre_personnes=(
                    ligne["nombre_personnes"]
                ),
                prime_nette_par_personne=(
                    ligne[
                        "prime_nette_par_personne"
                    ]
                ),
                prime_nette=(
                    prime_nette_college
                ),
                accessoire=(
                    accessoire_college
                ),
                taxe=(
                    resultat_taxe_college["taxe"]
                ),
                prime_totale=(
                    resultat_taxe_college["prime_ttc"]
                ),
            )

            db.add(ligne_avenant)

        for mouvement in mouvements:
            mouvement.avenant_id = (
                avenant.avenant_id
            )

        db.commit()
        db.refresh(avenant)

        lignes_creees = (
            db.query(LigneAvenant)
            .filter(
                LigneAvenant.avenant_id
                == avenant.avenant_id
            )
            .order_by(
                LigneAvenant.ligne_avenant_id
            )
            .all()
        )

        return {
            "message": (
                "Avenant de retrait "
                "créé avec succès."
            ),
            "avenant": {
                "id": avenant.avenant_id,
                "numero_avenant": (
                    avenant.numero_avenant
                ),
                "type_avenant": (
                    avenant.type_avenant
                ),
                "contrat_id": avenant.contrat_id,
                "periode_debut": (
                    avenant.periode_debut
                ),
                "periode_fin": (
                    avenant.periode_fin
                ),
                "date_effet": avenant.date_effet,
                "statut": avenant.statut,
                "prime_nette": float(
                    avenant.prime_nette
                ),
                "accessoire": float(
                    avenant.accessoire
                ),
                "taxe": float(
                    avenant.taxe
                ),
                "prime_totale": float(
                    avenant.prime_totale
                ),
            },
            "souscripteur": {
                "id": souscripteur.souscripteur_id,
                "raison_sociale": (
                    souscripteur.raison_sociale
                ),
                "type_souscripteur": (
                    souscripteur.type_souscripteur
                ),
            },
            "lignes": [
                {
                    "id": ligne.ligne_avenant_id,
                    "college_id": ligne.college_id,
                    "nombre_personnes": (
                        ligne.nombre_personnes
                    ),
                    "prime_nette_par_personne": (
                        float(
                            ligne.prime_nette_par_personne
                        )
                    ),
                    "prime_nette": float(
                        ligne.prime_nette
                    ),
                    "accessoire": float(
                        ligne.accessoire
                    ),
                    "taxe": float(
                        ligne.taxe
                    ),
                    "prime_totale": float(
                        ligne.prime_totale
                    ),
                }
                for ligne in lignes_creees
            ],
            "mouvements": [
                {
                    "id": mouvement.mouvement_id,
                    "assure_id": mouvement.assure_id,
                    "avenant_id": mouvement.avenant_id,
                }
                for mouvement in mouvements
            ],
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Erreur lors de la création "
                "de l'avenant de retrait : "
                f"{str(exc)}"
            ),
        )
