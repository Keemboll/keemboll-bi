# Checklist qualité et accessibilité

## Accessibilité

- [ ] Contraste texte / fond ≥ 4,5:1 (≥ 3:1 pour les grands textes et éléments graphiques).
- [ ] Aucune information portée **uniquement** par la couleur (ajouter icône, signe, libellé).
- [ ] **Texte alternatif** renseigné sur chaque visuel porteur d'information (peut être une mesure DAX dynamique).
- [ ] **Ordre de tabulation** défini (Affichage → Volet de sélection → Ordre de tabulation) ; éléments décoratifs masqués de la tabulation.
- [ ] Titres de visuels explicites ; pas de texte dans des images.
- [ ] Taille de police ≥ 10 pt pour les étiquettes, ≥ 12 pt pour les titres.
- [ ] Test du rapport avec le thème « contraste élevé » de Windows.

## Qualité

- [ ] Thème `theme-keemboll.json` appliqué, pas de couleurs codées en dur hors thème.
- [ ] Alignement sur la grille de 8 px, marges cohérentes.
- [ ] Unité et période visibles pour chaque chiffre.
- [ ] Filtres actifs visibles.
- [ ] Interactions entre visuels vérifiées.
- [ ] Pages masquées : infobulles et extractions uniquement.
- [ ] Analyseur de performances : aucun visuel > 2 s (voir `powerbi-performance`).
- [ ] Mise en page mobile créée pour les pages consultées sur téléphone — **À ADAPTER**.
- [ ] Noms de pages courts et explicites ; page d'accueil ou sommaire si > 5 pages.
