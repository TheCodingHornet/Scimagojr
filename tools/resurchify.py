# -*- coding: utf-8 -*-
#
# File Name:       resurchify.py
# Creation Date:   23/06/2023
# Version:         0.0.1
# Author:          Simon STEPHAN <simon.stephan@u-bourgogne.fr>
#
# Copyright (c) 2023,
# All rights reserved.
#

import requests
from bs4 import BeautifulSoup
import sqlite3

import settings


def get_impact_score(journal_title):
    # Formater l'URL
    url = f"https://www.resurchify.com/find/?query={journal_title}#search_results"

    # Récupérer le HTML de la page
    response = requests.get(url)
    response.raise_for_status()  # S'assurer que la requête a réussi

    # Analyser le HTML avec BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    try:
        # Trouver le premier résultat
        result = soup.find(class_='w3-white w3-container w3-card-4 w3-hover-light-gray')

        # Extraire le score d'impact
        impact_score_tag = result.find(string=lambda text: text and "Impact Score" in text)
        impact_score_str = impact_score_tag.split(":")[1].strip()
        impact_score = float(impact_score_str)
    except:
        impact_score = None

    return impact_score


def update_impact_score(journal_id, journal_name, impact_factor):
    # Connecter à la base de données
    conn = sqlite3.connect(settings.database)  # Remplacer par le chemin de votre base de données

    # Créer un curseur
    c = conn.cursor()

    # Mettre à jour le score d'impact pour le journal
    print(journal_name + " -> " + str(impact_factor))
    # Not the real impact factor, but the impact score
    # c.execute("UPDATE journaux SET impact_factor = ? WHERE id = ?", (impact_factor, journal_id))

    # Committer les changements et fermer la connexion
    conn.commit()
    conn.close()


# Connect to your database
conn = sqlite3.connect(settings.database)
cursor = conn.cursor()
cursor.execute("SELECT id, title FROM journaux")
journal_names = cursor.fetchall()
conn.close()

for journal in journal_names:
    impact_factor = get_impact_score(journal[1])

    if impact_factor is not None:
        update_impact_score(journal[0], journal[1], impact_factor)
