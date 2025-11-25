from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer

from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier, XGBRegressor

def create_ml_pipeline(model, numeric_features: list, categorical_features: list) -> Pipeline:
    """
    Creates a full machine learning pipeline including preprocessing for
    numeric and categorical features.

    Args:
        model: The machine learning model/estimator to be used at the end of the pipeline.
        numeric_features: A list of column names for numeric features.
        categorical_features: A list of column names for categorical features.

    Returns:
        A scikit-learn Pipeline object.
    """

    # Create preprocessing steps for numeric features
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')), # Impute missing values with the median
        ('scaler', StandardScaler()) # Scale features to have zero mean and unit variance
    ])

    # Create preprocessing steps for categorical features
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')), # Impute missing values with the mode
        ('onehot', OneHotEncoder(handle_unknown='ignore')) # Convert categories to one-hot vectors
    ])

    # Create a preprocessor object using ColumnTransformer
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ],
        remainder='passthrough' # Keep other columns (if any), though typically we specify all
    )

    # Create the final pipeline by combining the preprocessor and the model
    pipeline = Pipeline(steps=[('preprocessor', preprocessor),
                               ('classifier' if hasattr(model, 'predict_proba') else 'regressor', model)])

    print(f"Pipeline created successfully for model: {model.__class__.__name__}")
    return pipeline

def get_classification_pipelines(numeric_features: list, categorical_features: list) -> dict:
    """
    Returns a dictionary of predefined classification pipelines.
    """
    models = {
        "RandomForest": RandomForestClassifier(random_state=42),
        "XGBoost": XGBClassifier(random_state=42, use_label_encoder=False, eval_metric='logloss'),
        "LogisticRegression": LogisticRegression(random_state=42),
        "DecisionTree": DecisionTreeClassifier(random_state=42),
    }

    pipelines = {name: create_ml_pipeline(model, numeric_features, categorical_features) for name, model in models.items()}
    return pipelines

def get_regression_pipelines(numeric_features: list, categorical_features: list) -> dict:
    """
    Returns a dictionary of predefined regression pipelines.
    """
    models = {
        "RandomForestRegressor": RandomForestRegressor(random_state=42),
        "XGBoostRegressor": XGBRegressor(random_state=42),
        "LinearRegression": LinearRegression(),
    }

    pipelines = {name: create_ml_pipeline(model, numeric_features, categorical_features) for name, model in models.items()}
    return pipelines
