import scipy
import pickle
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.linear_model import Lasso, Ridge, ElasticNet
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler, StandardScaler
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.model_selection import cross_val_score, GridSearchCV

train_path = "data/working/train_df.pkl"
train_df = pd.read_pickle(train_path)

X_train = train_df.drop("price", axis=1)
y_train = train_df.price

# define the intended features and type
num_cols = ["bedrooms", "bathrooms", "sqft_living", "sqft_lot"]
cat_cols = ["waterfront", "zipcode", "condition", "view"]

# define our numerical and categorical pipelines
num_pipe = Pipeline(
    steps=[
        ("impute", SimpleImputer(strategy="mean")),
        ("standardize", StandardScaler()),
        ("scale", MinMaxScaler()),
    ]
)
cat_pipe = Pipeline(
    steps=[
        ("impute", SimpleImputer(strategy="most_frequent")),
        ("one-hot", OneHotEncoder(handle_unknown="ignore", sparse=False)),
    ]
)

# combine preprocessing pipelines
preprocessor = ColumnTransformer(
    transformers=[
        ("numerical", num_pipe, num_cols),
        ("categorical", cat_pipe, cat_cols),
    ]
)

# define estimator - TransformedTargetRegressor to normalize the target variable
estimator = TransformedTargetRegressor(
    regressor=Ridge(), func=np.log10, inverse_func=scipy.special.exp10
)

# construct full pipeline
full_pipe = Pipeline(steps=[("preprocess", preprocessor), ("model", estimator)])

# perform gridsearch to find best param settting
gscv = GridSearchCV(
    full_pipe,
    param_grid={"model__regressor__alpha": np.arange(0.1, 1, 0.1)},
    cv=5,
    scoring="neg_mean_absolute_error",
    n_jobs=-1,
)

gscv.fit(X_train, y_train)
print(f'Best MAE: {gscv.best_score_}')

# save model
with open("model.pkl", "wb") as f:
    pickle.dump(gscv.best_estimator_, f)