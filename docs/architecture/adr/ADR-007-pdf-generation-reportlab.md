# ADR-00X : Génération native de rapports PDF via ReportLab

## Statut
Validé

## Contexte
Le cahier des charges de la plateforme SENTRA exige la génération de rapports d'incidents automatisés et exportables, notamment au format PDF. 
Dans un environnement web classique, la méthode courante consiste à générer du HTML/CSS puis à utiliser un outil de conversion externe (comme `wkhtmltopdf`, Puppeteer, ou headless Chrome) pour créer le PDF.

## Décision
Nous avons décidé d'utiliser la bibliothèque Python **ReportLab** pour construire les fichiers PDF de manière native, plutôt que de passer par une conversion HTML-vers-PDF.

## Conséquences

### Avantages
* **Conteneurisation ultra-légère :** Ne nécessitant aucun binaire système (pas de Chrome, pas de dépendances C++ complexes), l'image Docker du moteur de reporting reste basée sur `python:3.11-slim`, réduisant drastiquement la surface d'attaque et le temps de build.
* **Vitesse d'exécution :** La génération est instantanée car elle ne nécessite pas le rendu DOM d'un moteur de navigateur web.
* **Sécurité :** L'absence d'interprétation HTML empêche toute faille de type XSS (Cross-Site Scripting) lors de l'injection des payloads malveillants capturés par l'IDS dans le rapport final.

### Inconvénients
* **Complexité de mise en page :** La stylisation des tableaux et des paragraphes se fait via le code Python (styles ReportLab) et non via CSS, ce qui rend les modifications visuelles légèrement plus laborieuses. Ce compromis a été jugé acceptable face aux gains de sécurité et de performance.