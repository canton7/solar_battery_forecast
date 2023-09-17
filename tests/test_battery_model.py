import random

from custom_components.solar_battery_forecast.brains.battery_model import Action
from custom_components.solar_battery_forecast.brains.battery_model import ActionType
from custom_components.solar_battery_forecast.brains.battery_model import BatteryModel
from custom_components.solar_battery_forecast.brains.battery_model import TimeSegment


def test_flux() -> None:
    consumption = [
        0.2,
        0.4,
        0.2,
        0.2,
        0.2,
        0.31,
        0.25,
        0.41,
        0.32,
        0.32,
        0.29,
        0.4,
        0.57,
        0.53,
        0.82,
        0.32,
        0.32,
        0.22,
        0.11,
        0.45,
        0.2,
        0.1,
        0.2,
        0.2,
    ]
    generation = [
        0,
        0,
        0,
        0,
        0,
        0,
        0.05,
        0.15,
        0.72,
        2.04,
        2.33,
        2.27,
        2.35,
        2.1,
        1.94,
        1.26,
        0.75,
        1.26,
        0.11,
        0.06,
        0,
        0,
        0,
        0,
    ]
    import_tariff = [30.72] * 2 + [18.43] * 3 + [30.72] * 11 + [43.01] * 3 + [30.72] * 5
    feed_in_tariff = [19.72] * 2 + [7.43] * 3 + [19.72] * 11 + [32.01] * 3 + [19.72] * 5

    result = run(consumption, generation, import_tariff, feed_in_tariff)
    expected = [
        Action(ActionType.SELF_USE, 0.2, 1.0),
        Action(ActionType.SELF_USE, 0.2, 1.0),
        Action(ActionType.CHARGE, 0.2, 0.4),
        Action(ActionType.CHARGE, 0.2, 0.4),
        Action(ActionType.CHARGE, 0.2, 0.4),
        Action(ActionType.SELF_USE, 0.2, 1.0),
        Action(ActionType.SELF_USE, 0.2, 1.0),
        Action(ActionType.SELF_USE, 0.2, 1.0),
        Action(ActionType.SELF_USE, 0.2, 1.0),
        Action(ActionType.SELF_USE, 0.2, 1.0),
        Action(ActionType.SELF_USE, 0.2, 1.0),
        Action(ActionType.SELF_USE, 0.2, 1.0),
        Action(ActionType.SELF_USE, 0.2, 1.0),
        Action(ActionType.SELF_USE, 0.2, 1.0),
        Action(ActionType.SELF_USE, 0.2, 1.0),
        Action(ActionType.SELF_USE, 0.2, 1.0),
        Action(ActionType.SELF_USE, 0.2, 1.0),
        Action(ActionType.SELF_USE, 0.2, 1.0),
        Action(ActionType.SELF_USE, 0.2, 1.0),
        Action(ActionType.SELF_USE, 0.2, 1.0),
        Action(ActionType.SELF_USE, 0.2, 1.0),
        Action(ActionType.SELF_USE, 0.2, 1.0),
        Action(ActionType.SELF_USE, 0.2, 1.0),
        Action(ActionType.SELF_USE, 0.2, 1.0),
    ]
    assert result == expected


def run(
    consumption: list[float], generation: list[float], import_tariff: list[float], feed_in_tariff: list[float]
) -> list[Action]:
    seed = random.randrange(2**32)
    random.seed(seed)
    print(f"Seed: {seed}")
    model = BatteryModel()
    model.debug = True
    segments = [
        TimeSegment(generation=g, consumption=c, feed_in_tariff=f, import_tariff=i)
        for g, c, f, i in zip(generation, consumption, feed_in_tariff, import_tariff, strict=True)
    ]
    segments = segments + segments
    result = model.shotgun_hillclimb(segments, 2)
    return result
