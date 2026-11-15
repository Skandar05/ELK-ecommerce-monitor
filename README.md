
# Plateforme de Monitoring et d'Analyse de Logs E-Commerce

Projet **ELK, NoSQL et Interface Web** 

---

## 1. Contexte

Une plateforme de vente en ligne traite plusieurs milliers de commandes par jour. Ses logs (paiements, erreurs, navigation, performance, fraude) sont dispersés sur différents serveurs, ce qui rend le diagnostic des incidents long et complexe. Il n'existe ni centralisation, ni alerting automatique, ni visualisation des tendances.

## 2. Objectif

Concevoir, développer et déployer une plateforme qui :

1. **Centralise** la collecte des logs e-commerce (fichiers CSV, JSON, TXT)
2. **Indexe** les données pour une recherche rapide (Elasticsearch)
3. **Visualise** les KPI et les tendances (Kibana et interface web)
4. **Offre une interface web** pour rechercher, filtrer et exporter les logs
5. **Se déploie facilement** grâce à Docker Compose

### KPI suivis

- Taux de conversion
- Taux d'abandon de panier
- Temps moyen de traitement des commandes
- Nombre d'erreurs par service
- Détection des pics de trafic

### Cas d'usage prioritaires

- Alerter l'équipe technique en cas de pic d'erreurs de paiement
- Analyser les parcours utilisateurs pour optimiser le tunnel de vente
- Identifier les produits générant le plus d'erreurs

## 3. Stack technique

| Composant | Technologie | Rôle |
|---|---|---|
| Indexation et recherche | Elasticsearch 8.x | Stockage et recherche des logs |
| Ingestion | Logstash 8.x | Parsing et enrichissement des fichiers |
| Visualisation | Kibana 8.x | Dashboards et visualisations |
| Backend / API REST | Flask 3.x (Python 3.11) | Application web et API |
| Base NoSQL documents | MongoDB 7.x | Métadonnées des fichiers, historique des recherches, utilisateurs |
| Cache / sessions | Redis 7.x | Cache des requêtes, sessions, rate limiting |
| Frontend | HTML5, CSS3, JavaScript, Bootstrap 5, Chart.js, DataTables | Interface responsive |
| Conteneurisation | Docker, Docker Compose | Orchestration de tous les services |



