"""
Script de test avec une erreur volontaire
Pour tester auto_debug
"""

def calculer_moyenne(notes):
    """Calcule la moyenne d'une liste de notes"""
    total = sum(notes)
    moyenne = total / len(note)  # BUG : 'note' au lieu de 'notes'
    return moyenne


def afficher_resultats(nom, notes):
    """Affiche les résultats d'un étudiant"""
    moyenne = calculer_moyenne(notes)
    print(f"Étudiant : {nom}")
    print(f"Notes : {notes}")
    print(f"Moyenne : {moyenne:.2f}")
    
    if moyenne >= 10:
        print("✅ Admis")
    else:
        print("❌ Recalé")


# Programme principal
if __name__ == "__main__":
    etudiants = {
        "Alice": [15, 12, 18, 14],
        "Bob": [8, 9, 7, 10],
        "Charlie": [16, 17, 15, 18]
    }
    
    print("=== Résultats des étudiants ===\n")
    
    for nom, notes in etudiants.items():
        afficher_resultats(nom, notes)
        print()