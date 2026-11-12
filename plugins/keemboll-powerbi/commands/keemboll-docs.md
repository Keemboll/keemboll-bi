---
description: Guide d'utilisation du plugin keemboll-powerbi (skills, sous-agents, script lean.py, fichiers de projet, méthode de travail, autres agents). Argument optionnel : une section.
argument-hint: "[installation | skills | exemples | projet | agents | lean | dette | methode | securite | depannage]"
---

Présente à l'utilisateur le guide ci-dessous, en français, **sans rien exécuter ni modifier**.

- Si `$ARGUMENTS` est vide : affiche la section « Vue d'ensemble », puis la table des matières des sections et la façon d'en ouvrir une (`/keemboll-docs <section>`).
- Si `$ARGUMENTS` correspond à une section (ou en est proche) : affiche uniquement cette section, en entier.
- Si `$ARGUMENTS` est une question (« comment auditer un modèle ? ») : réponds à partir de ce guide et indique la section concernée.
- Termine toujours par une ligne : « Version installée : » suivie du résultat de la commande `claude plugin list` pour `keemboll-powerbi` si tu peux la lire, sinon omets cette ligne.

---

# keemboll-powerbi — guide d'utilisation

## Vue d'ensemble

`keemboll-powerbi` ajoute à Claude Code des **règles et méthodes maison** pour gérer et développer un projet BI avec Power BI, du cadrage à l'exploitation. Il complète les skills Microsoft (`fabric-skills`, `powerbi-authoring`), qui gèrent la **mécanique** (fichiers PBIP, API Fabric, connexion à Power BI Desktop). Les skills se chargent **automatiquement** selon votre demande : il suffit d'écrire ce que vous voulez en français.

| Section | Contenu |
|---|---|
| `installation` | Prérequis et installation |
| `skills` | Les 14 skills et quand ils s'activent |
| `exemples` | Demandes prêtes à l'emploi |
| `projet` | Phases d'un projet BI et fichiers à la racine du projet |
| `agents` | Sous-agents fournis ; utilisation avec Codex, Grok, Gemini… |
| `lean` | Le script d'analyse `lean.py` |
| `dette` | `DEBT.md` et `CHANGES.md` |
| `methode` | La méthode de travail recommandée |
| `securite` | Données sensibles et garde-fous |
| `depannage` | Problèmes fréquents |

## installation

Prérequis sur le poste : **Azure CLI** (`az login --allow-no-subscriptions`), **Node.js LTS** (pour le serveur MCP Microsoft), **Python 3.8+** (pour `lean.py`), **Git** (avec `git config --global credential.helper manager`), **Claude Code**.

```powershell
# Skills Microsoft (mécanique PBIP / Fabric)
claude plugin marketplace add microsoft/skills-for-fabric
claude plugin install fabric-skills@fabric-collection
claude plugin install powerbi-authoring@fabric-collection

# Skills maison
claude plugin marketplace add keemboll/keemboll-bi
claude plugin install keemboll-powerbi@keemboll
```

Puis dans Claude Code : `/plugin` → **Marketplaces** → `keemboll` et `fabric-collection` → **Enable auto-update**. Vérifier avec `/mcp` que `plugin:powerbi-authoring:powerbi-modeling-mcp` est connecté (sinon **Reconnect**).

Les rapports doivent être enregistrés au format **PBIP** (Power BI Desktop → Fichier → Enregistrer sous → *Fichiers projet Power BI*).

## skills

**Piloter et livrer**

| Skill | S'active quand vous… |
|---|---|
| `powerbi-project` | démarrez ou reprenez un projet, cadrez un besoin, définissez des KPI, demandez la prochaine étape ou si un livrable est terminé |
| `powerbi-governance` | concevez ou relisez des rôles RLS / OLS, décidez qui voit quoi, préparez une publication (sensibilité, endossement, accès) |
| `powerbi-testing` | voulez vérifier un modèle ou une mesure, prouver qu'un changement n'a rien cassé, tester la sécurité, conduire une recette |
| `powerbi-alm` | organisez le dépôt, les branches, les environnements, une mise en production ou une intégration continue |
| `powerbi-documentation` | documentez un modèle ou un rapport : dictionnaire de données, fiche de rapport, note de version, passation |

**Construire**

| Skill | S'active quand vous… |
|---|---|
| `powerbi-conventions` | modifiez un modèle ou un rapport ; auditez un modèle « selon nos conventions » (nommage, descriptions, formats, processus de validation, modèle existant, confidentialité) |
| `powerbi-data-modeling` | concevez ou refondez un modèle : schéma en étoile, grain, SCD, dimensions de rôle, table de dates |
| `powerbi-tmdl` | lisez ou modifiez les fichiers `.tmdl` d'un projet PBIP |
| `powerbi-dax-library` | écrivez des mesures : cumuls, N-1, ratios, classements, nouveaux clients, interrupteurs Plan / N-1 |
| `powerbi-performance` | une page ou une mesure est lente ; vous voulez optimiser DAX, modèle ou Power Query |
| `powerbi-mockup` | voulez une maquette HTML d'une page à partir du modèle réel, avant de construire |
| `powerbi-report-design` | concevez ou revoyez une page : quatre questions, grille, couleurs, fonds SVG, accessibilité |
| `powerbi-html-visuals` | voulez un visuel SVG / HTML en DAX (sparkline, barre de progression, carte KPI) |
| `powerbi-lean` | demandez une revue, un audit, l'inventaire d'un champ, l'état de la dette ou le journal des modifications |

Les valeurs marquées « À ADAPTER » dans les skills (préfixes, couleurs, devise…) sont des choix par défaut, pas des obligations.

## exemples

| Objectif | Demande à écrire |
|---|---|
| Découvrir un modèle | « Liste les tables, mesures et relations du modèle de ce projet. » |
| Auditer | « Audite le modèle selon nos conventions. » / « Lance un audit powerbi-lean. » |
| Avant un renommage | « Où est utilisée la mesure [Nom de la mesure] ? » |
| Corriger sans risque | « Applique les corrections sans impact visuel de l'audit (table de dates, summarizeBy, masquage). Montre-moi le plan avant. » |
| Nouvelle mesure | « Ajoute une mesure de cumul annuel et d'évolution vs N-1 pour [Mesure]. Montre-moi le DAX avant. » |
| Nouvelle page | « Fais une maquette HTML d'une page de suivi de [sujet] à partir du modèle. » |
| Lenteur | « Ce visuel met 30 s à charger : diagnostique avec powerbi-performance, sans rien modifier. » |
| Avant commit | « Fais une revue powerbi-lean de mes modifications. » |
| Dette | « Où en est la dette du projet ? » / « Solde D-004 : la correction est faite et vérifiée. » |
| Démarrer un projet | « Cadre un nouveau rapport de suivi de [sujet] : pose-moi les questions de la fiche de cadrage. » |
| KPI | « Ajoute au catalogue KPI.md l'indicateur [nom] ; je te donne la définition métier. » |
| Où en est-on ? | « Où en est ce projet et quelle est la prochaine étape ? » |
| Sécurité | « Conçois les rôles RLS par région, montre-moi le plan et le protocole de test avant d'écrire. » |
| Tests | « Écris les requêtes de contrôle du modèle (clés, intégrité, rapprochement) dans tests/. » |
| Non-régression | « Je vais modifier [Mesure] : prépare le test avant / après. » |
| Mise en production | « Passe la checklist de mise en production et dis-moi ce qui bloque. » |
| CI | « Mets en place une intégration continue qui lance lean.py sur chaque demande de fusion. » |
| Documentation | « Génère DATA_DICTIONARY.md et liste les mesures sans description. » |
| Avis indépendant | « Fais auditer ce projet par powerbi-auditor pendant que je continue. » |

## projet

Le skill `powerbi-project` découpe un projet en phases ; chacune a un livrable, un skill qui fait foi et un critère de sortie :

**cadrage → modélisation → mesures → maquette → rapport → tests et recette → publication → exploitation**

Fichiers à la racine du projet (à côté du `.pbip`), versionnés avec lui :

| Fichier | Rôle | Skill |
|---|---|---|
| `SCOPE.md` | Public, questions métier, périmètre, sources, sécurité, critères de succès | `powerbi-project` |
| `KPI.md` | Catalogue des indicateurs (`K-001`…) : définition métier, formule, mesure, propriétaire | `powerbi-project` |
| `SECURITY_MODEL.md` | Qui voit quoi : matrice rôle × périmètre, validation, date de test | `powerbi-governance` |
| `tests/` et `tests/ACCEPTANCE.md` | Requêtes DAX de contrôle (`T-001`…) et procès-verbal de recette | `powerbi-testing` |
| `DATA_DICTIONARY.md` | Dictionnaire de données généré depuis le modèle | `powerbi-documentation` |
| `DEBT.md`, `CHANGES.md` | Ce qui reste à corriger, ce qui a été fait | `powerbi-lean` |

Aucun de ces fichiers ne contient de valeurs réelles ni de noms de personnes. Les décisions métier (définition d'un KPI, seuil, périmètre) restent à l'utilisateur : Claude propose, ne tranche pas.

## agents

**Sous-agents fournis** (Claude les lance quand la tâche s'y prête, ou sur demande : « fais auditer par powerbi-auditor ») :

| Sous-agent | Rôle |
|---|---|
| `powerbi-auditor` | Relecteur en **lecture seule** : audit, revue d'un changement, contrôle avant mise en production |
| `powerbi-modeler` | Modèle sémantique et mesures DAX, une fois le plan validé |
| `powerbi-report-designer` | Maquette, mise en page, visuels d'une page de rapport |

**Autres agents** (Codex, Grok, Gemini, Copilot, Cursor…) : les skills sont au format ouvert Agent Skills et s'installent dans un projet avec `python scripts/install.py --agent <agent> --target <projet>` depuis une copie du dépôt `keemboll/keemboll-bi`. Détails et emplacements par agent : `docs/agents.md` de ce dépôt. Toute l'équipe applique alors les mêmes règles, quel que soit l'outil.

## lean

Script Python en **lecture seule**, fourni avec `powerbi-lean`. Claude le lance lui-même ; vous pouvez aussi l'exécuter :

```powershell
python "<dossier du skill>/scripts/lean.py" audit <projet>                 # audit complet
python "<dossier du skill>/scripts/lean.py" audit <projet> --changed       # fichiers modifiés depuis le dernier commit
python "<dossier du skill>/scripts/lean.py" usage <projet>                 # champs utilisés par page / visuel
python "<dossier du skill>/scripts/lean.py" usage <projet> --field "[Mesure]"
python "<dossier du skill>/scripts/lean.py" dette <projet>                 # état DEBT.md + CHANGES.md
python "<dossier du skill>/scripts/lean.py" catalogue <projet>             # dictionnaire de données (Markdown) sur la sortie standard
```

`--json` donne une sortie exploitable. « Inutilisé » = non utilisé par **ce** rapport : vérifiez la vue de traçabilité de l'espace de travail avant de supprimer.

## dette

Deux fichiers à la racine de chaque projet, versionnés avec lui :

- `DEBT.md` : ce qui reste à corriger (`D-001`…), avec priorité et échéance.
- `CHANGES.md` : ce qui a été corrigé ou ajouté (`M-001`…), plus récent en haut ; il se remplit à mesure que la dette diminue.

Solder une dette : entrée `M-xxx` dans le journal → `D-xxx` déplacée dans « Soldé » avec `**Modification** : M-xxx` → `lean.py dette` sans incohérence → un commit `M-xxx: …`. Avancée partielle : `D-xxx (partielle)`. Projet existant sans journal : « Initialise CHANGES.md en reprenant l'historique Git ».

## methode

0. **Cadrage** (`SCOPE.md`, `KPI.md`) pour un nouveau projet ou un nouveau rapport.
1. **Audit** en lecture seule.
2. **Plan** priorisé : d'abord ce qui ne change pas les visuels, les renommages en dernier.
3. **Commit de sauvegarde** ; Power BI Desktop enregistré.
4. **Maquette HTML** pour toute nouvelle page.
5. **Exécution** par étapes ; DAX montré avant application ; décisions métier laissées à l'utilisateur.
6. **Vérification** dans Desktop (valeurs avant / après) et revue humaine.
7. **Tests et recette** (`tests/`, `tests/ACCEPTANCE.md`) ; sécurité vérifiée par rôle.
8. **Revue powerbi-lean**, journal, documentation régénérée, commit ; la mise en production suit la checklist de `powerbi-alm`.

## securite

- Claude lit les **métadonnées** du projet (noms, DAX) : vérifiez que c'est autorisé pour le projet.
- Les **données** (`.pbi/cache.abf`) ne doivent jamais être lues ni versionnées : `.gitignore` + règle `deny Read(**/.pbi/cache.abf)` dans `~/.claude/settings.json`.
- Les requêtes DAX via le MCP renvoient de vraies données : à valider une par une (règle `ask`).
- Les maquettes n'utilisent que des valeurs fictives ; `DEBT.md` et `CHANGES.md` ne contiennent jamais de valeurs réelles.
- Dépôts privés uniquement ; pas de `git push` automatique.

## depannage

| Symptôme | Solution |
|---|---|
| Skills absents | `claude plugin list` ; `claude plugin update keemboll-powerbi@keemboll` ; relancer `claude` |
| `powerbi-modeling-mcp` en × | `/mcp` → Reconnect ; si fréquent : `$env:MCP_TIMEOUT="60000"` avant `claude` |
| Écriture refusée par le mode auto | Projet sous Git + `.claude/settings.local.json`, ou mode par défaut (Shift+Tab) |
| `python` ouvre le Microsoft Store | `winget install Python.Python.3.12`, puis rouvrir le terminal |
| Changements non visibles dans Desktop | Appliquer les changements externes (préversion, Desktop d'août 2026 ou plus récent) ou rouvrir le `.pbip` |
| Visuel très lent | « Diagnostique avec powerbi-performance » ; copier la requête de l'Analyseur de performances vers DAX Studio |

Contribuer (nouvelle règle, nouvelle référence visuelle) : voir le `README.md` du dépôt `keemboll/keemboll-bi`.
