from datetime import date


def calculer_nombre_mois(
    date_debut: date,
    date_fin: date
) -> int:
    """
    Calcule le nombre de mois entre deux dates.
    Le mois de début et le mois de fin sont inclus.
    """

    if date_debut > date_fin:
        return 0

    return (
        (date_fin.year - date_debut.year) * 12
        + (date_fin.month - date_debut.month)
        + 1
    )


def calculer_prime_incorporation(
    prime_annuelle: float,
    date_effet: date,
    date_fin_contrat: date
) -> dict:
    """
    Calcul de la prime d'une incorporation.

    Le mois de la date d'effet est entièrement dû.
    """

    nombre_mois = calculer_nombre_mois(
        date_effet,
        date_fin_contrat
    )

    prime_mensuelle = prime_annuelle / 12
    montant = prime_mensuelle * nombre_mois

    return {
        "type_mouvement": "INCORPORATION",
        "nombre_mois": nombre_mois,
        "prime_annuelle": prime_annuelle,
        "prime_mensuelle": prime_mensuelle,
        "montant": montant
    }


def calculer_ristourne_retrait(
    prime_annuelle: float,
    date_retrait: date,
    date_fin_contrat: date
) -> dict:
    """
    Calcul de la ristourne lors d'un retrait.

    Le mois du retrait est dû.
    La ristourne commence donc le mois suivant.
    """

    if (
        date_retrait.year == date_fin_contrat.year
        and date_retrait.month == date_fin_contrat.month
    ):
        nombre_mois = 0
    else:
        if date_retrait.month == 12:
            date_debut_ristourne = date(
                date_retrait.year + 1,
                1,
                1
            )
        else:
            date_debut_ristourne = date(
                date_retrait.year,
                date_retrait.month + 1,
                1
            )

        nombre_mois = calculer_nombre_mois(
            date_debut_ristourne,
            date_fin_contrat
        )

    prime_mensuelle = prime_annuelle / 12
    montant_ristourne = prime_mensuelle * nombre_mois

    return {
        "type_mouvement": "RETRAIT",
        "nombre_mois_ristourne": nombre_mois,
        "prime_annuelle": prime_annuelle,
        "prime_mensuelle": prime_mensuelle,
        "montant_ristourne": montant_ristourne
    }
def calculer_taxe(
    prime_nette_totale: float,
    accessoire: float,
    type_souscripteur: str
) -> dict:
    """
    Calcule la taxe selon le type de souscripteur.

    ENTREPRISE  -> 3 %
    PARTICULIER -> 8 %

    Base taxable = prime nette totale + accessoire
    """

    if type_souscripteur == "ENTREPRISE":
        taux_taxe = 0.03

    elif type_souscripteur == "PARTICULIER":
        taux_taxe = 0.08

    else:
        raise ValueError(
            "Type de souscripteur invalide. "
            "Valeurs autorisées : ENTREPRISE ou PARTICULIER."
        )

    base_taxable = prime_nette_totale + accessoire
    taxe = base_taxable * taux_taxe
    prime_ttc = base_taxable + taxe

    return {
        "type_souscripteur": type_souscripteur,
        "base_taxable": base_taxable,
        "taux_taxe": taux_taxe,
        "taxe": taxe,
        "prime_ttc": prime_ttc,
    }
def calculer_taxe(
    prime_nette_totale: float,
    accessoire: float,
    type_souscripteur: str
) -> dict:
    """
    Calcul de la taxe selon le type de souscripteur.

    Base taxable = prime nette totale + accessoire

    ENTREPRISE  -> 3 %
    PARTICULIER -> 8 %
    """

    if type_souscripteur == "ENTREPRISE":
        taux_taxe = 0.03
    elif type_souscripteur == "PARTICULIER":
        taux_taxe = 0.08
    else:
        raise ValueError(
            "Type de souscripteur invalide. "
            "Valeurs autorisées : ENTREPRISE ou PARTICULIER."
        )

    base_taxable = prime_nette_totale + accessoire
    taxe = base_taxable * taux_taxe
    prime_ttc = base_taxable + taxe

    return {
        "type_souscripteur": type_souscripteur,
        "base_taxable": base_taxable,
        "taux_taxe": taux_taxe,
        "taxe": taxe,
        "prime_ttc": prime_ttc,
    }