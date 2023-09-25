from datetime import timedelta

import numpy as np
import pandas as pd
from statsmodels.tsa.api import STLForecast
from statsmodels.tsa.statespace.sarimax import SARIMAX

TRAIN_PERIOD = timedelta(weeks=4)
PREDICTION_PERIOD = pd.DateOffset(days=1)


class LoadForecaster:
    def __init__(self) -> None:
        self._order = (2, 1, 1)

    def predict(self, df: pd.DataFrame, exog_train: pd.DataFrame, exog_predict: pd.DataFrame) -> pd.DataFrame:
        df["mean_log"] = np.log(df["mean"])
        # df = df.tail(floor(TRAIN_PERIOD.total_seconds() / 3600))
        model = STLForecast(
            df["mean_log"],
            SARIMAX,
            model_kwargs={
                "order": self._order,
                "enforce_invertibility": False,
                "enforce_stationarity": False,
                "exog": exog_train,
            },
        )
        results = model.fit(fit_kwargs={"disp": False, "warn_convergence": False})
        model_prediction = results.get_prediction(
            start=df.iloc[-1].name + pd.DateOffset(hours=1),
            end=df.iloc[-1].name + PREDICTION_PERIOD,  # type: ignore
            exog=exog_predict,
        )
        predicted_mean: pd.DataFrame = np.exp(model_prediction.predicted_mean.rename("predicted").to_frame())
        confidence_interval: pd.DataFrame = np.exp(
            model_prediction.conf_int(alpha=0.5).rename(
                columns={"upper": "predicted_upper", "lower": "predicted_lower"}
            )
        )
        prediction = predicted_mean.combine_first(confidence_interval)
        return prediction
