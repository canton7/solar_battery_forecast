import pandas as pd
from matplotlib import pyplot
from pandas.plotting import autocorrelation_plot
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.arima.model import ARIMA
import statsmodels
import statsmodels.api as sm
from statsmodels.graphics.tsaplots import plot_acf
import numpy as np
from statsmodels.graphics.tsaplots import plot_predict

df = pd.read_csv('entities-2023-09-02_17 33 41.csv', usecols=['start', 'mean'])
df['start'] = pd.to_datetime(df['start'], format='%Y-%m-%d %H:%M:%S')
df['dow'] = df['start'].dt.dayofweek
df = df.set_index('start')
df = df.asfreq(freq='H')
df = df[['mean', 'dow']].head(4*7*24)

from skforecast.model_selection_sarimax import grid_search_sarimax
from skforecast.ForecasterSarimax import ForecasterSarimax
from pmdarima import ARIMA
from sklearn.utils import parallel_backend

forecaster = ForecasterSarimax(
                 regressor=ARIMA(order=(1, 1, 1), seasonal_order=(1, 1, 1, 24), maxiter=200),
             )

orders = []
seasonal_orders = []
for p in [0, 1, 2]:
    for d in [0, 1, 2]:
        for q in [0, 1, 2]:
            orders.append((p, d, q))

for p in [0, 1, 2]:
    for d in [0, 1, 2]:
        for q in [0, 1, 2]:
            seasonal_orders.append((p, d, q, 24))

param_grid = {
    'order': orders,
    'seasonal_order': seasonal_orders,
    # 'trend': [None]
}

results_grid = grid_search_sarimax(
                forecaster         = forecaster,
                y                  = df['mean'],
                exog               = df['dow'],
                param_grid         = param_grid,
                steps              = 24,
                refit              = False,
                metric             = 'mean_absolute_error',
                initial_train_size = 24*7*3,
                fixed_train_size   = False,
                return_best        = True,
                n_jobs             = -1,
                verbose            = False,
                show_progress      = True
            )

results_grid.head(10)
