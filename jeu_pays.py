# -*- coding: utf-8 -*-
"""
NATION LEADER — Simulateur de dirigeant
Jeu textuel dans lequel le joueur incarne le dirigeant d'un pays,
avec choix du rôle, du système politique et du pays (réel ou fictif).

Lancement :  python3 jeu_pays.py
"""

import random
import sys

# ---------------------------------------------------------------------------
# Données de départ
# ---------------------------------------------------------------------------

ROLES = {
    "1": ("Roi", "M"),
    "2": ("Reine", "F"),
    "3": ("Président", "M"),
    "4": ("Présidente", "F"),
    "5": ("Premier Ministre", "M"),
    "6": ("Première Ministre", "F"),
}

SYSTEMES = {
    "1": {
        "nom": "Dictature",
        "description": "Pouvoir total, opposition interdite. La répression est efficace, "
                       "mais le monde vous regarde avec méfiance.",
        "effets": {"repression": 1.5, "popularite_min": 5, "croissance_eco": 0.8},
    },
    "2": {
        "nom": "Monarchie absolue",
        "description": "Vous décidez de tout, par droit divin. Tradition respectée, "
                       "mais le peuple compte les années.",
        "effets": {"repression": 1.2, "popularite_min": 15, "croissance_eco": 1.0},
    },
    "3": {
        "nom": "Monarchie constitutionnelle",
        "description": "Rôle symbolique renforcé d'un vrai pouvoir moral. "
                       "Difficile d'imposer des réformes audacieuses.",
        "effets": {"repression": 0.7, "popularite_min": 30, "croissance_eco": 1.1},
    },
    "4": {
        "nom": "Démocratie parlementaire",
        "description": "Le parlement vous surveille. Chaque décision doit "
                       "trouver une majorité.",
        "effets": {"repression": 0.5, "popularite_min": 35, "croissance_eco": 1.2},
    },
    "5": {
        "nom": "Régime présidentiel",
        "description": "Pouvoir exécutif fort, élection directe. "
                       "Grande liberté d'action, grandes responsabilités.",
        "effets": {"repression": 0.8, "popularite_min": 30, "croissance_eco": 1.2},
    },
    "6": {
        "nom": "Régime semi-présidentiel",
        "description": "Vous partagez le pouvoir avec un Premier ministre. "
                       "Cohabitation possible, autorité partagée.",
        "effets": {"repression": 0.7, "popularite_min": 30, "croissance_eco": 1.15},
    },
    "7": {
        "nom": "République fédérale",
        "description": "Des États fédérés avec leurs propres gouverneurs. "
                       "Décisions lentes mais pays très résilient.",
        "effets": {"repression": 0.6, "popularite_min": 30, "croissance_eco": 1.25},
    },
    "8": {
        "nom": "Régime militaire",
        "description": "L'armée vous a porté au pouvoir. Elle attend des résultats... "
                       "et beaucoup de budget.",
        "effets": {"repression": 1.6, "popularite_min": 10, "croissance_eco": 0.9},
    },
}

PAYS_REELS = [
    "France", "Japon", "Brésil", "Canada", "Allemagne", "Sénégal",
    "Inde", "Maroc", "Australie", "Mexique", "Suède", "Égypte",
    "Corée du Sud", "Argentine", "Nigéria", "Italie", "Indonésie",
]

PREFIXES_FICTIFS = ["Val", "Nor", "Ast", "Fer", "Lud", "Zen", "Kalta", "Ober",
                    "Mir", "San", "Eld", "Tor"]
SUFFIXES_FICTIFS = ["doria", "vakia", "landia", "esia", "onie", "aria",
                    "stan", "mark", "thie", "guay", "novie", "bérie"]

# ---------------------------------------------------------------------------
# Événements : (texte, [ (libellé choix, effets_dict), ... ])
# Effets : popularite, economie, armee, bonheur, stabilite
# ---------------------------------------------------------------------------

EVENEMENTS = [
    {
        "titre": "Manifestations dans les grandes villes",
        "texte": "Des centaines de milliers de personnes descendent dans la rue. "
                 "Les slogans visent directement votre gouvernement.",
        "choix": [
            ("Envoyer la police disperser la foule",
             {"popularite": -8, "stabilite": 8, "bonheur": -10, "repression_ok": True}),
            ("Répondre à leurs revendications (coût social)",
             {"popularite": 8, "economie": -10, "bonheur": 8}),
            ("Ignorer et continuer de gouverner",
             {"popularite": -5, "stabilite": -6}),
        ],
    },
    {
        "titre": "Crise économique mondiale",
        "texte": "Les marchés internationaux s'effondrent. Votre monnaie "
                 "commence à faiblir.",
        "choix": [
            ("Lancer un plan de relance massif",
             {"economie": -8, "bonheur": 9, "popularite": 5}),
            ("Adopter une politique d'austérité stricte",
             {"economie": 10, "popularite": -10, "bonheur": -8}),
            ("Fermer les frontières commerciales",
             {"economie": -4, "popularite": 3, "stabilite": -3, "bornes": (-2, 2)}),
        ],
    },
    {
        "titre": "Tensions à la frontière",
        "texte": "Un pays voisin revendique une région stratégique et "
                 "masse des troupes à la frontière.",
        "choix": [
            ("Mobiliser l'armée et verrouiller la frontière",
             {"armee": 10, "economie": -8, "stabilite": 5}),
            ("Ouvrir des négociations diplomatiques",
             {"popularite": 4, "bonheur": 5, "stabilite": 2}),
            ("Demander l'aide d'une grande puissance",
             {"economie": 5, "popularite": -7, "stabilite": 6}),
        ],
    },
    {
        "titre": "Scandale de corruption",
        "texte": "La presse révèle que plusieurs membres de votre "
                 "gouvernement ont détourné des fonds publics.",
        "choix": [
            ("Les limoger et ouvrir une enquête publique",
             {"popularite": 7, "stabilite": -4, "bonheur": 4}),
            ("Étouffer l'affaire",
             {"popularite": -12, "stabilite": 3, "repression_ok": True}),
            ("Accuser la presse de désinformation",
             {"popularite": -6, "bonheur": -4, "stabilite": 2}),
        ],
    },
    {
        "titre": "Révolution technologique",
        "texte": "Une start-up nationale invente une batterie révolutionnaire. "
                 "Le monde entier veut en acheter.",
        "choix": [
            ("Investir massivement dans le secteur",
             {"economie": 12, "armee": 3, "popularite": 5}),
            ("Nationaliser la technologie",
             {"economie": 5, "bonheur": -5, "popularite": -6}),
            ("La vendre à l'étranger pour un prix énorme",
             {"economie": 15, "popularite": -9, "armee": -2}),
        ],
    },
    {
        "titre": "Catastrophe naturelle",
        "texte": "Un séisme dévaste une région entière. Des milliers de "
                 "sans-abri attendent votre réaction.",
        "choix": [
            ("Déployer l'armée et l'aide d'urgence",
             {"armee": -3, "popularite": 9, "bonheur": 8, "economie": -5}),
            ("Demander l'aide internationale",
             {"economie": 3, "popularite": -8, "bonheur": -2}),
            ("Minimiser l'ampleur de la catastrophe",
             {"popularite": -10, "bonheur": -8, "stabilite": -5}),
        ],
    },
    {
        "titre": "Attentat terroriste",
        "texte": "Un attentat frappe la capitale. Le pays est sous le choc "
                 "et exige une réponse.",
        "choix": [
            ("Renforcer la sécurité et voter des lois d'exception",
             {"stabilite": 8, "bonheur": -5, "popularite": 3, "repression_ok": True}),
            ("Lancer une grande enquête sans mesures d'exception",
             {"stabilite": 2, "popularite": -4, "bonheur": 2}),
            ("Frapper les camps ennemis à l'étranger",
             {"armee": -5, "popularite": 8, "stabilite": -3}),
        ],
    },
    {
        "titre": "Réussite sportive historique",
        "texte": "L'équipe nationale remporte la coupe du monde. "
                 "Le pays est en fête.",
        "choix": [
            ("Organiser une parade géante",
             {"popularite": 10, "economie": -3, "bonheur": 10}),
            ("En profiter pour lancer un plan « sport et jeunesse »",
             {"economie": -5, "bonheur": 7, "popularite": 6}),
            ("Rester sobre : c'est juste du sport",
             {"popularite": -3, "economie": 2}),
        ],
    },
    {
        "titre": "La presse découvre un projet secret",
        "texte": "Un journaliste révèle l'existence d'un programme militaire "
                 "caché au parlement et au peuple.",
        "choix": [
            ("Assumer le programme publiquement",
             {"armee": 8, "popularite": -5, "stabilite": 3}),
            ("Le démanteler pour sauver votre image",
             {"armee": -8, "popularite": 6}),
            ("Faire arrêter le journaliste",
             {"popularite": -10, "stabilite": 5, "repression_ok": True}),
        ],
    },
    {
        "titre": "Grève générale",
        "texte": "Les transports, les écoles et les hôpitaux sont paralysés "
                 "par une grève illimitée.",
        "choix": [
            ("Relever les salaires de tous les fonctionnaires",
             {"economie": -9, "popularite": 8, "bonheur": 8}),
            ("Réquisitionner les grévistes",
             {"stabilite": 6, "popularite": -9, "bonheur": -6, "repression_ok": True}),
            ("Négocier un compromis lent mais solide",
             {"economie": -3, "popularite": 2, "stabilite": 2}),
        ],
    },
]

# ---------------------------------------------------------------------------
# Utilitaires d'affichage
# ---------------------------------------------------------------------------

def afficher_titre():
    print("=" * 70)
    print("            N A T I O N   L E A D E R   —   Simulateur")
    print("=" * 70)


def demander(message, validees):
    """Pose une question et redemande tant que la réponse n'est pas valide."""
    while True:
        reponse = input(message).strip()
        if reponse in validees:
            return reponse
        print(f"  >> Réponse invalide, tapez un nombre entre {min(validees)} "
              f"et {max(validees)}.")


def demander_texte(message, defaut):
    valeur = input(message).strip()
    return valeur if valeur else defaut


def vider_ligne():
    input("\n  [Entrée pour continuer]...")


# ---------------------------------------------------------------------------
# Création du pays et du personnage
# ---------------------------------------------------------------------------

def choisir_pays():
    print("\n--- CHOIX DU PAYS ---")
    print("  1. Jouer un pays réel")
    print("  2. Inventer un pays fictif")
    print("  3. Générer un nom de pays fictif au hasard")
    type_pays = demander("  Votre choix (1-3) : ", {"1", "2", "3"})

    if type_pays == "1":
        print("\n  Pays disponibles :")
        for i, pays in enumerate(PAYS_REELS, 1):
            print(f"    {i:>2}. {pays}")
        numero = demander(f"  Votre pays (1-{len(PAYS_REELS)}) : ",
                          {str(i) for i in range(1, len(PAYS_REELS) + 1)})
        return PAYS_REELS[int(numero) - 1]

    if type_pays == "2":
        return demander_texte("  Nom de votre pays fictif : ", "Nouvelle Aventure")

    nom = (random.choice(PREFIXES_FICTIFS) + random.choice(SUFFIXES_FICTIFS)).capitalize()
    print(f"\n  Le hasard a créé : {nom}")
    return nom


def choisir_role():
    print("\n--- CHOIX DU RÔLE ---")
    for cle, (nom, _) in ROLES.items():
        print(f"  {cle}. {nom}")
    cle = demander("  Votre choix (1-6) : ", set(ROLES))
    return ROLES[cle][0]


def choisir_systeme():
    print("\n--- CHOIX DU SYSTÈME POLITIQUE ---")
    for cle, sys_ in SYSTEMES.items():
        print(f"  {cle}. {sys_['nom']}")
    cle = demander("  Votre choix (1-8) : ", set(SYSTEMES))
    return SYSTEMES[cle]


# ---------------------------------------------------------------------------
# Jeu principal
# ---------------------------------------------------------------------------

class Partie:
    def __init__(self, pays, role, systeme):
        self.pays = pays
        self.role = role
        self.systeme = systeme
        self.tour = 1
        self.max_tours = 12
        self.statistiques = {
            "popularite": 55,
            "economie": 55,
            "armee": 50,
            "bonheur": 55,
            "stabilite": 60,
        }
        self.historique = []

    # -- affichage ----------------------------------------------------------
    def afficher_etat(self):
        print("\n" + "-" * 70)
        print(f"  {self.pays}  |  {self.role}  |  {self.systeme['nom']}")
        print(f"  Mandat : tour {self.tour}/{self.max_tours}")
        print("-" * 70)
        for nom, valeur in self.statistiques.items():
            valeurs = min(100, max(0, valeur))
            barre = "#" * (valeurs // 5) + "." * (20 - valeurs // 5)
            alerte = "  << ALERTE" if valeurs < 20 else ""
            print(f"  {nom.capitalize():<11} {valeurs:>3}  [{barre}]{alerte}")
        print("-" * 70)

    # -- application d'effets ----------------------------------------------
    def appliquer_effets(self, effets):
        rep = self.systeme["effets"].get("repression", 1.0)
        for nom, delta in effets.items():
            if nom in ("repression_ok", "bornes"):
                continue
            if nom in self.statistiques:
                gain = delta * rep if (nom == "stabilite"
                                       and effets.get("repression_ok")) else delta
                self.statistiques[nom] += int(round(gain))

        self.statistiques = {k: min(100, max(0, v))
                             for k, v in self.statistiques.items()}

    # -- évolution naturelle du pays ----------------------------------------
    def tour_de_paie(self):
        croissance = self.systeme["effets"]["croissance_eco"]
        self.statistiques["economie"] += random.randint(-3, 3) + int(
            croissance * 2) - 2
        self.statistiques["bonheur"] += random.randint(-3, 2)
        self.statistiques["stabilite"] += random.randint(-3, 2)
        self.statistiques = {k: min(100, max(0, v))
                             for k, v in self.statistiques.items()}

    # -- conditions de fin ---------------------------------------------------
    def verifier_fin(self):
        """Renvoie un message de fin ou None."""
        s = self.statistiques
        limite_pop = self.systeme["effets"]["popularite_min"]
        if s["popularite"] < limite_pop:
            return (f"Révolution ! Avec seulement {s['popularite']} % de popularité, "
                    f"votre soutien est tombé sous le seuil critique de votre régime. "
                    f"Une foule prend le palais : vous devez fuir {self.pays}.")
        if s["stabilite"] <= 0:
            return (f"Guerre civile ! La stabilité a atteint zéro. "
                    f"{self.pays} se fracture en plusieurs camps armés.")
        if s["economie"] <= 0:
            return (f"Faillite totale ! {self.pays} ne peut plus payer ses dettes. "
                    f"Vous êtes chassé du pouvoir par les créanciers.")
        if s["armee"] <= 0:
            return (f"Armée désintégrée ! Un coup d'État militaire renverse "
                    f"votre gouvernement cette nuit.")
        if self.tour > self.max_tours:
            return self.bilan()
        return None

    def bilan(self):
        s = self.statistiques
        score = (s["popularite"] + s["economie"] + s["armee"] +
                 s["bonheur"] + s["stabilite"]) // 5
        if score >= 75:
            verdict = "LES MANUELS D'HISTOIRE PARLERONT DE VOUS avec admiration."
        elif score >= 55:
            verdict = "Un règne SOLIDE. Ni héros, ni tyran : un vrai dirigeant."
        elif score >= 35:
            verdict = "Survie tant bien que mal... L'opposition vous attend au tournant."
        else:
            verdict = "Un bilan DÉSASTREUX. Vos souvenirs vous poursuivront."
        return (f"Fin de mandat ! Bilan de votre direction de {self.pays} :\n"
                f"  Score global : {score}/100\n  {verdict}")

    # -- boucle principale ---------------------------------------------------
    def jouer(self):
        evenements_tires = []
        while True:
            self.afficher_etat()

            if len(evenements_tires) < len(EVENEMENTS):
                evenement = random.choice([e for e in EVENEMENTS
                                           if e not in evenements_tires])
            else:
                evenement = random.choice(EVENEMENTS)
            evenements_tires.append(evenement)

            print(f"\n  === ÉVÉNEMENT : {evenement['titre']} ===")
            print(f"  {evenement['texte']}\n")
            for i, (libelle, _) in enumerate(evenement["choix"], 1):
                print(f"    {i}. {libelle}")

            effets_options = [c[1] for c in evenement["choix"]]
            numero = demander(f"  Votre décision (1-{len(effets_options)}) : ",
                              {str(i) for i in range(1, len(effets_options) + 1)})
            effets = effets_options[int(numero) - 1]

            self.appliquer_effets(effets)
            self.tour_de_paie()

            self.tour += 1
            fin = self.verifier_fin()
            if fin:
                print("\n" + "=" * 70)
                print(fin)
                print("=" * 70)
                return

            vider_ligne()


def jouer_partie():
    afficher_titre()
    print("\nVous allez devenir le dirigeant d'un pays.\n"
          "Vos décisions façonnent le destin de votre nation... et le vôtre.\n")

    pays = choisir_pays()
    role = choisir_role()
    systeme = choisir_systeme()

    print(f"\n  Vous êtes : {role} de {pays}")
    print(f"  Régime : {systeme['nom']}")
    print(f"  {systeme['description']}\n")

    partie = Partie(pays, role, systeme)
    vider_ligne()
    partie.jouer()

    recommencer = input("\nVoulez-vous rejouer ? (o/n) : ").strip().lower()
    if recommencer == "o":
        print("\n" * 2)
        jouer_partie()
    else:
        print("\nMerci d'avoir joué. Que votre règne passe à la postérité !\n")
        sys.exit(0)


if __name__ == "__main__":
    try:
        jouer_partie()
    except (KeyboardInterrupt, EOFError):
        print("\n\nPartie interrompue. À bientôt !")
