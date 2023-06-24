# -*- coding: utf-8 -*-
#
# File Name:       impactfactor.py
# Creation Date:   23/06/2023
# Version:         0.0.1
# Author:          Simon STEPHAN <simon.stephan@u-bourgogne.fr>
#
# Copyright (c) 2023,
# All rights reserved.
#

import subprocess
import json
import sqlite3
from sqlite3 import Error

import settings

# Connect to your database
conn = sqlite3.connect(settings.database)
cursor = conn.cursor()
cursor.execute("SELECT id, title FROM journaux")
journal_names = cursor.fetchall()
conn.close()


def get_impact_factor(journal_name):
    command = ['impact_factor', 'search', journal_name]
    result = subprocess.run(command, capture_output=True, text=True)

    # Replace single quotes with double quotes
    text = result.stdout.replace("'", '"')
    result_json = json.loads(text)

    if result_json:
        if 'journal' in result_json[0] and result_json[0]['journal'].lower() == journal_name.lower():
            return result_json[0]['factor']
    return None


def update_impact_factor(journal, impact_factor):
    try:
        # Connect to your sqlite database
        conn = sqlite3.connect(settings.database)
        cursor = conn.cursor()

        journal_id = journal[0]
        journal_name = journal[1]

        # Update the impact factor in the database
        cursor.execute("""UPDATE journaux SET impact_factor = ? WHERE id = ?""", (impact_factor, journal_id))
        conn.commit()

        print(f"Updated impact factor for {journal_name} to {impact_factor}")

    except Error as e:
        print(e)

    finally:
        if conn:
            conn.close()


for journal in journal_names:
    print(journal[1])
    impact_factor = get_impact_factor(journal[1])
    if impact_factor is not None:
        update_impact_factor(journal, impact_factor)
