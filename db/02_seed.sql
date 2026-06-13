-- ============================================================
-- 03_seed.sql
-- Initial reference data for DevOps HW 2 / Diabetes Predict
--
-- Назначение:
--   - добавить начальную активную версию модели;
--   - не содержит пользователей, потому что users.password_hash
--     должен создаваться через bcrypt в Python-скрипте.
-- ============================================================

INSERT INTO model_versions (
    model_name,
    model_version,
    artifact_path,
    preprocessing_version,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    params_json,
    traffic_weight,
    role
)

VALUES (
    'LogisticRegressionTuned',
    'lab2-1.0.0',
    'experiments/best_model/model.joblib',
    'preprocessing-v1',
    NULL,
    0.7931034482758621,
    0.6734693877551020,
    0.8048780487804879,
    0.7333333333333333,
    '{
        "C": 1,
        "penalty": "l1",
        "class_weight": "balanced",
        "solver": "liblinear",
        "max_iter": 1000
    }'::jsonb,
    100,
    'champion'
)

ON CONFLICT (model_version) DO UPDATE
SET
    model_name = EXCLUDED.model_name,
    artifact_path = EXCLUDED.artifact_path,
    preprocessing_version = EXCLUDED.preprocessing_version,
    trained_on_dataset_id = EXCLUDED.trained_on_dataset_id,
    accuracy_score = EXCLUDED.accuracy_score,
    precision_score = EXCLUDED.precision_score,
    recall_score = EXCLUDED.recall_score,
    f1_score = EXCLUDED.f1_score,
    params_json = EXCLUDED.params_json,
    traffic_weight = EXCLUDED.traffic_weight,
    role = EXCLUDED.role;