import random
from dataclasses import dataclass
from math import floor
from typing import Sequence

from matplotlib import pyplot as plt  # type: ignore


@dataclass
class Action:
    charge: bool
    min_soc: float
    max_soc: float

    def clone(self) -> "Action":
        return Action(self.charge, self.min_soc, self.max_soc)

    def make_hash(self) -> int:
        return hash((self.charge, self.min_soc, self.max_soc))

    def __repr__(self) -> str:
        return f"Action({self.charge}, {self.min_soc}, {self.max_soc})"


@dataclass
class TimeSegment:
    generation: float
    consumption: float
    feed_in_tariff: float
    import_tariff: float


SEGMENT_LENGTH_HOURS = 1
BATTERY_CAPACITY = 4.2
BATTERY_CHARGE_AMOUNT_PER_SEGMENT = 3 * SEGMENT_LENGTH_HOURS
EXPORT_LIMIT_PER_SEGMENT = 9999
AC_TO_DC_EFFICIENCY = 0.95
DC_TO_AC_EFFICIENCY = 0.8
EXPORT_LIMIT_PER_SEGMENT_DC = EXPORT_LIMIT_PER_SEGMENT / DC_TO_AC_EFFICIENCY

# Lowest that we can choose to discharge the battery to
MIN_SOC_PERMITTED_PERCENT = 20
SOC_STEP_PERCENT = 20

OPTIMIZATION_MIN_SOC_PERCENT = 10
OPTIMIZATION_SOC_STEP_PERCENT = 10

INITIAL_ACTION = Action(charge=False, min_soc=MIN_SOC_PERMITTED_PERCENT / 100, max_soc=1.0)


class BatteryModel:
    def __init__(self) -> None:
        self.debug = False
        self.num_runs = 0

    def run(
        self, segments: list[TimeSegment], actions: Sequence[Action | None], initial_battery: float, debug: bool = False
    ) -> float:
        self.num_runs += 1
        battery_level = initial_battery
        feed_in_cost = 0.0
        import_cost = 0.0
        action = INITIAL_ACTION

        # Debug
        battery_levels = []
        imports = []
        exports = []

        for segment, action_change in zip(segments, actions, strict=True):
            if action_change is not None:
                action = action_change
            solar_to_battery = 0.0
            solar_to_grid = 0.0
            battery_to_load = 0.0
            grid_to_load = 0.0
            grid_to_battery_dc = 0.0

            if action.charge:
                # I don't actually know, but... I assume that solar replaces grid up to the charge rate
                solar_to_battery = max(0, min(BATTERY_CAPACITY * action.max_soc - battery_level, segment.generation))
                grid_to_battery_dc = max(
                    0,
                    min(
                        BATTERY_CAPACITY * action.max_soc - battery_level - solar_to_battery,
                        BATTERY_CHARGE_AMOUNT_PER_SEGMENT,
                    ),
                )
                excess_solar_ac = (segment.generation - solar_to_battery) * DC_TO_AC_EFFICIENCY
                # Doesn't consider inverter limits
                if excess_solar_ac > segment.consumption:
                    solar_to_grid = min(EXPORT_LIMIT_PER_SEGMENT, excess_solar_ac - segment.consumption)
                else:
                    grid_to_load = segment.consumption - excess_solar_ac
            else:
                # If generation can cover consumption, excess goes into battery. Else excess comes from battery if
                # available
                if segment.generation > segment.consumption / DC_TO_AC_EFFICIENCY:
                    excess_solar_dc = segment.generation - segment.consumption / DC_TO_AC_EFFICIENCY
                    solar_to_battery = max(0.0, min(BATTERY_CAPACITY * action.max_soc - battery_level, excess_solar_dc))
                    solar_to_grid = (
                        min(EXPORT_LIMIT_PER_SEGMENT_DC, excess_solar_dc - solar_to_battery) * DC_TO_AC_EFFICIENCY
                    )
                else:
                    required_energy_ac = segment.consumption - segment.generation * DC_TO_AC_EFFICIENCY
                    battery_to_load = max(
                        0.0,
                        min(
                            battery_level - BATTERY_CAPACITY * action.min_soc, required_energy_ac / DC_TO_AC_EFFICIENCY
                        ),
                    )
                    grid_to_load = required_energy_ac - battery_to_load * DC_TO_AC_EFFICIENCY

            battery_change = solar_to_battery + grid_to_battery_dc - battery_to_load
            battery_level += battery_change
            assert battery_level >= 0

            feed_in_cost += solar_to_grid * segment.feed_in_tariff
            import_cost += (grid_to_load + grid_to_battery_dc / AC_TO_DC_EFFICIENCY) * segment.import_tariff

            if debug:
                imports.append(grid_to_load + grid_to_battery_dc / AC_TO_DC_EFFICIENCY)
                exports.append(solar_to_grid)
                battery_levels.append(battery_level)

        score = round(feed_in_cost, 2) - round(import_cost, 2)

        if debug:
            size = len(battery_levels)
            print(f"Feed-in: {feed_in_cost}; import: {import_cost}; total: {score}")
            plt.plot(range(0, size), battery_levels, marker="o", label="batt")
            plt.plot(range(0, size), [x.consumption for x in segments], marker="x", label="cons")
            plt.plot(range(0, size), [x.generation for x in segments], marker="+", label="gen")
            plt.plot(range(0, size), imports, marker="<", label="gen")
            plt.plot(range(0, size), exports, marker=">", label="gen")
            plt.fill_between(
                range(0, size),
                [None if x is None else x.min_soc * BATTERY_CAPACITY - 0.05 for x in actions],
                [None if x is None else x.max_soc * BATTERY_CAPACITY + 0.05 for x in actions],
                step="mid",
                alpha=0.1,
            )
            plt.show()

        # Round to avoid floating-point error saying that one result is better than another, when in fact they're the
        # same
        return score

    def create_hash(self, actions: list[Action | None]) -> int:
        prev_action_hash = INITIAL_ACTION.make_hash()
        h = 0
        for action in actions:
            this_hash = prev_action_hash if action is None else action.make_hash()
            h = hash((h, this_hash))
        return h

    def shotgun_hillclimb(self, segments: list[TimeSegment], initial_battery: float) -> list[Action]:
        def is_better(x: float, y: float, margin: float = 0.0) -> bool:
            if abs(x - y) < margin:
                return False
            return x > y

        visited_actions_hashes = set()
        charge_set = [False, True]
        best_result_ever: float | None = None
        best_actions_ever: list[Action] = []
        slots = list(range(len(segments)))
        for _ in range(20):
            # Keeping a fair number of "Do last action" seems to make it easier for it to find solutions which only work
            # if you consistently do the same thing a lot.
            actions: list[Action | None] = [None] * len(segments)
            # I've noticed that just seeding the first 24 hours works well: it speeds things up, without compromising
            # the quality of the first 24 hours. Of course the second 24 hours suffers, but we don't care about that
            # really.
            for _ in range(floor(24 * 0.5)):  # Seeding about half seems to work well
                charge = random.choice(charge_set)
                # No point having a min soc when charging
                min_soc_percent = (
                    MIN_SOC_PERMITTED_PERCENT
                    if charge
                    else random.randrange(MIN_SOC_PERMITTED_PERCENT, 101, SOC_STEP_PERCENT)
                )
                actions[random.randint(0, 24)] = Action(
                    charge,
                    min_soc=min_soc_percent / 100.0,
                    max_soc=random.randrange(min_soc_percent, 101, SOC_STEP_PERCENT) / 100.0,
                )
            best_actions = actions.copy()
            best_result = self.run(segments, actions, initial_battery)
            while True:
                found_better = False
                # We evaluate each of the possible changes, and see which one has the greatest effect
                best_improved_result = best_result
                best_improved_actions: list[Action | None] | None = None
                # Shuffling these means we choose a random action from those with the best score
                random.shuffle(slots)
                for slot in slots:
                    old_action = actions[slot]
                    if actions[slot] is None:
                        actions[slot] = Action(
                            charge=False, min_soc=MIN_SOC_PERMITTED_PERCENT / 100, max_soc=1.0
                        )  # All these properties are going to be overridden shortly
                    else:
                        actions[slot] = actions[slot].clone()  # type: ignore
                    action = actions[slot]
                    assert action is not None
                    for new_charge in charge_set:
                        action.charge = new_charge
                        for new_min_soc_percent in (
                            [MIN_SOC_PERMITTED_PERCENT]
                            if new_charge
                            or segments[slot].generation > segments[slot].consumption / DC_TO_AC_EFFICIENCY
                            else range(MIN_SOC_PERMITTED_PERCENT, 101, SOC_STEP_PERCENT)
                        ):
                            action.min_soc = new_min_soc_percent / 100
                            for new_max_soc_percent in (
                                range(new_min_soc_percent, 101, SOC_STEP_PERCENT)
                                if new_charge
                                or segments[slot].generation > segments[slot].consumption / DC_TO_AC_EFFICIENCY
                                else [100]
                            ):
                                action.max_soc = new_max_soc_percent / 100
                                new_result = self.run(segments, actions, initial_battery)
                                if is_better(new_result, best_improved_result):
                                    found_better = True
                                    best_improved_result = new_result
                                    best_improved_actions = actions.copy()
                                    # Since we're going to be further mutating this action, we need to clone it now
                                    action = actions[slot] = action.clone()
                    actions[slot] = old_action

                actions_hash = self.create_hash(actions)
                if actions_hash in visited_actions_hashes:
                    break
                visited_actions_hashes.add(actions_hash)

                if found_better:
                    # Did we find an improvement? Keep going
                    best_result = best_improved_result
                    best_actions = actions = best_improved_actions  # type: ignore
                else:
                    # No? We've reached a local maximum
                    break
            if best_result_ever is None or is_better(best_result, best_result_ever):
                best_result_ever = best_result
                best_actions_ever = best_actions  # type: ignore

        # Also get rid of Nones

        old_action = INITIAL_ACTION
        for slot in range(len(actions)):
            if best_actions_ever[slot] is None:
                # We're going to be mutating these, so we need to clone them
                best_actions_ever[slot] = old_action.clone()
            else:
                old_action = best_actions_ever[slot]

        # for i, action in enumerate(best_actions_ever):
        #     print(f"{i}: {action}")
        # print(score_result(best_result_ever))
        # run(segments, best_actions_ever, initial_battery, debug=True)
        # best_actions_ever[10] = Action(ActionType.SELF_USE, 0.1, 1.0)
        # # # # # best_actions_ever[3] = Action(ActionType.SELF_USE, 1.0, 1.0)
        # for i, action in enumerate(best_actions_ever):
        #     print(f"{i}: {action}")
        # best_result_ever = self.run(segments, best_actions_ever, initial_battery, debug=True)
        # print(best_result_ever)

        assert best_actions_ever is not None
        assert best_result_ever is not None
        print(repr(best_actions_ever))

        # Ty and simplify: if changing a slot to a "lower" action doesn't hurt the score, do it

        # TODO: Use 24 rather than len(actions) below? Do we really care about optimizing beyond 24h?

        # When seeing if a new result is better, use a margin of 1p. That way something which is neater but a tiny bit
        # worse can still be selected
        margin = 1.0

        for slot in range(len(actions)):
            old_action = best_actions_ever[slot]

            copied_another_action = False

            # If we can make it the same as the previous action, do that
            if not copied_another_action and slot > 0:
                best_actions_ever[slot] = best_actions_ever[slot - 1].clone()
                new_result = self.run(segments, best_actions_ever, initial_battery)
                if not is_better(best_result_ever, new_result, margin=margin):
                    copied_another_action = True
                else:
                    best_actions_ever[slot] = old_action

            # Try and disable charging
            if not copied_another_action and best_actions_ever[slot].charge:
                best_actions_ever[slot].charge = False
                new_result = self.run(segments, best_actions_ever, initial_battery)
                # If the old result was better, go back to it and continue. Otherwise go for the new result
                if not is_better(best_result_ever, new_result, margin=margin):
                    break
                # assert(new_score < best_score_ever)
                best_actions_ever[slot].charge = True

        # The step above will have removed any unnecessary charge periods (which do pop up, as a means to prevent
        # discharge). However, we do want charge periods to extend backwards as far as possible. If we have a 3-hour
        # cheap period say, we want the charge period to extend across all of it
        ends_of_charge_periods = [
            i
            for i in range(1, len(actions))
            if best_actions_ever[i].charge and (i == len(actions) - 1 or not best_actions_ever[i + 1].charge)
        ]
        for end_of_charge_period in ends_of_charge_periods:
            for candidate in range(end_of_charge_period - 1, -1, -1):
                if best_actions_ever[candidate].charge:
                    continue
                prev_action = best_actions_ever[candidate]
                best_actions_ever[candidate] = best_actions_ever[end_of_charge_period].clone()
                new_result = self.run(segments, best_actions_ever, initial_battery)
                if is_better(best_result_ever, new_result, margin=margin):
                    best_actions_ever[candidate] = prev_action
                    break

        for i, action in enumerate(best_actions_ever):
            print(f"{i}: {action}")
        best_result_ever = self.run(segments, best_actions_ever, initial_battery, debug=True)
        print(best_result_ever)

        # Now that we've got the charge periods in place, try and optimize the min/max socs
        # This time we can lower it to 10%. We didn't want to do that during planning to as to leave a margin.
        for slot in range(len(actions)):
            # Introduce a shock -- a large consumption for this slot. This gives us a way of tuning the min soc so
            # as to prevent excessive discharge in this case (e.g. to tide us through an expensive period).

            if best_actions_ever[slot].charge:
                prev_consumption = segments[slot].consumption
                prev_generation = segments[slot].generation
                # This needs to be large enough to drain the battery
                segments[slot].consumption = BATTERY_CAPACITY
                segments[slot].generation = 0

                test_result = self.run(segments, best_actions_ever, initial_battery)

                best_min_soc = best_actions_ever[slot].min_soc
                for min_soc_percent in range(OPTIMIZATION_MIN_SOC_PERCENT, 101, OPTIMIZATION_SOC_STEP_PERCENT):
                    min_soc = min_soc_percent / 100
                    best_actions_ever[slot].min_soc = min_soc
                    new_result = self.run(segments, best_actions_ever, initial_battery)
                    if is_better(new_result, test_result, margin=margin):
                        test_result = new_result
                        best_min_soc = min_soc
                best_actions_ever[slot].min_soc = best_min_soc

                segments[slot].consumption = prev_consumption
                segments[slot].generation = prev_generation
                # Reducing the min allowable min_soc can improve the score, particularly past the 24h point, as it's
                # able to drain the battery further
                best_result_ever = self.run(segments, best_actions_ever, initial_battery)
            else:
                # For charge periods, just set min soc to the min
                best_actions_ever[slot].min_soc = OPTIMIZATION_MIN_SOC_PERCENT / 100

            # We want to try the max and min before anything in between. If we're just charging normally it
            # should be 1.0, if we're using it to prevent discharge it should be min_soc, and more specialised cases
            # take intermediate values.
            # We also want to apply shocks here. For example if we've got an hour during a Flux peak period where the
            # generation < consumption, the model won't see any reason to impose a max soc to stop the battery from
            # charging. Applying a shock generation ensures that this limit is put in place.
            # Else, if this is a charge period, just make it as high as it can be.
            if best_actions_ever[slot].charge:
                prev_max_soc = best_actions_ever[slot].max_soc
                for max_soc_percent in range(100, round(prev_max_soc * 100), -SOC_STEP_PERCENT):
                    best_actions_ever[slot].max_soc = max_soc_percent / 100
                    new_result = self.run(segments, best_actions_ever, initial_battery)
                    if not is_better(best_result_ever, new_result, margin=margin):
                        break
                    best_actions_ever[slot].max_soc = prev_max_soc
            else:
                prev_generation = segments[slot].generation
                # Don't do this if it's night
                segments[slot].generation = (
                    BATTERY_CAPACITY + segments[slot].consumption if segments[slot].generation > 0 else 0
                )

                test_result = self.run(segments, best_actions_ever, initial_battery)

                best_max_soc = best_actions_ever[slot].max_soc
                # We prefer a max soc of 1.0 (normal operation) or 0.1 (prevent charge) before other values.
                min_soc_percent = round(best_actions_ever[slot].min_soc * 100)
                max_soc_percents = [
                    *range(min_soc_percent + OPTIMIZATION_SOC_STEP_PERCENT, 100, OPTIMIZATION_SOC_STEP_PERCENT),
                    min_soc_percent,
                    100,
                ]
                for max_soc_percent in max_soc_percents:
                    max_soc = max_soc_percent / 100
                    best_actions_ever[slot].max_soc = max_soc
                    new_result = self.run(segments, best_actions_ever, initial_battery)
                    # Allow socs which result in the same score as the model to be used in preference
                    if not is_better(test_result, new_result, margin=margin):
                        test_result = new_result
                        best_max_soc = max_soc
                best_actions_ever[slot].max_soc = best_max_soc
                segments[slot].generation = prev_generation
                best_result_ever = self.run(segments, best_actions_ever, initial_battery)

        if self.debug:
            for i, action in enumerate(best_actions_ever[:24]):
                print(f"{i}: {action}")

            self.run(segments[:24], best_actions_ever[:24], initial_battery, debug=True)

            print(f"Number of runs: {self.num_runs}")

        return best_actions_ever[:24]
