# Network Security – Phishing Website Detection (MLOps Project)

An end-to-end machine learning pipeline that detects **phishing websites** from URL/website-based features. The project is built as a production-style MLOps pipeline: raw data is stored in **MongoDB**, run through modular **ingestion → validation → transformation → training** stages, tracked with **MLflow**, served through a **FastAPI** app, containerized with **Docker**, and synced to **AWS S3**.

## What this project does

Phishing websites try to trick users into giving up sensitive information by mimicking legitimate sites. This project trains a binary classifier that predicts whether a website is **legitimate** or **phishing**, based on 30 engineered features extracted from a website/URL (e.g. use of IP address instead of domain name, URL length, presence of `@` symbol, SSL certificate state, domain age, web traffic rank, etc.).

The final trained model + preprocessing object are exposed via a REST API where a user can upload a CSV of website features and get back predictions.

## Dataset

- **File:** `Network_Data/phisingData.csv`
- **Rows / Columns:** 11,055 rows × 31 columns
- **Target column:** `Result` (`1` = legitimate, `-1` = phishing)
- **Features (30):** binary/categorical indicators such as `having_IP_Address`, `URL_Length`, `Shortining_Service`, `having_At_Symbol`, `double_slash_redirecting`, `Prefix_Suffix`, `having_Sub_Domain`, `SSLfinal_State`, `Domain_registeration_length`, `Favicon`, `port`, `HTTPS_token`, `Request_URL`, `URL_of_Anchor`, `Links_in_tags`, `SFH`, `Submitting_to_email`, `Abnormal_URL`, `Redirect`, `on_mouseover`, `RightClick`, `popUpWidnow`, `Iframe`, `age_of_domain`, `DNSRecord`, `web_traffic`, `Page_Rank`, `Google_Index`, `Links_pointing_to_page`, `Statistical_report`

The expected schema for every stage is defined in `data_schema/schema.yaml`, which the data validation step uses to enforce column count/types.

## Project architecture

The pipeline follows a modular **components → entity → pipeline** design:

```
Network_Data/phisingData.csv
        │  (push_data.py)
        ▼
    MongoDB Atlas (NetworkSecurity.NetworkData)
        │
        ▼
 1. Data Ingestion        → pulls data from MongoDB, splits into train/test
 2. Data Validation        → validates schema, checks for dataset drift (KS test)
 3. Data Transformation    → KNN imputation + preprocessing, saves .npy arrays
 4. Model Trainer          → trains & selects best classifier, logs to MLflow
        │
        ▼
  final_model/model.pkl, final_model/preprocessor.pkl
        │
        ▼
     FastAPI app (app.py) → /train and /predict endpoints
        │
        ▼
   Artifacts synced to AWS S3 (networksecurity/cloud/s3_syncer.py)
```

### Repository structure

```
├── app.py                        # FastAPI app: /train and /predict endpoints
├── main.py                       # Script entry point to run the training pipeline
├── push_data.py                  # Loads the CSV into MongoDB
├── setup.py                      # Packaging config
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Container build (FastAPI + AWS CLI)
├── data_schema/schema.yaml       # Expected column names/types
├── Network_Data/phisingData.csv  # Raw phishing dataset
├── final_model/                  # Trained model.pkl + preprocessor.pkl
├── templates/table.html          # HTML template for showing predictions
├── prediction_output/output.csv  # Sample output of a prediction run
├── valid_data/test.csv           # Sample validated test data
└── networksecurity/
    ├── components/                # data_ingestion, data_validation, data_transformation, model_trainer
    ├── entity/                    # config_entity.py, artifact_entity.py (dataclasses for configs/artifacts)
    ├── pipeline/training_pipeline.py  # Orchestrates all components end-to-end
    ├── cloud/s3_syncer.py         # Syncs local artifacts/model to an S3 bucket
    ├── constants/training_pipeline # All pipeline constants (paths, DB/collection names, etc.)
    ├── utils/                     # main_utils (save/load objects, yaml I/O) & ml_utils (metrics, estimator)
    ├── exception/                 # Custom NetworkSecurityException
    └── logging/                   # Custom logger
```

## Pipeline stages in detail

1. **Data Ingestion** (`components/data_ingestion.py`)
   Reads data from the `NetworkSecurity.NetworkData` MongoDB collection, writes it to a feature store CSV, then splits it into train/test sets (80/20 by default).

2. **Data Validation** (`components/data_validation.py`)
   Confirms the number of columns matches `data_schema/schema.yaml`, and checks for **data drift** between the base and current datasets using the Kolmogorov–Smirnov test, writing a drift report YAML.

3. **Data Transformation** (`components/data_transformation.py`)
   Applies **KNN imputation** (`n_neighbors=3`) to handle missing values, fits/saves a preprocessing pipeline (`preprocessor.pkl`), and stores transformed train/test arrays as `.npy` files.

4. **Model Trainer** (`components/model_trainer.py`)
   Trains and compares several classifiers — **Random Forest, Decision Tree, Gradient Boosting, Logistic Regression, AdaBoost** — with hyperparameter grids, selects the best-performing model by evaluation score, computes F1/precision/recall, logs metrics and the model to **MLflow**, and saves the final `model.pkl` + `preprocessor.pkl` to `final_model/`.

5. **Serving** (`app.py`)
   A FastAPI app exposes:
   - `GET /train` — runs the full training pipeline on demand
   - `POST /predict` — accepts an uploaded CSV of features, loads the saved model/preprocessor, returns predictions rendered as an HTML table (and saves them to `prediction_output/output.csv`)

6. **Cloud sync** (`networksecurity/cloud/s3_syncer.py`)
   After training, artifacts and the final model are synced to an AWS S3 bucket (`TRAINING_BUCKET_NAME` in constants) for versioned storage.

## Tech stack

- **Language:** Python 3.10
- **ML:** scikit-learn, XGBoost, SciPy
- **Data:** Pandas, NumPy, MongoDB (via `pymongo`)
- **Experiment tracking:** MLflow (optionally DagsHub)
- **API:** FastAPI + Uvicorn
- **Cloud:** AWS S3 (artifact/model sync), AWS CLI in Docker image
- **Containerization:** Docker

## Setup & installation

```bash
# 1. Clone the repo
git clone https://github.com/ranjitpawar7271-web/NetworkSecurity_DS_Project.git
cd NetworkSecurity_DS_Project

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

### Environment variables

Create a `.env` file in the project root with:

```
MONGO_DB_URL=<your MongoDB connection string>
```

(`app.py` reads `MONGODB_URL_KEY`; `data_ingestion.py`/`push_data.py` read `MONGO_DB_URL` — make sure both are set to your MongoDB URI, or align the variable name if you rename one.)

For S3 sync, configure AWS credentials (e.g. via `aws configure` or standard AWS environment variables).

## Usage

**1. Load the dataset into MongoDB:**
```bash
python push_data.py
```

**2. Run the training pipeline (CLI):**
```bash
python main.py
```

**3. Run the API server:**
```bash
python app.py
# or
uvicorn app:app --host 0.0.0.0 --port 8000
```
Then visit `http://localhost:8000/docs` for interactive Swagger docs, or:
- `GET /train` to trigger training
- `POST /predict` with a CSV file to get predictions

**4. Run with Docker:**
```bash
docker build -t network-security-app .
docker run -p 8000:8000 --env-file .env network-security-app
```

## Model output

Predictions are returned with a `predicted_column` (`1` = legitimate, `-1` = phishing) appended to the uploaded data, rendered as an HTML table and saved to `prediction_output/output.csv`.

## Author

**Ranjit Pawar**
