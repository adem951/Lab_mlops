# 🚀 Model Promotion Pipeline - MLOps Exercise

Pipeline MLOps complet démontrant la gestion automatisée du cycle de vie des modèles avec quality gates, environnements staging et promotion vers production.

## 📋 Vue d'ensemble

Ce projet implémente un pipeline ML qui :

- ✅ Entraîne et enregistre des modèles dans MLflow
- ✅ Déploie automatiquement vers l'environnement staging
- ✅ Exécute des quality gates (précision)
- ✅ Promeut les modèles vers production seulement si les gates passent
- ✅ Sert les modèles via Flask avec endpoints staging/production séparés

## 📁 Structure du projet

```
Lab_mlops/
├── ml/                                # Scripts ML
│   ├── train_and_register.py         # Entraîne et enregistre dans MLflow
│   ├── evaluate.py                    # Quality gate (évaluation)
│   ├── requirements.txt               # mlflow, scikit-learn
│   └── Dockerfile                     # Image Docker pour training
├── backend/                           # API Flask
│   ├── app.py                         # API avec /health et /predict
│   ├── model_loader.py                # Charge modèles depuis MLflow
│   ├── requirements.txt               # flask, mlflow, scikit-learn
│   └── Dockerfile                     # Image Docker pour serving
├── frontend/                          # Interface web simple
│   └── index.html                     # Dashboard de prédiction
├── deploy/                            # Déploiement local
│   ├── docker-compose.staging.yml    # Staging sur port 8000
│   └── docker-compose.production.yml # Production sur port 8001
├── .github/workflows/                # CI/CD GitHub Actions
│   ├── train_register_deploy_staging.yml  # Workflow 1: Candidate → Staging
│   └── promote_deploy_production.yml      # Workflow 2: Promote → Production
├── .env.example                       # Template variables d'environnement
└── README.md
```

## 🚀 Configuration initiale

### A) Secrets GitHub

Créez ces secrets dans votre repo GitHub (Settings → Secrets and variables → Actions):

- `DAGSHUB_MLFLOW_TRACKING_URI` : `https://dagshub.com/<org>/<repo>.mlflow`
- `DAGSHUB_TOKEN` : Votre personal access token DagsHub
- `DOCKERHUB_USERNAME` : Votre nom d'utilisateur Docker Hub
- `DOCKERHUB_TOKEN` : Votre token Docker Hub

### B) Nom du modèle MLflow

Le modèle s'appelle : **`churn-model`**

### C) Configuration locale

```powershell
# Créer un fichier .env à la racine
MLFLOW_TRACKING_URI=https://dagshub.com/<org>/<repo>.mlflow
MLFLOW_TRACKING_TOKEN=your-dagshub-token
```

## 🔄 Les 2 Workflows

### Workflow 1: Candidate → Staging

**Fichier**: `.github/workflows/train_register_deploy_staging.yml`

**Déclenchement**:
- Manuel via GitHub Actions (workflow_dispatch)
- Automatique lors de push dans `ml/`

**Étapes**:
1. **Train & Register**: Entraîne un modèle et l'enregistre dans MLflow
2. **Evaluate Gate**: Vérifie que accuracy >= 0.90
3. **Deploy Staging**: Build et push l'image Docker (si gate passé)
4. **Smoke Test**: Placeholder pour tests

### Workflow 2: Promote → Production

**Fichier**: `.github/workflows/promote_deploy_production.yml`

**Déclenchement**:
- Manuel uniquement (workflow_dispatch)
- Nécessite le numéro de version du modèle en input

**Étapes**:
1. **Promote**: Transition du modèle vers stage "Production" dans MLflow
2. **Deploy Production**: Build et push l'image Docker production

## 📝 Réalisation des Tasks

### Task 1: Run Candidate → Staging workflow

1. **Aller dans GitHub Actions**
   - Onglet "Actions" de votre repo
   - Sélectionner "Candidate to Staging"
   - Cliquer "Run workflow"

2. **Observer les logs**
   - Job "train_register": Noter run_id, accuracy, model_version
   - Job "Evaluate gate": Voir si PASSED ou FAILED
   - Job "deploy_staging": Seulement si gate passed

3. **Deliverables à noter**:
   ```
   Model version number: ___
   Accuracy: ___
   Did the gate pass? YES / NO
   ```

### Task 2: Explain what "staging" proves

**Réponse courte**:

Staging teste que le modèle fonctionne comme **service déployé**, pas seulement comme script. Il valide:
- Le modèle se charge correctement depuis MLflow registry
- L'API fonctionne avec le modèle
- Le format requête/réponse est correct
- La latence est acceptable
- L'environnement Docker fonctionne

**Ce que l'évaluation offline ne teste pas**: l'intégration complète du déploiement.

### Task 3: Promote to production

1. **Déclencher le workflow "Promote to Production"**
   - Actions → "Promote to Production"
   - Run workflow
   - Entrer le `model_version` de Task 1

2. **Observer les logs**
   - Chercher la ligne: `Promoted churn-model v{version} to Production`

3. **Deliverable**: Screenshot de cette ligne de promotion

### Task 4: Prove production uses registry stage

**Local testing**:

```powershell
# Terminal 1 - Staging
cd deploy
$env:MLFLOW_TRACKING_URI = "votre-uri"
$env:MLFLOW_TRACKING_TOKEN = "votre-token"
docker-compose -f docker-compose.staging.yml up --build

# Terminal 2 - Production
cd deploy
$env:MLFLOW_TRACKING_URI = "votre-uri"
$env:MLFLOW_TRACKING_TOKEN = "votre-token"
docker-compose -f docker-compose.production.yml up --build

# Terminal 3 - Tester
curl http://localhost:8000/health
# Devrait retourner: {"status": "ok", "stage": "Staging"}

curl http://localhost:8001/health
# Devrait retourner: {"status": "ok", "stage": "Production"}
```

**Deliverable**: Screenshots montrant que staging et production servent des stages différents.

## 🧪 Tests locaux

### Test du workflow complet manuellement

```powershell
# 1. Entraîner un modèle
cd ml
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

$env:MLFLOW_TRACKING_URI = "votre-uri"
$env:MLFLOW_TRACKING_TOKEN = "votre-token"
$env:MODEL_NAME = "churn-model"

python train_and_register.py > output.json
Get-Content output.json

# 2. Évaluer
Get-Content output.json | python evaluate.py
# Si exit code = 0 → gate passed

# 3. Démarrer staging
cd ..\deploy
docker-compose -f docker-compose.staging.yml up

# 4. Tester staging
curl http://localhost:8000/health
curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d '{"features": [[0.1,0.2,0.0,0.4,0.5,0.0,0.2,0.1,0.3,0.9]]}'
```

## 🎯 API Endpoints

### `GET /health`
Retourne le statut et le stage du modèle

**Réponse**:
```json
{
  "status": "ok",
  "stage": "Staging"
}
```

### `POST /predict`
Fait des prédictions

**Requête**:
```json
{
  "features": [[0.1, 0.2, 0.0, 0.4, 0.5, 0.0, 0.2, 0.1, 0.3, 0.9]]
}
```

**Réponse**:
```json
{
  "predictions": [0]
}
```

## 💡 Questions de discussion

### 1. Pourquoi est-il dangereux de déployer "ce qui vient d'être mergé sur main" comme modèle?

- Pas de validation de la qualité du modèle
- Pourrait déployer un modèle dégradé ou cassé
- Pas de tests dans staging d'abord
- Pas de suivi de version
- Contourne tous les quality gates

### 2. Qu'est-ce que le registry stage apporte qu'un Git tag n'apporte pas?

- **Artifacts du modèle** (poids, preprocessors), pas juste le code
- **Metadata**: métriques, paramètres, version des données
- **Lineage**: quelle donnée et quel code ont produit ce modèle
- **Transitions de stage**: Staging → Production avec audit trail
- **Rollback**: peut instantanément revenir à une version précédente
- Git tag = version du code, MLflow stage = version du modèle + artifacts

### 3. Si staging passe mais production échoue, quelles pourraient être les causes?

- **Différences d'environnement**: ressources, dépendances, config
- **Différences de données**: distribution différente en production
- **Problèmes d'échelle**: charge plus élevée en production
- **Infrastructure**: réseau, firewall, connexions externes
- **Timing**: mauvaise version chargée depuis le registry

### 4. Où devrait se placer DVC dans un pipeline sérieux?

- **Training data snapshot**: ✅ OUI - Pin la version exacte des données
- **Evaluation dataset**: ✅ OUI - Ensemble de test fixe pour comparaisons
- **Drift reference dataset**: ✅ OUI - Baseline pour détecter le drift

**Où**: Avant training, `dvc pull` pour récupérer les données exactes, logger le hash DVC dans MLflow pour reproductibilité complète.

### 5. Que devrait-on ajouter au gate au-delà de l'accuracy?

- **Métriques métier**: précision, recall, F1-score
- **Performance opérationnelle**: latence (p95, p99), throughput
- **Qualité des données**: validation du schéma, valeurs manquantes
- **Fairness**: performance sur différents groupes démographiques
- **Tests fonctionnels**: santé de l'API, format de réponse
- **Coût**: coût par prédiction

## 🐛 Dépannage

### Le modèle ne se charge pas
```powershell
# Vérifier la connexion MLflow
python -c "import mlflow; mlflow.set_tracking_uri('votre-uri'); print(mlflow.list_experiments())"
```

### Les containers Docker ne démarrent pas
```powershell
# Vérifier que le fichier .env existe
Get-Content .env

# Voir les logs
docker-compose -f deploy/docker-compose.staging.yml logs
```

### Le quality gate échoue toujours
```powershell
# Baisser le threshold pour tester
$env:ACCURACY_THRESHOLD = "0.80"
```

## 📚 Points clés de l'exercice

1. ✅ Pattern Model Registry avec MLflow
2. ✅ Déploiement multi-environnement (staging/production)
3. ✅ Quality gates automatisés
4. ✅ CI/CD pour ML avec GitHub Actions
5. ✅ Containerisation des services ML
6. ✅ Séparation des workflows pour candidats et promotion

---

**Bonne chance pour vos tasks! 🎓**
