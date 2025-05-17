# questions_db.py
import random

# Définir un ordre pour les niveaux de difficulté, utile pour l'affichage et le tri
DIFFICULTY_LEVELS_ORDERED = ["Facile", "Moyen", "Difficile"]

# Structure de données mise à jour : chaque question a maintenant une clé 'difficulty'.
QUESTIONS_DATABASE_BY_CATEGORY = {
    "Algorithmes et Structures de Données": [
        {
            "id": "ASD001",
            "text": "Expliquez la notation Big O (Grand O) en termes simples. Pourquoi est-elle importante dans l'analyse des algorithmes ?",
            "difficulty": "Moyen"
        },
        {
            "id": "ASD002",
            "text": "Quelle est la différence principale entre une liste (array/list) et une liste chaînée (linked list) en termes d'opérations (accès, insertion, suppression) et d'utilisation mémoire ?",
            "difficulty": "Facile"
        },
        {
            "id": "ASD003",
            "text": "Décrivez l'algorithme de tri à bulles (Bubble Sort). Quelle est sa complexité temporelle dans le meilleur, le pire et le cas moyen ?",
            "difficulty": "Facile"
        },
        {
            "id": "ASD004",
            "text": "Qu'est-ce qu'une pile (stack) et une file (queue) ? Donnez un exemple d'utilisation pour chacune.",
            "difficulty": "Facile"
        },
        {
            "id": "ASD005",
            "text": "Expliquez le concept d'arbre binaire de recherche (BST). Quelles sont ses propriétés et comment effectuer une recherche ?",
            "difficulty": "Moyen"
        },
        {
            "id": "ASD006",
            "text": "Décrivez l'algorithme de Dijkstra pour trouver le chemin le plus court dans un graphe pondéré. Quelle est sa complexité typique avec un min-heap ?",
            "difficulty": "Difficile"
        }
    ],
    "System Design (Concepts de base)": [
        {
            "id": "SYS001",
            "text": "Qu'est-ce qu'un load balancer et quel est son rôle principal dans une architecture système ?",
            "difficulty": "Facile"
        },
        {
            "id": "SYS002",
            "text": "Expliquez la différence entre la scalabilité verticale (scaling up) et la scalabilité horizontale (scaling out).",
            "difficulty": "Facile"
        },
        {
            "id": "SYS003",
            "text": "Qu'est-ce qu'une base de données SQL par rapport à une base de données NoSQL ? Donnez un cas d'usage pour chacune.",
            "difficulty": "Moyen"
        },
        {
            "id": "SYS004",
            "text": "Qu'est-ce qu'une API RESTful ? Quelles sont certaines des caractéristiques communes d'une API RESTful ?",
            "difficulty": "Moyen"
        },
        {
            "id": "SYS005",
            "text": "Décrivez le concept de Content Delivery Network (CDN) et ses avantages.",
            "difficulty": "Moyen"
        },
        {
            "id": "SYS006",
            "text": "Expliquez le théorème CAP (Consistency, Availability, Partition tolerance) et son importance dans les systèmes distribués.",
            "difficulty": "Difficile"
        }
    ],
    "Python (Concepts Généraux)": [
        {
            "id": "PYT001",
            "text": "Expliquez la différence entre les variables mutables et immutables en Python. Donnez des exemples.",
            "difficulty": "Facile"
        },
        {
            "id": "PYT002",
            "text": "Qu'est-ce qu'un décorateur en Python et à quoi sert-il ? Fournissez un exemple simple.",
            "difficulty": "Moyen"
        },
        {
            "id": "PYT003",
            "text": "Comment Python gère-t-il la mémoire (par exemple, garbage collection) ?",
            "difficulty": "Moyen"
        },
        {
            "id": "PYT004",
            "text": "Qu'est-ce que le Global Interpreter Lock (GIL) en Python et quel impact a-t-il sur le multithreading ?",
            "difficulty": "Difficile"
        }
    ]
}

def get_categories() -> list[str]:
    """
    Retourne la liste des noms des catégories disponibles, triées alphabétiquement.
    """
    return sorted(list(QUESTIONS_DATABASE_BY_CATEGORY.keys()))

def get_available_difficulties(category_name: str) -> list[str]:
    """
    Retourne la liste des niveaux de difficulté uniques disponibles pour une catégorie donnée,
    triée selon DIFFICULTY_LEVELS_ORDERED.
    Retourne une liste vide si la catégorie n'existe pas ou n'a pas de questions.
    """
    questions_in_category = QUESTIONS_DATABASE_BY_CATEGORY.get(category_name, [])
    if not questions_in_category:
        return []

    # Utiliser un set pour obtenir les difficultés uniques
    unique_difficulties = set(q['difficulty'] for q in questions_in_category if 'difficulty' in q)

    # Trier les difficultés selon l'ordre prédéfini
    # Garder uniquement celles présentes dans la catégorie et dans l'ordre défini
    sorted_present_difficulties = [d for d in DIFFICULTY_LEVELS_ORDERED if d in unique_difficulties]

    return sorted_present_difficulties

def get_questions(category_name: str, difficulty_level: str) -> list[dict]:
    """
    Retourne la liste des questions correspondant à la catégorie ET à la difficulté spécifiées.
    Retourne une liste vide si la catégorie n'existe pas ou si aucune question
    ne correspond aux critères.
    """
    questions_in_category = QUESTIONS_DATABASE_BY_CATEGORY.get(category_name, [])
    if not questions_in_category:
        return []

    filtered_questions = [
        q for q in questions_in_category
        if q.get('difficulty') == difficulty_level # Utiliser .get() pour éviter KeyError si 'difficulty' manque
    ]
    return filtered_questions

def get_random_question(category_name: str, difficulty_level: str) -> dict | None:
    """
    Retourne une question aléatoire de la catégorie ET de la difficulté spécifiées.
    Retourne None si aucune question ne correspond aux critères.
    """
    questions_for_criteria = get_questions(category_name, difficulty_level)
    if not questions_for_criteria:
        return None
    return random.choice(questions_for_criteria)

# Code de test optionnel
if __name__ == '__main__':
    print("--- Test de la base de questions multi-catégories et multi-difficultés ---")

    print("\n--- Catégories Disponibles ---")
    categories = get_categories()
    print(categories)

    if categories:
        print("\n--- Difficultés par Catégorie ---")
        for category in categories:
            difficulties = get_available_difficulties(category)
            print(f"Catégorie '{category}': Difficultés disponibles: {difficulties}")

            if difficulties:
                print(f"  --- Questions pour '{category}' ---")
                for difficulty in difficulties:
                    questions = get_questions(category, difficulty)
                    print(f"    Difficulté '{difficulty}' ({len(questions)} questions):")
                    if questions:
                        # Afficher la première question de cette difficulté pour le test
                        print(f"      Ex: ID: {questions[0]['id']}, Text: {questions[0]['text'][:50]}...")
                    else:
                        print("      Aucune question pour cette difficulté.")

        print("\n--- Test de Questions Aléatoires (Catégorie + Difficulté) ---")
        # Tester avec une catégorie et une difficulté spécifiques
        test_cat = "Algorithmes et Structures de Données"
        test_diff = "Moyen"
        print(f"\nQuestion aléatoire pour '{test_cat}' - '{test_diff}':")
        random_q = get_random_question(test_cat, test_diff)
        if random_q:
            print(f"  ID: {random_q['id']}, Question: {random_q['text']}")
        else:
            print(f"  Impossible d'obtenir une question aléatoire pour '{test_cat}' - '{test_diff}'.")

        # Tester avec une combinaison qui pourrait ne pas avoir de questions
        test_cat_no_hard = "Python (Concepts Généraux)" # Vérifier si on a des questions "Facile"
        test_diff_easy = "Facile"
        print(f"\nQuestion aléatoire pour '{test_cat_no_hard}' - '{test_diff_easy}':")
        random_q_py_easy = get_random_question(test_cat_no_hard, test_diff_easy)
        if random_q_py_easy:
            print(f"  ID: {random_q_py_easy['id']}, Question: {random_q_py_easy['text']}")
        else:
            print(f"  Aucune question 'Facile' trouvée pour '{test_cat_no_hard}'.")


    # Vérification des IDs uniques globalement (toujours une bonne pratique)
    all_ids = []
    for cat_questions in QUESTIONS_DATABASE_BY_CATEGORY.values():
        for question in cat_questions:
            all_ids.append(question['id'])

    if len(all_ids) != len(set(all_ids)):
        print("\nAttention : Les IDs des questions ne sont pas tous uniques globalement !")
    else:
        print("\nLes IDs des questions sont bien uniques globalement.")