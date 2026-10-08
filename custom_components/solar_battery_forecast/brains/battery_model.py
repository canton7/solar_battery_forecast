import math
from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from typing import Iterable
from typing import Sequence


class ActionType(Enum):
    SELF_USE = 0
    CHARGE = 1
    DISCHARGE = 2


@dataclass
class Action:
    action_type: ActionType
    min_soc: float
    max_soc: float

    def clone(self) -> "Action":
        return Action(self.action_type, self.min_soc, self.max_soc)

    def __repr__(self) -> str:
        return f"Action({self.action_type}, {self.min_soc}, {self.max_soc})"


@dataclass
class TimeSegment:
    generation: float
    consumption: float
    feed_in_tariff: float
    import_tariff: float


DISCHARGE_DISINCENTIVE = 2

SEGMENT_LENGTH_HOURS = 1
BATTERY_CAPACITY = 4.2

AC_TO_DC_EFFICIENCY = 0.95
DC_TO_AC_EFFICIENCY = 0.95

INVERTER_POWER_PER_SEGMENT = 3 * SEGMENT_LENGTH_HOURS

# TODO: These are currently unused
EXPORT_LIMIT_PER_SEGMENT = 9999
EXPORT_LIMIT_PER_SEGMENT_DC = EXPORT_LIMIT_PER_SEGMENT / DC_TO_AC_EFFICIENCY

# Lowest that we can choose to discharge the battery to
MIN_SOC_PERMITTED_PERCENT = 20
SOC_STEP_PERCENT = 20

OPTIMIZATION_MIN_SOC_PERCENT = 10
OPTIMIZATION_SOC_STEP_PERCENT = 10

# When seeing if a new result is better, use a margin of 1p. That way something which is neater but a tiny bit
# worse can still be selected
MARGIN = 1.0


@dataclass(slots=True)
class RunOutputSegment:
    battery_kwh: float
    battery_soc_fraction: float
    feed_in_kwh: float
    import_kwh: float
    feed_in_cost: float
    import_cost: float
    cumulative_score: float


@dataclass(slots=True)
class RunOutput:
    segments: list[RunOutputSegment] = field(default_factory=list)


@dataclass(slots=True)
class IncrementalState:
    cumulative_score: float
    battery_soc_fraction: float
    actions: list[Action]


class BatteryModel:
    def __init__(self, initial_battery_kwh: float, debug: bool = False) -> None:
        self.num_runs = 0
        self._initial_battery_kwh = initial_battery_kwh
        self._debug = debug

    def plot(self, segments: list[TimeSegment], actions: Sequence[Action]) -> None:
        if not self._debug:
            return

        from matplotlib import pyplot as plt

        output = RunOutput()
        self.run(segments, actions, output)

        size = len(output.segments)
        print(f"total: {output.segments[-1].cumulative_score}")
        plt.plot(range(size), [x.battery_kwh for x in output.segments], marker="o", label="batt")
        plt.plot(range(size), [x.consumption for x in segments], marker="x", label="cons")
        plt.plot(range(size), [x.generation for x in segments], marker="+", label="gen")
        plt.plot(range(size), [x.import_kwh for x in output.segments], marker="<", label="gen")
        plt.plot(range(size), [x.feed_in_kwh for x in output.segments], marker=">", label="gen")
        plt.fill_between(
            range(size),
            [0 if x is None else x.min_soc * BATTERY_CAPACITY - 0.05 for x in actions],
            [0 if x is None else x.max_soc * BATTERY_CAPACITY + 0.05 for x in actions],
            step="mid",
            alpha=0.1,
        )
        plt.show()

    def run(
        self,
        segments: Sequence[TimeSegment],
        actions: Sequence[Action],
        outputs: RunOutput | None = None,
    ) -> float:
        self.num_runs += 1
        battery_soc_fraction = self._initial_battery_kwh / BATTERY_CAPACITY
        total_score = 0.0

        for segment, action in zip(segments, actions, strict=True):
            segment_result = self._run_one_segment(battery_soc_fraction, segment, action, total_score)
            total_score = segment_result.cumulative_score
            battery_soc_fraction = segment_result.battery_soc_fraction

            if outputs is not None:
                outputs.segments.append(segment_result)

        # Round to avoid floating-point error saying that one result is better than another, when in fact they're the
        # same
        return round(total_score, 2)

    def _run_one_segment(
        self,
        battery_soc_fraction: float,
        segment: TimeSegment,
        action: Action,
        input_score: float,
    ) -> RunOutputSegment:
        def clamp(val: float, upper: float) -> float:
            if val < 0 or upper < 0:
                return 0
            if val > upper:
                return upper
            return val

        battery_kwh = battery_soc_fraction * BATTERY_CAPACITY
        battery_discharge = 0.0
        inverter_output_ac = 0.0

        if action.action_type == ActionType.SELF_USE:
            # If generation can cover consumption, excess goes into battery. Else excess comes from battery if
            # available
            if segment.generation > segment.consumption / DC_TO_AC_EFFICIENCY:
                # Generation covers consumption: charge the battery and then export the rest
                excess_solar_dc = segment.generation - segment.consumption / DC_TO_AC_EFFICIENCY
                battery_discharge = -clamp(excess_solar_dc, BATTERY_CAPACITY * action.max_soc - battery_kwh)
                # TODO: Export limit
                inverter_output_ac = segment.consumption + (excess_solar_dc + battery_discharge) * DC_TO_AC_EFFICIENCY
            else:
                # Generation doesn't cover consumption: output all generation + some battery
                required_energy_dc = segment.consumption / DC_TO_AC_EFFICIENCY - segment.generation
                battery_discharge = clamp(required_energy_dc, battery_kwh - BATTERY_CAPACITY * action.min_soc)
                inverter_output_ac = (segment.generation + battery_discharge) * DC_TO_AC_EFFICIENCY

        elif action.action_type == ActionType.CHARGE:
            # Solar goes to the battery if available
            solar_to_battery = clamp(segment.generation, BATTERY_CAPACITY * action.max_soc - battery_kwh)
            if solar_to_battery == segment.generation:
                # Any remaining charge comes through the inverter
                inverter_to_battery_dc = clamp(
                    INVERTER_POWER_PER_SEGMENT / AC_TO_DC_EFFICIENCY,
                    BATTERY_CAPACITY * action.max_soc - battery_kwh - solar_to_battery,
                )
                inverter_output_ac = -inverter_to_battery_dc * AC_TO_DC_EFFICIENCY
            else:
                # Any excess solar is output from the inverter
                inverter_to_battery_dc = 0
                inverter_output_ac = (segment.generation - solar_to_battery) * DC_TO_AC_EFFICIENCY
            battery_discharge = -(solar_to_battery + inverter_to_battery_dc)

        elif action.action_type == ActionType.DISCHARGE:
            # The inverter exports at the set rate, using as much solar as possible, and the rest from battery.
            # Load is taken from the exported energy, with the rest going to the grid
            # TODO: Max export rate
            inverter_max_export_dc = INVERTER_POWER_PER_SEGMENT / DC_TO_AC_EFFICIENCY
            solar_to_inverter_export = min(segment.generation, inverter_max_export_dc)
            # The battery dischages to make up the gap if possible. Any excess generation goes into the battery
            if inverter_max_export_dc > solar_to_inverter_export:
                battery_discharge = clamp(
                    inverter_max_export_dc - solar_to_inverter_export,
                    battery_kwh - BATTERY_CAPACITY * action.min_soc,
                )
            else:
                battery_discharge = -clamp(
                    solar_to_inverter_export - inverter_max_export_dc,
                    BATTERY_CAPACITY * action.max_soc - battery_kwh,
                )
            inverter_output_ac = (solar_to_inverter_export + max(0, battery_discharge)) * DC_TO_AC_EFFICIENCY

        battery_kwh -= battery_discharge
        assert battery_kwh >= 0

        if inverter_output_ac > segment.consumption:
            feed_in_amount = inverter_output_ac - segment.consumption
            import_amount = 0.0
        else:
            feed_in_amount = 0.0
            import_amount = segment.consumption - inverter_output_ac

        this_feed_in_cost = max(0, feed_in_amount * (segment.feed_in_tariff - DISCHARGE_DISINCENTIVE))
        this_import_cost = import_amount * segment.import_tariff
        score = round(this_feed_in_cost, 2) - round(this_import_cost, 2)
        cumulative_score = round(input_score + score, 2)

        return RunOutputSegment(
            battery_kwh=round(battery_kwh, 2),
            battery_soc_fraction=round(battery_kwh / BATTERY_CAPACITY, 2),
            feed_in_kwh=round(feed_in_amount, 2),
            import_kwh=round(import_amount, 2),
            feed_in_cost=round(this_feed_in_cost, 2),
            import_cost=round(this_import_cost, 2),
            cumulative_score=cumulative_score,
        )

    def solve(self, segments: list[TimeSegment]) -> tuple[list[Action], RunOutput]:
        inputs: dict[float, IncrementalState] = {
            self._initial_battery_kwh / BATTERY_CAPACITY: IncrementalState(
                0, self._initial_battery_kwh / BATTERY_CAPACITY, []
            )
        }
        outputs: dict[float, IncrementalState] = {}

        for segment in segments:
            for _, segment_input in sorted(inputs.items(), key=lambda x: x[0], reverse=True):
                action = Action(ActionType.SELF_USE, 0, 0)
                for action_type in ActionType:
                    action.action_type = action_type

                    # min soc is used:
                    # - when charging, it isn't used
                    # - when in self use, to prevent discharge
                    # - when force discharging, to say what limit to force discharge to
                    new_min_soc_percents: Iterable[int]
                    if action_type == ActionType.CHARGE:
                        new_min_soc_percents = (MIN_SOC_PERMITTED_PERCENT,)
                    elif action_type == ActionType.SELF_USE:
                        new_min_soc_percents = (
                            (MIN_SOC_PERMITTED_PERCENT,)
                            if segment.generation > segment.consumption / DC_TO_AC_EFFICIENCY
                            else (100, MIN_SOC_PERMITTED_PERCENT)
                        )
                    elif action_type == ActionType.DISCHARGE:
                        # Don't allow a discharge down to 100%: the model tries to use it as a way to keep charge
                        new_min_soc_percents = range(MIN_SOC_PERMITTED_PERCENT, 99, SOC_STEP_PERCENT)

                    for new_min_soc_percent in new_min_soc_percents:
                        action.min_soc = new_min_soc_percent / 100
                        # max soc is used:
                        #  - when charging, to limit how much we pull from the grid
                        #  - when we're consuming solar, to leave space in the battery for e.g. a cheap charge
                        #    period in the future
                        #  - when discharging, unused
                        new_max_soc_percents: Iterable[int]
                        if action_type == ActionType.CHARGE:
                            new_max_soc_percents = range(100, new_min_soc_percent - 1, -SOC_STEP_PERCENT)
                        elif action_type == ActionType.SELF_USE:
                            new_max_soc_percents = (
                                (100, new_min_soc_percent)
                                if segment.generation > segment.consumption / DC_TO_AC_EFFICIENCY
                                else (100,)
                            )
                        elif action_type == ActionType.DISCHARGE:
                            new_max_soc_percents = (100,)

                        for new_max_soc_percent in new_max_soc_percents:
                            action.max_soc = new_max_soc_percent / 100

                            result = self._run_one_segment(
                                segment_input.battery_soc_fraction, segment, action, segment_input.cumulative_score
                            )
                            clamped_soc = round(result.battery_soc_fraction, 1)  # Clamp to nearest 10%

                            existing_state = outputs.get(clamped_soc)
                            if existing_state is None or self.is_better(
                                result.cumulative_score, existing_state.cumulative_score, margin=MARGIN
                            ):
                                outputs[clamped_soc] = IncrementalState(
                                    result.cumulative_score,
                                    result.battery_soc_fraction,
                                    [*segment_input.actions, action.clone()],
                                )

            inputs, outputs = outputs, inputs
            outputs.clear()

        best_actions = None
        best_score = -math.inf

        for input_state in inputs.values():
            # self.plot(segments, actions)
            if input_state.cumulative_score > best_score:
                best_actions = input_state.actions
                best_score = input_state.cumulative_score
        assert best_actions is not None

        self.plot(segments, best_actions)

        self.optimize_actions(segments, best_actions, best_score)

        self.plot(segments, best_actions)

        run_output = RunOutput()
        self.run(segments, best_actions, run_output)
        return best_actions[:24], run_output

    def is_better(self, x: float, y: float, margin: float = 0.0) -> bool:
        if abs(x - y) < margin:
            return False
        return x > y

    def optimize_actions(self, segments: Sequence[TimeSegment], actions: list[Action], result: float) -> float:
        # TODO: Use 24 rather than len(actions) below? Do we really care about optimizing beyond 24h?
        for slot in range(len(actions)):
            old_action = actions[slot]

            copied_another_action = False

            # If we can make it the same as the previous action, do that.
            # Don't do this for discharge: it tends to make the model extend the discharge beyond the end of a period
            # with good export rates, which negatively affects things later. For discharge, it's better if we can extend
            # it earlier.
            # TODO: We might want to try copying discharge actions forward in time? That would require passes in two
            # directions here.
            if (
                not copied_another_action
                and slot > 0
                and old_action != actions[slot - 1]
                and actions[slot - 1].action_type != ActionType.DISCHARGE
            ):
                actions[slot] = actions[slot - 1].clone()
                new_result = self.run(segments, actions)
                if not self.is_better(result, new_result, margin=MARGIN):
                    copied_another_action = True
                else:
                    actions[slot] = old_action

            # Try and disable charging
            # (discharging doesn't seem to need this)
            if not copied_another_action and actions[slot].action_type == ActionType.CHARGE:
                actions[slot] = actions[slot].clone()
                # A charge with a low max soc is sometimes used to limit charge (which we can replace with low min/max
                # soc) or discharge (replaced with high min/max soc)
                actions[slot].action_type = ActionType.SELF_USE
                actions[slot].max_soc = 1.0
                actions[slot].min_soc = 1.0
                new_result = self.run(segments, actions)
                # If the old result was better, go back to it and continue. Otherwise go for the new result
                if self.is_better(result, new_result, margin=MARGIN):
                    actions[slot].max_soc = MIN_SOC_PERMITTED_PERCENT / 100.0
                    actions[slot].min_soc = MIN_SOC_PERMITTED_PERCENT / 100.0
                    new_result = self.run(segments, actions)
                    if self.is_better(result, new_result, margin=MARGIN):
                        actions[slot] = old_action

        # The step above will have removed any unnecessary charge periods (which do pop up, as a means to prevent
        # discharge). However, we do want charge periods to extend backwards as far as possible. If we have a 3-hour
        # cheap period say, we want the charge period to extend across all of it.
        # The "copy last action" step above will already have extended it forwards
        ends_of_charge_periods = [
            i
            for i in range(1, len(actions))
            if actions[i].action_type == ActionType.CHARGE
            and (i == len(actions) - 1 or actions[i + 1].action_type != ActionType.CHARGE)
        ]
        for end_of_charge_period in ends_of_charge_periods:
            for candidate in range(end_of_charge_period - 1, -1, -1):
                if actions[candidate].action_type == ActionType.CHARGE:
                    continue
                prev_action = actions[candidate]
                actions[candidate] = actions[end_of_charge_period].clone()
                new_result = self.run(segments, actions)
                if self.is_better(result, new_result, margin=MARGIN):
                    actions[candidate] = prev_action
                    break

        # We want to move discharge periods as late as possible. This is so that there's a bit more of a buffer in case
        # load is higher than expected.
        # We've already extended the period as late as we can, so just try and chop off the start.
        start_of_discharge_periods = [
            i
            for i in range(len(actions))
            if actions[i].action_type == ActionType.DISCHARGE
            and (i == 0 or actions[i - 1].action_type != ActionType.DISCHARGE)
        ]
        for start_of_discharge_period in start_of_discharge_periods:
            for candidate in range(start_of_discharge_period, len(actions)):
                if actions[candidate].action_type != ActionType.DISCHARGE:
                    break
                prev_action = actions[candidate]
                actions[candidate] = actions[candidate].clone()
                # The closest we can get to discharge using self-use is a low min/max to prevent charge
                actions[candidate].action_type = ActionType.SELF_USE
                actions[candidate].min_soc = MIN_SOC_PERMITTED_PERCENT / 100.0
                actions[candidate].max_soc = MIN_SOC_PERMITTED_PERCENT / 100.0
                new_result = self.run(segments, actions)
                if self.is_better(result, new_result, margin=MARGIN):
                    actions[candidate] = prev_action
                    break

        # We might have made the result slightly worse. Re-calculate
        # (we don't do this as we go, to make sure that we never get more than MARGIN away from the original best case)
        result = self.run(segments, actions)

        # We may need to run this more than once
        while True:
            changed, result = self.optimize_min_max_soc(segments, actions, result, margin=MARGIN)
            if not changed:
                break

        return result

    def optimize_min_max_soc(
        self,
        segments: Sequence[TimeSegment],
        actions: Sequence[Action],
        best_result_ever: float,
        shock: bool = True,
        margin: float = 0.0,
    ) -> tuple[bool, float]:
        changed = False

        # Now that we've got the charge periods in place, try and optimize the min/max socs
        # This time we can lower it to 10%. We didn't want to do that during planning to as to leave a margin.

        # Do the non-charge slots before the charge slots. Otherwise we can have a situation where we fail to increase
        # a charge slot because an unnecessarily low max soc later on would stop the battery from charging from solar
        # later.
        for slot in range(len(actions)):
            # Introduce a shock -- a large consumption for this slot. This gives us a way of tuning the min soc so
            # as to prevent excessive discharge in this case (e.g. to tide us through an expensive period).

            prev_min_soc = actions[slot].min_soc
            if actions[slot].action_type == ActionType.CHARGE:
                # For charge periods, just set min soc to the min
                actions[slot].min_soc = OPTIMIZATION_MIN_SOC_PERCENT / 100
            else:
                prev_consumption = segments[slot].consumption
                prev_generation = segments[slot].generation

                # This needs to be large enough to drain the battery.
                # Don't do this for discharge: we're draining down to a min soc anyway, so this won't affect how much
                # the battery is drained. In practice, it just results in the model opting to drain the battery too far.
                if shock and actions[slot].action_type == ActionType.SELF_USE:
                    segments[slot].consumption = BATTERY_CAPACITY
                    segments[slot].generation = 0

                test_result = self.run(segments, actions)

                best_min_soc = actions[slot].min_soc
                # The model's pretty good at finding the min soc when discharging. Don't try and find one that's lower,
                # as this can result in over-zealous discharging.
                min_soc_percents = (
                    range(int(actions[slot].min_soc * 100), 101, OPTIMIZATION_SOC_STEP_PERCENT)
                    if actions[slot].action_type == ActionType.DISCHARGE
                    else range(OPTIMIZATION_MIN_SOC_PERCENT, 101, OPTIMIZATION_SOC_STEP_PERCENT)
                )
                for min_soc_percent in min_soc_percents:
                    min_soc = min_soc_percent / 100
                    actions[slot].min_soc = min_soc
                    new_result = self.run(segments, actions)
                    if self.is_better(new_result, test_result, margin=margin):
                        test_result = new_result
                        best_min_soc = min_soc

                changed = changed or prev_min_soc != best_min_soc

                actions[slot].min_soc = best_min_soc
                segments[slot].consumption = prev_consumption
                segments[slot].generation = prev_generation
                # Reducing the min allowable min_soc can improve the score, particularly past the 24h point, as it's
                # able to drain the battery further
                best_result_ever = self.run(segments, actions)

            # We want to try the max and min before anything in between. If we're just charging normally it
            # should be 1.0, if we're using it to prevent discharge it should be min_soc, and more specialised cases
            # take intermediate values.
            # We also want to apply shocks here. For example if we've got an hour during a Flux peak period where the
            # generation < consumption, the model won't see any reason to impose a max soc to stop the battery from
            # charging. Applying a shock generation ensures that this limit is put in place.
            # Else, if this is a charge period, just make it as high as it can be.
            if actions[slot].action_type == ActionType.DISCHARGE:
                # For discharge periods, just set the max soc to the max
                actions[slot].max_soc = 1.0
            elif actions[slot].action_type == ActionType.SELF_USE:
                prev_max_soc = actions[slot].max_soc
                prev_generation = segments[slot].generation
                # Don't do this if it's night
                if shock and segments[slot].generation > 0:
                    segments[slot].generation = BATTERY_CAPACITY + segments[slot].consumption

                test_result = self.run(segments, actions)

                best_max_soc = actions[slot].max_soc
                # We prefer a max soc of 1.0 (normal operation) or 0.1 (prevent charge) before other values.
                min_soc_percent = round(actions[slot].min_soc * 100)
                max_soc_percents = [
                    *range(min_soc_percent + OPTIMIZATION_SOC_STEP_PERCENT, 100, OPTIMIZATION_SOC_STEP_PERCENT),
                    min_soc_percent,
                    100,
                ]
                for max_soc_percent in max_soc_percents:
                    max_soc = max_soc_percent / 100
                    actions[slot].max_soc = max_soc
                    new_result = self.run(segments, actions)
                    # Allow socs which result in the same score as the model to be used in preference
                    if not self.is_better(test_result, new_result, margin=margin):
                        test_result = new_result
                        best_max_soc = max_soc

                changed = changed or prev_max_soc != best_max_soc
                actions[slot].max_soc = best_max_soc
                segments[slot].generation = prev_generation
                best_result_ever = self.run(segments, actions)

        # When we optimize charge periods, we need to do all actions in a period at the same time,
        # otherwise there's no advantage in just reducing the soc of the first.
        # If the model has decided to have different parts of the charge period have different socs, then treat those
        # parts separately
        start_of_charge_periods = [
            i
            for i in range(len(actions))
            if actions[i].action_type == ActionType.CHARGE
            and (
                i == 0
                or actions[i - 1].action_type != ActionType.CHARGE
                or actions[i - 1].max_soc != actions[i].max_soc
            )
        ]
        for slot in start_of_charge_periods:
            prev_max_soc = actions[slot].max_soc
            actions_in_period = [actions[slot]]
            for i in range(slot + 1, len(actions)):
                if actions[i].action_type != ActionType.CHARGE or actions[slot].max_soc != prev_max_soc:
                    break
                actions_in_period.append(actions[i])

            # We might want to tune this up *or* down a bit, as we're now working with smaller step size.
            # Therefore just search the whole space for the best.
            best_max_soc = prev_max_soc
            for max_soc_percent in range(OPTIMIZATION_MIN_SOC_PERCENT, 101, OPTIMIZATION_SOC_STEP_PERCENT):
                max_soc = max_soc_percent / 100
                for action in actions_in_period:
                    action.max_soc = max_soc

                new_result = self.run(segments, actions)
                if self.is_better(new_result, best_result_ever, margin=margin):
                    best_result_ever = new_result
                    best_max_soc = max_soc

            for action in actions_in_period:
                action.max_soc = best_max_soc

            changed = changed or best_max_soc != prev_max_soc

        return (changed, best_result_ever)
