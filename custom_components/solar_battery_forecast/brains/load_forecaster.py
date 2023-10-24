import logging
from datetime import timedelta
from math import floor

import numpy as np
import pandas as pd
from statsmodels.tsa.api import STLForecast
from statsmodels.tsa.statespace.sarimax import SARIMAX

TRAIN_PERIOD = timedelta(weeks=4)
PREDICTION_PERIOD = timedelta(days=2)  # TODO: This is strongly tied to the implementation of BatteryModel currently

_LOGGER = logging.getLogger(__name__)


class LoadForecaster:
    def __init__(self) -> None:
        self._order = (2, 1, 1)

    def predict(self, df: pd.DataFrame) -> pd.DataFrame | None:
        if len(df) < 24:
            _LOGGER.warning(f"Unable to provide a forecast for {len(df)} hours of data. Please wait")
            return None

        # Even a few missing values are enough to make it return solid NaNs for the forecast
        df["value"] = df["value"].interpolate()
        df["value_log"] = np.log(df["value"])
        df = df.tail(floor(TRAIN_PERIOD.total_seconds() / 3600))
        model = STLForecast(
            df["value_log"],
            SARIMAX,
            model_kwargs={"order": self._order, "enforce_invertibility": False, "enforce_stationarity": False},
        )
        results = model.fit(fit_kwargs={"disp": False, "warn_convergence": False})
        model_prediction = results.get_prediction(
            start=df.iloc[-1].name + pd.DateOffset(hours=1), end=df.iloc[-1].name + PREDICTION_PERIOD  # type: ignore
        )
        predicted_value: pd.DataFrame = np.exp(model_prediction.predicted_mean.rename("predicted").to_frame())
        confidence_interval: pd.DataFrame = np.exp(
            model_prediction.conf_int(alpha=0.5).rename(
                columns={"upper": "predicted_upper", "lower": "predicted_lower"}
            )
        )
        prediction = predicted_value.combine_first(confidence_interval)
        return prediction
