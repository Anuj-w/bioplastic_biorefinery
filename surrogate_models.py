import biosteam as bst
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    r2_score,
    mean_absolute_error,
    mean_squared_error
)
# Predictive behavior study using linear regression

X = results[
    [
        ('Feed', 'Total feed [kg/hr]'),
        ('PLA', 'Price [$/kg]'),
        ('Lignin', 'Price [$/kg]'),
        ('PEG400', 'Price [$/kg]'),
        ('Film extrusion', 'Y [fraction]')
    ]
]

y_msp = results[('-', 'MSP [USD/kg]')]
y_tci = results[('-', 'TCI [10^6*USD]')]
y_npv = results[('-', 'NPV [$]')]
y_aoc = results[('-', 'AOC [$/yr]')]

print('\n MSP Linear Regression \n')
model_msp = LinearRegression()
model_msp.fit(X, y_msp)
print(model_msp.intercept_)
print(model_msp.coef_)
X_train, X_test, y_train, y_msp_test = train_test_split(
    X,
    y_msp,
    test_size=0.2,
    random_state=42
)
model_msp.fit(X_train, y_train)
y_pred_msp = model_msp.predict(X_test)
r2_msp = r2_score(y_msp_test, y_pred_msp)
mae_msp = mean_absolute_error(y_msp_test, y_pred_msp)
rmse_msp = mean_squared_error(
    y_msp_test,
    y_pred_msp
) ** 0.5
print("R²:", r2_msp)
print("MAE:", mae_msp)
print("RMSE:", rmse_msp)

print('\n TCI Linear Regression \n')
model_tci = LinearRegression()
model_tci.fit(X, y_tci)
print(model_tci.intercept_)
print(model_tci.coef_)
X_train, X_test, y_train, y_tci_test = train_test_split(
    X,
    y_tci,
    test_size= 0.2,
    random_state= 42,
)
model_tci.fit(X_train, y_train)
y_pred_tci = model_tci.predict(X_test)
r2_tci = r2_score(y_tci_test, y_pred_tci)
mae_tci = mean_absolute_error(y_tci_test, y_pred_tci)
rmse_tci = mean_squared_error(
    y_tci_test,
    y_pred_tci,
)**0.5
print("R²:", r2_tci)
print("MAE:", mae_tci)
print("RMSE:", rmse_tci)

print('\n NPV Linear Regression \n')
model_npv = LinearRegression()
model_npv.fit(X, y_npv)
print(model_npv.intercept_)
print(model_npv.coef_)
X_train, X_test, y_train, y_npv_test = train_test_split(
    X,
    y_npv,
    test_size= 0.2,
    random_state= 42
)
model_npv.fit(X_train, y_train)
y_pred_npv = model_npv.predict(X_test)
r2_npv = r2_score(y_npv_test, y_pred_npv)
mae_npv = mean_absolute_error(y_npv_test, y_pred_npv)
rmse_npv = mean_squared_error(
    y_npv_test,
    y_pred_npv
)**0.5
print("R²:", r2_npv)
print("MAE:", mae_npv)
print("RMSE:", rmse_npv)

print('\n AOC Linear Regression \n')
model_aoc = LinearRegression()
model_aoc.fit(X, y_aoc)
print(model_aoc.intercept_)
print(model_aoc.coef_)
X_train, X_test, y_train, y_aoc_test = train_test_split(
    X,
    y_aoc,
    test_size=0.2,
    random_state=42
)
model_aoc.fit(X_train, y_train)
y_pred_aoc = model_aoc.predict(X_test)
r2_aoc = r2_score(y_aoc_test, y_pred_aoc)
mae_aoc = mean_absolute_error(y_aoc_test, y_pred_aoc)
rmse_aoc = mean_squared_error(
    y_aoc_test,
    y_pred_aoc
) ** 0.5
print("R²:", r2_aoc)
print("MAE:", mae_aoc)
print("RMSE:", rmse_aoc)

def parity_plot(y_test, y_pred, name, units):

    # Calculate metrics
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = mean_squared_error(y_test, y_pred) ** 0.5

    plt.figure(figsize=(6, 6))

    # Scatter plot
    plt.scatter(y_test, y_pred)

    # 1:1 parity line
    min_value = min(y_test.min(), y_pred.min())
    max_value = max(y_test.max(), y_pred.max())

    plt.plot(
        [min_value, max_value],
        [min_value, max_value],
        linestyle='--'
    )

    # Labels
    plt.xlabel(f"Actual {name} [{units}]")
    plt.ylabel(f"Predicted {name} [{units}]")
    plt.title(f"{name} Linear Regression")

    # Metrics box
    metrics_text = (
        f"$R^2$ = {r2:.4f}\n"
        f"MAE = {mae:.4g}\n"
        f"RMSE = {rmse:.4g}"
    )

    plt.text(
        0.05,
        0.95,
        metrics_text,
        transform=plt.gca().transAxes,
        verticalalignment='top',
        bbox=dict(
            boxstyle='round',
            facecolor='white',
            alpha=0.8
        )
    )

    plt.tight_layout()
    plt.show()

parity_plot(
    y_msp_test,
    y_pred_msp,
    "MSP",
    "USD/kg"
)

parity_plot(
    y_tci_test,
    y_pred_tci,
    "TCI",
    "10^6*USD"
)

parity_plot(
    y_npv_test,
    y_pred_npv,
    "NPV",
    "$"
)

parity_plot(
    y_aoc_test,
    y_pred_aoc,
    "AOC",
    "$/yr",
)

# Independent validation and model selection

np.random.seed(1234)
samples_validation = model.sample(N =5000, rule = 'L')
model.load_samples(samples_validation, sort = True)
model.evaluate()
validation_results = model.table.copy()
validation_results

def evaluate_model(y_true, y_pred, name):

    r2 = r2_score(y_true, y_pred)

    mae = mean_absolute_error(
        y_true,
        y_pred
    )

    rmse = mean_squared_error(
        y_true,
        y_pred
    ) ** 0.5

    print(f"\n{name}")
    print(f"R²   : {r2:.6f}")
    print(f"MAE  : {mae:.6f}")
    print(f"RMSE : {rmse:.6f}")

    return r2, mae, rmse
X_validation = validation_results[
    [
        ('Feed', 'Total feed [kg/hr]'),
        ('PLA', 'Price [$/kg]'),
        ('Lignin', 'Price [$/kg]'),
        ('PEG400', 'Price [$/kg]'),
        ('Film extrusion', 'Y [fraction]')
    ]
]

y_msp_validation = validation_results[
    ('-', 'MSP [USD/kg]')
]

y_irr_validation = validation_results[
    ('-', 'IRR [%]')
]

y_npv_validation = validation_results[
    ('-', 'NPV [$]')
]

print('\n Independent validation MSP Linear Regression \n')

y_pred_msp_validation = model_msp.predict(X_validation)


print('\n Independent validation IRR Linear Regression \n')


y_pred_irr_validation = model_irr.predict(X_validation)


print('\n Independent validation NPV Linear Regression \n')


y_pred_npv_validation = model_npv.predict(X_validation)

evaluate_model(
    y_msp_validation,
    y_pred_msp_validation,
    "MSP - Independent Validation"
)

evaluate_model(
    y_irr_validation,
    y_pred_irr_validation,
    "IRR - Independent Validation"
)

evaluate_model(
    y_npv_validation,
    y_pred_npv_validation,
    "NPV - Independent Validation"
)

def parity_plot(y_test, y_pred, name, units):

    # Calculate metrics
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = mean_squared_error(y_test, y_pred) ** 0.5

    plt.figure(figsize=(6, 6))

    # Scatter plot
    plt.scatter(y_test, y_pred)

    # 1:1 parity line
    min_value = min(y_test.min(), y_pred.min())
    max_value = max(y_test.max(), y_pred.max())

    plt.plot(
        [min_value, max_value],
        [min_value, max_value],
        linestyle='--'
    )

    # Labels
    plt.xlabel(f"Actual {name} [{units}]")
    plt.ylabel(f"Predicted {name} [{units}]")
    plt.title(f"{name} Linear Regression")

    # Metrics box
    metrics_text = (
        f"$R^2$ = {r2:.4f}\n"
        f"MAE = {mae:.4g}\n"
        f"RMSE = {rmse:.4g}"
    )

    plt.text(
        0.05,
        0.95,
        metrics_text,
        transform=plt.gca().transAxes,
        verticalalignment='top',
        bbox=dict(
            boxstyle='round',
            facecolor='white',
            alpha=0.8
        )
    )

    plt.tight_layout()
    plt.show()

parity_plot(
    y_msp_validation,
    y_pred_msp_validation,
    "MSP",
    "USD/kg"
)

parity_plot(
    y_irr_validation,
    y_pred_irr_validation,
    "IRR",
    "%"
)

parity_plot(
    y_npv_validation,
    y_pred_npv_validation,
    "NPV",
    "$"
)