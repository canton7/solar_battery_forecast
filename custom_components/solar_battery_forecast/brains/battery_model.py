import random
from dataclasses import dataclass
from dataclasses import field
from typing import Iterable
from typing import Sequence


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

# When seeing if a new result is better, use a margin of 1p. That way something which is neater but a tiny bit
# worse can still be selected
MARGIN = 1.0

INITIAL_ACTION = Action(charge=False, min_soc=MIN_SOC_PERMITTED_PERCENT / 100, max_soc=1.0)


@dataclass
class RunOutputSegment:
    battery_level: float
    battery_soc: float
    feed_in_kwh: float
    import_kwh: float
    feed_in_cost: float
    cumulative_feed_in_cost: float
    import_cost: float
    cumulative_import_cost: float
    cumulative_score: float


@dataclass
class RunOutput:
    segments: list[RunOutputSegment] = field(default_factory=list)


class BatteryModel:
    def __init__(self, initial_battery: float, debug: bool = False) -> None:
        self.num_runs = 0
        self._initial_battery = initial_battery
        self._debug = debug

    def plot(self, segments: list[TimeSegment], actions: Sequence[Action | None]) -> None:
        from matplotlib import pyplot as plt  # type: ignore

        output = RunOutput()
        self.run(segments, actions, output)

        size = len(output.segments)
        print(
            f"Feed-in: {output.segments[-1].cumulative_feed_in_cost}; import: "
            f"{output.segments[-1].cumulative_import_cost}; total: {output.segments[-1].cumulative_score}"
        )
        plt.plot(range(0, size), [x.battery_level for x in output.segments], marker="o", label="batt")
        plt.plot(range(0, size), [x.consumption for x in segments], marker="x", label="cons")
        plt.plot(range(0, size), [x.generation for x in segments], marker="+", label="gen")
        plt.plot(range(0, size), [x.import_kwh for x in output.segments], marker="<", label="gen")
        plt.plot(range(0, size), [x.feed_in_kwh for x in output.segments], marker=">", label="gen")
        plt.fill_between(
            range(0, size),
            [0 if x is None else x.min_soc * BATTERY_CAPACITY - 0.05 for x in actions],
            [0 if x is None else x.max_soc * BATTERY_CAPACITY + 0.05 for x in actions],
            step="mid",
            alpha=0.1,
        )
        plt.show()

    def run(
        self,
        segments: list[TimeSegment],
        actions: Sequence[Action | None],
        outputs: RunOutput | None = None,
    ) -> float:
        def clamp(val: float, lower: float, upper: float) -> float:
            if val < lower:
                return lower
            if val > upper:
                return upper
            return val

        self.num_runs += 1
        battery_level = self._initial_battery
        feed_in_cost = 0.0
        import_cost = 0.0
        action = INITIAL_ACTION

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
                solar_to_battery = clamp(BATTERY_CAPACITY * action.max_soc - battery_level, 0, segment.generation)
                grid_to_battery_dc = clamp(
                    BATTERY_CAPACITY * action.max_soc - battery_level - solar_to_battery,
                    0,
                    BATTERY_CHARGE_AMOUNT_PER_SEGMENT,
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
                    solar_to_battery = clamp(BATTERY_CAPACITY * action.max_soc - battery_level, 0, excess_solar_dc)
                    solar_to_grid = (
                        min(EXPORT_LIMIT_PER_SEGMENT_DC, excess_solar_dc - solar_to_battery) * DC_TO_AC_EFFICIENCY
                    )
                else:
                    required_energy_ac = segment.consumption - segment.generation * DC_TO_AC_EFFICIENCY
                    battery_to_load = clamp(
                        battery_level - BATTERY_CAPACITY * action.min_soc, 0, required_energy_ac / DC_TO_AC_EFFICIENCY
                    )
                    grid_to_load = required_energy_ac - battery_to_load * DC_TO_AC_EFFICIENCY

            battery_change = solar_to_battery + grid_to_battery_dc - battery_to_load
            battery_level += battery_change
            assert battery_level >= 0

            this_feed_in_cost = solar_to_grid * segment.feed_in_tariff
            feed_in_cost += this_feed_in_cost
            import_amount = grid_to_load + grid_to_battery_dc / AC_TO_DC_EFFICIENCY
            this_import_cost = import_amount * segment.import_tariff
            import_cost += this_import_cost

            if outputs is not None:
                outputs.segments.append(
                    RunOutputSegment(
                        battery_level=round(battery_level, 2),
                        battery_soc=round((battery_level / BATTERY_CAPACITY) * 100),
                        feed_in_kwh=round(solar_to_grid, 2),
                        import_kwh=round(import_amount, 2),
                        feed_in_cost=round(this_feed_in_cost, 2),
                        cumulative_feed_in_cost=round(feed_in_cost, 2),
                        import_cost=round(this_import_cost, 2),
                        cumulative_import_cost=round(import_cost, 2),
                        cumulative_score=round(feed_in_cost, 2) - round(import_cost, 2),
                    )
                )

        score = round(feed_in_cost, 2) - round(import_cost, 2)

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

    def is_better(self, x: float, y: float, margin: float = 0.0) -> bool:
        if abs(x - y) < margin:
            return False
        return x > y

    def shotgun_hillclimb(self, segments: list[TimeSegment]) -> tuple[list[Action], RunOutput]:
        # visited_actions_hashes = set()
        charge_set = [False, True]
        best_result_ever: float | None = None
        best_actions_ever: list[Action] = []
        slots = list(range(len(segments)))
        for _loops in range(10):
            # Keeping a fair number of "Do last action" seems to make it easier for it to find solutions which only work
            # if you consistently do the same thing a lot.
            # actions: list[Action | None] = [INITIAL_ACTION.clone() for _ in range(len(segments))]
            actions: list[Action | None] = [None] * len(segments)
            # I've noticed that just seeding the first 24 hours works well: it speeds things up, without compromising
            # the quality of the first 24 hours. Of course the second 24 hours suffers, but we don't care about that
            # really.

            # Different types of scenario suit different numbers of seeds. For cases where we e.g. need to hold the soc
            # low for a long period, then having a long sequence of None's works well. For simpler cases, we converge
            # faster if there are fewer Nones, as the whole thing is a bit less volatile.
            # A long fill factor is quite often better if we need to keep the soc low all day, but other than that
            # short fill factors tend to be better.
            fill_factor = (1, 4, 8)[(_loops % 3)]
            # TODO: Thi 24 is faster... Is it better in all cases?
            for i in range(len(actions)):
                if i % fill_factor == 0:
                    # if True:
                    charge = random.choice(charge_set)
                    # No point having a min soc when charging
                    min_soc_percent = (
                        MIN_SOC_PERMITTED_PERCENT if charge else random.choice((MIN_SOC_PERMITTED_PERCENT, 100))
                    )
                    actions[i] = Action(
                        charge,
                        min_soc=min_soc_percent / 100.0,
                        max_soc=random.randrange(min_soc_percent, 101, SOC_STEP_PERCENT) / 100.0
                        if charge
                        else random.choice([min_soc_percent, 100]) / 100.0,
                    )
            best_actions = actions.copy()
            best_result = self.run(segments, actions)
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
                        # min soc is used to prevent discharge. We'll give the model 2 options: prevent discharge,
                        # or don't.
                        for new_min_soc_percent in (
                            (MIN_SOC_PERMITTED_PERCENT,)
                            if new_charge
                            or segments[slot].generation > segments[slot].consumption / DC_TO_AC_EFFICIENCY
                            else (MIN_SOC_PERMITTED_PERCENT, 100)
                        ):
                            action.min_soc = new_min_soc_percent / 100
                            # max soc is used:
                            #  - when charging, to limit how much we pull from the grid
                            #  - when we're consuming solar, to leave space in the battery for e.g. a cheap charge
                            #    period in the future
                            new_max_soc_percents: Iterable[int]
                            if new_charge:
                                new_max_soc_percents = range(new_min_soc_percent, 101, SOC_STEP_PERCENT)
                            elif segments[slot].generation > segments[slot].consumption / DC_TO_AC_EFFICIENCY:
                                new_max_soc_percents = (new_min_soc_percent, 100)
                            else:
                                new_max_soc_percents = (100,)

                            for new_max_soc_percent in new_max_soc_percents:
                                action.max_soc = new_max_soc_percent / 100
                                new_result = self.run(segments, actions)
                                if self.is_better(new_result, best_improved_result):
                                    # self.run(segments, actions, initial_battery, debug=True)
                                    found_better = True
                                    best_improved_result = new_result
                                    best_improved_actions = actions.copy()
                                    # Since we're going to be further mutating this action, we need to clone it now
                                    action = actions[slot] = action.clone()

                    actions[slot] = old_action

                # Doing this here, rather than only when we reach a local maximum, seems to help some scenarios with
                # high generation and a late free period
                removed = 0
                for slot in range(len(actions)):
                    old_action = actions[slot]
                    if old_action is not None:
                        actions[slot] = None
                        new_result = self.run(segments, actions)
                        if self.is_better(best_improved_result, new_result):
                            actions[slot] = old_action
                        else:
                            removed += 1
                # print(f"Removed {removed}")

                # Try and remove actions, if doing so doesn't actively make things worse
                # if found_better:
                #     removed = 0
                #     for slot in range(len(actions)):
                #         old_action = best_improved_actions[slot]
                #         best_improved_actions[slot] = None
                #         new_result = self.run(segments, best_improved_actions, initial_battery)
                #         if self.is_better(best_improved_result, new_result):
                #             best_improved_actions[slot] = old_action
                #         else:
                #             removed += 1
                # print(f"Removed {removed}")

                # This does appear to be excluding solutions sometimes...
                # actions_hash = self.create_hash(actions)
                # if actions_hash in visited_actions_hashes:
                #     break
                # visited_actions_hashes.add(actions_hash)

                if found_better:
                    # Did we find an improvement? Keep going
                    best_result = best_improved_result
                    best_actions = actions = best_improved_actions  # type: ignore
                else:
                    # No? We've reached a local maximum
                    # removed = 0
                    # for slot in range(len(actions)):
                    #     old_action = actions[slot]
                    #     if old_action is not None:
                    #         actions[slot] = None
                    #         new_result = self.run(segments, actions, initial_battery)
                    #         if self.is_better(best_improved_result, new_result, margin=MARGIN):
                    #             actions[slot] = old_action
                    #         else:
                    #             removed += 1
                    # # print(f"Removed {removed}")
                    # if removed == 0:
                    break

                    # changed = self.optimize_min_max_soc(
                    #     segments, best_actions, best_result, initial_battery, shock=False
                    # )
                    # if changed:
                    #     new_result = self.run(segments, best_actions, initial_battery)
                    #     # print(f"Local maximum! Optimized min/max soc, {best_result} -> {new_result}")
                    #     best_result = new_result
                    # else:
                    #     break

                    # I would have thought this would help, but it doesn't appear to
                    # old_action = INITIAL_ACTION
                    # for slot in range(len(actions)):
                    #     if best_actions[slot] is None:
                    #         # We're going to be mutating these, so we need to clone them
                    #         best_actions[slot] = old_action.clone()
                    #     else:
                    #         old_action = best_actions[slot]

                    # while self.optimize_min_max_soc(segments, best_actions, initial_battery):
                    #     pass
                    # best_result = self.run(segments, best_actions, initial_battery)
                    # break

            best_result_24h = self.run(segments[:24], best_actions[:24])
            # self.run(segments, best_actions, initial_battery, debug=True)
            if best_result_ever is None or self.is_better(best_result, best_result_ever):
                print(f"Improved: {best_result} ({best_result_24h})")
                best_result_ever = best_result
                best_actions_ever = best_actions  # type: ignore
            else:
                print(f"Not improved: {best_result} ({best_result_24h})")

        # Also get rid of Nones

        # At this point, scrap > 48h
        # segments = segments[:24]
        # best_actions_ever = best_actions_ever[:24]

        old_action = INITIAL_ACTION
        for slot in range(len(best_actions_ever)):
            if best_actions_ever[slot] is None:
                # We're going to be mutating these, so we need to clone them
                best_actions_ever[slot] = old_action.clone()
            else:
                old_action = best_actions_ever[slot]

        assert best_actions_ever is not None
        assert best_result_ever is not None
        print(repr(best_actions_ever))

        if self._debug:
            self.plot(segments, best_actions_ever)
            self.plot(segments[:24], best_actions_ever[:24])

        # Try and simplify: if changing a slot to a "lower" action doesn't hurt the score, do it

        # TODO: Use 24 rather than len(actions) below? Do we really care about optimizing beyond 24h?

        for slot in range(len(best_actions_ever)):
            old_action = best_actions_ever[slot]

            copied_another_action = False

            # If we can make it the same as the previous action, do that
            if not copied_another_action and slot > 0 and old_action != best_actions_ever[slot - 1]:
                best_actions_ever[slot] = best_actions_ever[slot - 1].clone()
                new_result = self.run(segments, best_actions_ever)
                if not self.is_better(best_result_ever, new_result, margin=MARGIN):
                    copied_another_action = True
                else:
                    best_actions_ever[slot] = old_action

            # Try and disable charging
            if not copied_another_action and best_actions_ever[slot].charge:
                best_actions_ever[slot].charge = False
                new_result = self.run(segments, best_actions_ever)
                # If the old result was better, go back to it and continue. Otherwise go for the new result
                if not self.is_better(best_result_ever, new_result, margin=MARGIN):
                    break
                # assert(new_score < best_score_ever)
                best_actions_ever[slot].charge = True

        # The step above will have removed any unnecessary charge periods (which do pop up, as a means to prevent
        # discharge). However, we do want charge periods to extend backwards as far as possible. If we have a 3-hour
        # cheap period say, we want the charge period to extend across all of it
        ends_of_charge_periods = [
            i
            for i in range(1, len(best_actions_ever))
            if best_actions_ever[i].charge and (i == len(best_actions_ever) - 1 or not best_actions_ever[i + 1].charge)
        ]
        for end_of_charge_period in ends_of_charge_periods:
            for candidate in range(end_of_charge_period - 1, -1, -1):
                if best_actions_ever[candidate].charge:
                    continue
                prev_action = best_actions_ever[candidate]
                best_actions_ever[candidate] = best_actions_ever[end_of_charge_period].clone()
                new_result = self.run(segments, best_actions_ever)
                if self.is_better(best_result_ever, new_result, margin=MARGIN):
                    best_actions_ever[candidate] = prev_action
                    break

        # We might have made the result slightly worse. Re-calculate
        # (we don't do this as we go, to make sure that we never get more than MARGIN away from the original best case)
        best_result_ever = self.run(segments, best_actions_ever)

        # We may need to run this more than once
        while True:
            changed, best_result_ever = self.optimize_min_max_soc(
                segments, best_actions_ever, best_result_ever, margin=MARGIN
            )
            if not changed:
                break

        # Now we want to shorten charge periods. The problem is that if generation is predicted to be low, the model
        # can extend an overnight charging period until mid-morning. However there's no advantage in doing this:
        # generation might be higher than expected in which case this is detremental, and using the grid later in
        # the day is no worse than earlier in the day.
        # Run this after optimizing min/max socs. Sometimes the model will insert a small "draw from grid not batteries"
        # after a charge, because it doesn't have the control to charge to exactly the right amount. The min/max socs
        # fixes that, and this step will remove the unnecessary charge.
        # However, I think this does more harm than good, as it will sometimes remove charges within a charge period.
        # for slot in range(len(best_actions_ever) - 1, -1, -1):
        #     if best_actions_ever[slot].charge:
        #         best_actions_ever[slot].charge = False
        #         new_result = self.run(segments, best_actions_ever, initial_battery)
        #         print(f"{slot}: {best_result_ever} -> {new_result}")
        #         if self.is_better(best_result_ever, new_result, margin=MARGIN):
        #             best_actions_ever[slot].charge = True

        for i, action in enumerate(best_actions_ever):
            print(f"{i}: {action}")
        best_result_ever = self.run(segments, best_actions_ever)

        if self._debug:
            self.plot(segments, best_actions_ever)
            for i, action in enumerate(best_actions_ever[:24]):
                print(f"{i}: {action}")

            self.plot(segments[:24], best_actions_ever[:24])

            print(f"Number of runs: {self.num_runs}")

        outputs = RunOutput()
        self.run(segments, best_actions_ever, outputs)
        return best_actions_ever[:24], outputs

    def optimize_min_max_soc(
        self,
        segments: list[TimeSegment],
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
            if actions[slot].charge:
                # For charge periods, just set min soc to the min
                actions[slot].min_soc = OPTIMIZATION_MIN_SOC_PERCENT / 100
            else:
                prev_consumption = segments[slot].consumption
                prev_generation = segments[slot].generation
                # This needs to be large enough to drain the battery
                if shock:
                    segments[slot].consumption = BATTERY_CAPACITY
                    segments[slot].generation = 0

                test_result = self.run(segments, actions)

                best_min_soc = actions[slot].min_soc
                for min_soc_percent in range(OPTIMIZATION_MIN_SOC_PERCENT, 101, OPTIMIZATION_SOC_STEP_PERCENT):
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
            if not actions[slot].charge:
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

        for slot in range(len(actions)):
            if actions[slot].charge:
                prev_max_soc = actions[slot].max_soc
                for max_soc_percent in range(100, round(prev_max_soc * 100), -SOC_STEP_PERCENT):
                    actions[slot].max_soc = max_soc_percent / 100
                    new_result = self.run(segments, actions)
                    if not self.is_better(best_result_ever, new_result, margin=margin):
                        best_result_ever = new_result
                        break
                    actions[slot].max_soc = prev_max_soc
                changed = changed or actions[slot].max_soc != prev_max_soc

        return (changed, best_result_ever)
