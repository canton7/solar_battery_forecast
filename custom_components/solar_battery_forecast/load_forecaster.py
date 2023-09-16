from math import floor

import numpy as np
import pandas as pd
from statsmodels.tsa.api import STLForecast
from statsmodels.tsa.statespace.sarimax import SARIMAX

TRAIN_PERIOD = pd.Timedelta(weeks=4)
PREDICTION_PERIOD = pd.DateOffset(days=2)


class LoadForecaster:
    def __init__(self) -> None:
        self._order = (2, 1, 1)

    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.asfreq(freq="H", method="pad").tail(floor(TRAIN_PERIOD.total_seconds() / 3600))
        df["mean_log"] = np.log(df["mean"])
        model = STLForecast(
            df["mean_log"],
            SARIMAX,
            model_kwargs={"order": self._order, "enforce_invertibility": False, "enforce_stationarity": False},
        )
        results = model.fit(fit_kwargs={"disp": False, "warn_convergence": False})
        model_prediction = results.get_prediction(
            start=df.iloc[-1].name + pd.DateOffset(hours=1), end=df.iloc[-1].name + PREDICTION_PERIOD  # type: ignore
        )
        predicted_mean: pd.DataFrame = np.exp(model_prediction.predicted_mean.rename("predicted").to_frame())
        confidence_interval: pd.DataFrame = np.exp(
            model_prediction.conf_int(alpha=0.5).rename(
                columns={"upper": "predicted_upper", "lower": "predicted_lower"}
            )
        )
        prediction = predicted_mean.combine_first(confidence_interval)
        return prediction
