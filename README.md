
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

## 4. Déploiement Kubernetes

Les manifests sont séparés par service dans `k8s/` : chaque dossier contient ses
propres fichiers de configuration, Service, Deployment ou StatefulSet et PVC.
La configuration de chaque pipeline Logstash est dans un fichier `.conf` dédié
sous `k8s/logstash/pipeline/`. Kustomize les regroupe dans la ConfigMap montée par
Logstash. Le cluster doit fournir une StorageClass par défaut.

Avant le déploiement :

1. Remplacez `logcommerce-webapp:latest` dans
   `k8s/webapp/deployment.yaml` par l'image Flask existante. Elle doit écouter
   sur le port `5000`.
2. Créez le Secret localement. Les identifiants générés ne sont pas enregistrés
   dans Git :

   ```powershell
   .\scripts\create-k8s-secrets.ps1
   ```

3. Appliquez les services de base (Elasticsearch, Logstash, Kibana, MongoDB et
   Redis) :

   ```powershell
   kubectl apply -k k8s/
   ```

L'application Flask et l'Ingress restent optionnels et ne sont pas inclus dans
`k8s/kustomization.yaml`.
Le service Elasticsearch est configuré sans authentification pour ce déploiement
local et n'est exposé qu'en `ClusterIP`. Le Secret contient les identifiants
MongoDB, Redis et la clé Flask. Installez également un contrôleur
`ingress-nginx` dans le cluster ; l'Ingress publie l'application sur
`http://logcommerce.local/` et Kibana sous `/kibana`.

Logstash reçoit des événements JSON Lines par TCP sur le port `5000` et les
indexe dans Elasticsearch sous `ecommerce-logs-*`. Vérifiez le déploiement avec
`kubectl get pods,svc,pvc -n logcommerce`.


