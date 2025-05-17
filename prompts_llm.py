# prompts_llm.py

# ... (FEEDBACK_PROMPT_TEMPLATE et format_user_prompt pour le feedback restent inchangés)
# ... (supposons que le code précédent est ici)

FEEDBACK_PROMPT_TEMPLATE = """
Vous êtes un évaluateur expert et bienveillant pour des entretiens techniques.
La question posée au candidat appartient à la catégorie : **"{category_name}"**.

Votre mission est d'analyser la réponse d'un candidat à la question technique et de fournir un feedback constructif pour l'aider à s'améliorer.

La question posée au candidat était :
QUESTION : "{question_text}"

La réponse fournie par le candidat est :
RÉPONSE CANDIDAT : "{user_answer_text}"

Veuillez évaluer la réponse du candidat en vous concentrant sur les aspects suivants, en tenant compte de la catégorie de la question :

**Partie 1 : Évaluation Technique et Clarté**

1.  **Clarté** :
    *   La réponse est-elle bien structurée et facile à comprendre ?
    *   Le langage utilisé est-il précis et technique lorsque c'est approprié pour la catégorie "{category_name}" ?
    *   Les explications sont-elles logiques et directes ?

2.  **Complétude et Exactitude Technique (spécifique à "{category_name}")** :
    *   La réponse aborde-t-elle les points essentiels et les concepts clés relatifs à la question dans le contexte de "{category_name}" ?
    *   Y a-t-il des omissions importantes ou des erreurs conceptuelles ? (Par exemple, pour "Algorithmes", la complexité est souvent clé. Pour "System Design", les compromis et la scalabilité sont importants).
    *   Si des exemples sont pertinents, sont-ils présents et corrects ?

**Partie 2 : Analyse de la Pensée Structurée / "Penser à voix haute" (déduit du texte)**

Évaluez si la réponse textuelle du candidat reflète une approche structurée de la résolution de problème, similaire à ce qu'on attendrait d'une personne qui "pense à voix haute" :

1.  **Décomposition du Problème :**
    *   Le candidat a-t-il tenté d'identifier les sous-problèmes, les contraintes, ou les étapes clés avant de plonger dans la solution ?
    *   La réponse montre-t-elle une compréhension des différentes parties du problème (particulièrement pertinent pour les questions d'algorithmes complexes ou de system design) ?

2.  **Exploration d'Options (si applicable à la question) :**
    *   Le candidat a-t-il mentionné ou semblé considérer brièvement des approches alternatives, des structures de données différentes, ou des compromis (trade-offs) avant de se concentrer sur une voie spécifique ?
    *   Même si une seule solution est présentée, y a-t-il des indices qu'une réflexion sur d'autres options a eu lieu ?

3.  **Justification des Choix :**
    *   Les décisions clés, les étapes de la solution, ou le choix d'une structure de données/algorithme sont-ils expliqués ou justifiés, même brièvement ?
    *   Le candidat explique-t-il *pourquoi* il fait certains choix ?

4.  **Clarté de la Progression Logique :**
    *   La réponse suit-elle un fil logique et compréhensible, allant par exemple des hypothèses/contraintes à la solution, ou d'une vue d'ensemble aux détails ?
    *   Est-il facile de suivre le raisonnement du candidat à travers son texte ?

**Instructions pour votre feedback :**
*   Rédigez votre feedback en **Markdown**.
*   Structurez clairement votre feedback avec les titres principaux suivants : `### Évaluation Technique et Clarté` et `### Analyse de la Pensée Structurée / "Penser à voix haute"`.
*   Sous `### Évaluation Technique et Clarté`, utilisez les sous-titres : `#### Clarté` et `#### Complétude et Exactitude Technique`.
*   Sous `### Analyse de la Pensée Structurée / "Penser à voix haute"`, utilisez les sous-titres : `#### Décomposition du Problème`, `#### Exploration d'Options`, `#### Justification des Choix`, et `#### Clarté de la Progression Logique`.
*   Sous chaque sous-titre, utilisez des listes à puces (`*`) pour des commentaires spécifiques, des observations et des suggestions d'amélioration.
*   Soyez spécifique dans vos commentaires. Au lieu de dire "pas assez décomposé", expliquez *ce qui aurait pu être décomposé* ou *comment*.
*   **Ne donnez PAS la solution complète.** Votre rôle est de guider. Posez des questions suggestives, indiquez les domaines où des approfondissements sont nécessaires.
*   Pour la section "Penser à voix haute", reconnaissez que vous évaluez cela à partir d'un texte et que ce n'est qu'une inférence. Le but est d'encourager l'utilisateur à structurer ses futures réponses (orales ou écrites) de cette manière.
*   Adoptez un ton encourageant et constructif.
*   Visez une longueur de feedback concise mais utile.

Votre feedback (en Markdown) :
"""

def format_user_prompt(question_text: str, user_answer_text: str, category_name: str) -> str:
    """
    Formate le prompt complet à envoyer au LLM pour le feedback principal.
    """
    if not all([question_text, user_answer_text, category_name]):
        return "Erreur: Des informations (question, réponse ou catégorie) sont manquantes pour formater le prompt."
    return FEEDBACK_PROMPT_TEMPLATE.format(
        category_name=category_name,
        question_text=question_text,
        user_answer_text=user_answer_text
    )


# --- Nouveau Prompt pour les Questions de Suivi ---

FOLLOW_UP_QUESTIONS_PROMPT_TEMPLATE = """
Vous êtes un assistant d'entretien technique expert. Votre rôle est de générer des questions de suivi pertinentes basées sur la discussion précédente.

Contexte de la discussion :
Catégorie de la question : **"{category_name}"**

Question Principale posée au candidat :
"{main_question_text}"

Réponse du candidat à la question principale :
"{user_answer_text}"

Feedback généré pour la réponse du candidat (ce feedback peut vous aider à identifier les points à creuser) :
"{feedback_text}"

Votre tâche :
Générez **1 ou 2 questions de suivi concises et pertinentes**. Ces questions devraient :
1.  Être directement liées à la question principale, à la réponse du candidat, ou aux points soulevés dans le feedback.
2.  Viser à :
    *   Clarifier un point ambigu ou incomplet dans la réponse.
    *   Explorer une alternative non mentionnée ou brièvement évoquée.
    *   Tester une compréhension plus profonde d'un concept utilisé.
    *   Aborder une omission significative identifiée dans le feedback.
    *   Demander des exemples ou des cas limites.
3.  Être formulées comme des questions claires et directes.
4.  NE PAS introduire un sujet complètement nouveau et non lié.
5.  NE PAS être des questions auxquelles le candidat a déjà répondu de manière exhaustive.

Format de sortie :
Retournez chaque question de suivi sur une nouvelle ligne.
Si vous estimez qu'aucune question de suivi pertinente n'est nécessaire ou ne peut être formulée, retournez la chaîne de caractères exacte : "AUCUNE QUESTION DE SUIVI".

Exemples de questions de suivi possibles (NE PAS les utiliser directement) :
*   "Pourriez-vous expliquer pourquoi vous avez choisi X plutôt que Y dans ce scénario ?"
*   "Comment votre solution gérerait-elle le cas où [condition spécifique/edge case] ?"
*   "Vous avez mentionné [concept]. Pouvez-vous nous en dire plus sur son impact ici ?"

Vos questions de suivi :
"""

def format_follow_up_prompt(main_question_text: str, user_answer_text: str, feedback_text: str, category_name: str) -> str:
    """
    Formate le prompt pour la génération de questions de suivi.

    Args:
        main_question_text: La question d'entretien initiale.
        user_answer_text: La réponse de l'utilisateur à la question initiale.
        feedback_text: Le feedback généré par l'IA sur la réponse de l'utilisateur.
        category_name: La catégorie de la question initiale.

    Returns:
        Le prompt formaté pour le LLM.
    """
    if not all([main_question_text, user_answer_text, feedback_text, category_name]):
        return "Erreur: Des informations contextuelles sont manquantes pour générer les questions de suivi."

    return FOLLOW_UP_QUESTIONS_PROMPT_TEMPLATE.format(
        category_name=category_name,
        main_question_text=main_question_text,
        user_answer_text=user_answer_text,
        feedback_text=feedback_text # Fournir le feedback comme contexte est crucial
    )


# Exemple d'utilisation pour les questions de suivi
if __name__ == '__main__':
    # ... (les tests pour format_user_prompt peuvent rester)

    print("\n\n--- TEST DU PROMPT POUR QUESTIONS DE SUIVI ---")
    mq = "Expliquez la différence entre scalabilité verticale et horizontale."
    ua = "Verticale c'est plus de puissance sur une machine, horizontale c'est plus de machines. Horizontale est mieux pour les gros trucs."
    fb = """
### Évaluation Technique et Clarté
#### Clarté
*   Votre distinction de base est correcte.
#### Complétude et Exactitude Technique
*   Bien que "mieux pour les gros trucs" soit intuitivement vrai, pourriez-vous élaborer sur les avantages et inconvénients spécifiques de chaque approche ? Par exemple, en termes de coût, de limites, de complexité de gestion ?
*   Y a-t-il des scénarios où la scalabilité verticale pourrait être préférable ?
### Analyse de la Pensée Structurée / "Penser à voix haute"
#### ... (feedback sur la pensée structurée) ...
    """
    cat = "System Design (Concepts de base)"

    follow_up_prompt = format_follow_up_prompt(mq, ua, fb, cat)
    print(f"--- PROMPT FORMATÉ POUR QUESTIONS DE SUIVI (Catégorie: {cat}) ---")
    print(follow_up_prompt)

    print("\n--- EXEMPLE DE SORTIE ATTENDUE DU LLM POUR QUESTIONS DE SUIVI ---")
    print("""Pourriez-vous discuter des compromis (coût, complexité, point unique de défaillance) entre la scalabilité verticale et horizontale ?
Dans quel type de système la scalabilité verticale pourrait-elle encore être une approche viable ou même préférée ?
    """)
    # Ou:
    # print("AUCUNE QUESTION DE SUIVI")