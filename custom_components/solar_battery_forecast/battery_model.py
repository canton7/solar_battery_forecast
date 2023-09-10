import enum
import random
from dataclasses import dataclass
from math import floor

from matplotlib import pyplot as plt


class ActionType(enum.IntEnum):
    SELF_USE = 0,
    FEED_IN = 1,
    BACKUP = 2,
    CHARGE = 3

@dataclass
class Action:
    type: ActionType
    min_soc: float
    max_soc: float

    def clone(self) -> 'Action':
        return Action(self.type, self.min_soc, self.max_soc)

    def hash(self) -> int:
        return hash((self.type, self.min_soc, self.max_soc))

    def __repr__(self) -> str:
        return f"Action(ActionType.{self.type.name}, {self.min_soc}, {self.max_soc})"

@dataclass
class TimeSegment:
    generation: float
    consumption: float
    feed_in_tariff: float
    import_tariff: float

@dataclass
class RunResult:
    import_cost: float = 0
    feed_in_cost: float = 0
    battery_level: float = 0
    battery_cumulative_charge: float = 0
    max_solar_battery: float = 0

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

INITIAL_ACTION = Action(ActionType.SELF_USE, min_soc=MIN_SOC_PERMITTED_PERCENT/100, max_soc=1.0)

class BatteryModel:

    def __init__(self) -> None:
        self.debug = False
        self.num_runs = 0

    def run(self, segments: list[TimeSegment], actions: list[Action | None], initial_battery: float, debug: bool = False) -> RunResult:
        self.num_runs += 1
        battery_level = initial_battery
        result = RunResult()
        action = INITIAL_ACTION

        # Debug
        battery_levels = []
        imports = []
        exports = []

        for i, (segment, action_change) in enumerate(zip(segments, actions)):
            if action_change is not None:
                action = action_change
            solar_to_battery = 0
            solar_to_grid = 0
            battery_to_load = 0
            grid_to_load = 0
            grid_to_battery_ac = 0
            grid_to_battery_dc = 0

            if action.type == ActionType.SELF_USE:
                # If generation can cover consumption, excess goes into battery. Else excess comes from battery if available
                if segment.generation > segment.consumption / DC_TO_AC_EFFICIENCY:
                    excess_solar_dc = segment.generation - segment.consumption / DC_TO_AC_EFFICIENCY
                    solar_to_battery = max(0, min(BATTERY_CAPACITY * action.max_soc - battery_level, excess_solar_dc))
                    solar_to_grid = min(EXPORT_LIMIT_PER_SEGMENT_DC, excess_solar_dc - solar_to_battery) * DC_TO_AC_EFFICIENCY
                else:
                    required_energy_ac = segment.consumption - segment.generation * DC_TO_AC_EFFICIENCY
                    battery_to_load = max(0, min(battery_level - BATTERY_CAPACITY * action.min_soc, required_energy_ac / DC_TO_AC_EFFICIENCY))
                    grid_to_load = required_energy_ac - battery_to_load * DC_TO_AC_EFFICIENCY
            elif action.type == ActionType.FEED_IN:
                # Generation goes to grid rather than battery (up to export limit), but consumption still draws from battery
                if segment.generation > segment.consumption / DC_TO_AC_EFFICIENCY:
                    excess_solar_dc = segment.generation - segment.consumption / DC_TO_AC_EFFICIENCY
                    solar_to_grid_dc = min(EXPORT_LIMIT_PER_SEGMENT_DC, excess_solar_dc)
                    solar_to_grid = solar_to_grid_dc * DC_TO_AC_EFFICIENCY
                    solar_to_battery = min(BATTERY_CAPACITY, excess_solar_dc - solar_to_grid_dc)
                else:
                    required_energy_ac = segment.consumption - segment.generation * DC_TO_AC_EFFICIENCY
                    battery_to_load = max(0, min(battery_level - BATTERY_CAPACITY * action.min_soc, required_energy_ac / DC_TO_AC_EFFICIENCY))
                    grid_to_load = required_energy_ac - battery_to_load * DC_TO_AC_EFFICIENCY
            elif action.type == ActionType.BACKUP:
                # PV goes first to batteries, then to house, with excess being exported
                solar_to_battery = max(0, min(BATTERY_CAPACITY * action.max_soc - battery_level, segment.generation))
                excess_solar_ac = (segment.generation - solar_to_battery) * DC_TO_AC_EFFICIENCY
                if excess_solar_ac > segment.consumption:
                    solar_to_grid = min(EXPORT_LIMIT_PER_SEGMENT, excess_solar_ac - segment.consumption)
                else:
                    grid_to_load = segment.consumption - excess_solar_ac
            elif action.type == ActionType.CHARGE:
                # I don't actually know, but... I assume that solar replaces grid up to the charge rate
                solar_to_battery = max(0, min(BATTERY_CAPACITY * action.max_soc - battery_level, segment.generation))
                grid_to_battery_dc = max(0, min(BATTERY_CAPACITY * action.max_soc - battery_level - solar_to_battery, BATTERY_CHARGE_AMOUNT_PER_SEGMENT))
                grid_to_battery_ac = grid_to_battery_dc / AC_TO_DC_EFFICIENCY
                excess_solar_ac = (segment.generation - solar_to_battery) * DC_TO_AC_EFFICIENCY
                # Doesn't consider inverter limits
                if excess_solar_ac > segment.consumption:
                    solar_to_grid = min(EXPORT_LIMIT_PER_SEGMENT, excess_solar_ac - segment.consumption)
                else:
                    grid_to_load = segment.consumption - excess_solar_ac

            battery_change = solar_to_battery + grid_to_battery_dc - battery_to_load
            battery_level += battery_change
            assert(battery_level >= 0)

            # TODO: Not currently working
            result.battery_cumulative_charge += battery_level
            result.feed_in_cost += solar_to_grid * segment.feed_in_tariff
            result.import_cost += (grid_to_load + grid_to_battery_ac) * segment.import_tariff
            if battery_change > 0 and battery_level >= BATTERY_CAPACITY and action.type != ActionType.CHARGE and battery_level > result.max_solar_battery:
                result.max_solar_battery = battery_level
                # print(f"Filled the battery at {i}")


            if debug:
                imports.append(grid_to_load + grid_to_battery_ac)
                exports.append(solar_to_grid)
                battery_levels.append(battery_level)

        if debug:
            plt.plot(range(0, 24), battery_levels[:24], marker='o', label='batt')
            plt.plot(range(0, 24), [x.consumption for x in segments[:24]], marker='x', label='cons')
            plt.plot(range(0, 24), [x.generation for x in segments[:24]], marker='+', label='gen')
            plt.plot(range(0, 24), imports[:24], marker='<', label='gen')
            plt.plot(range(0, 24), exports[:24], marker='>', label='gen')
            plt.show()

        result.battery_level = battery_level
        return result

    def create_hash(self, actions: list[Action | None]) -> int:
        prev_action_hash = INITIAL_ACTION.hash()
        h = 0
        for action in actions:
            this_hash = prev_action_hash if action is None else action.hash()
            h = hash((h, this_hash))
        return h


    def shotgun_hillclimb(self, segments: list[TimeSegment], initial_battery: float):

        def score_result(result: RunResult) -> float:
            # Round to avoid floating-point error saying that one result is better than another, when in fact they're the same
            return round(result.feed_in_cost, 2) - round(result.import_cost, 2)#  + round(result.battery_level * 10)

        def is_better(x: RunResult, y: RunResult) -> bool:
            # if x.max_solar_battery != y.max_solar_battery:
            #     return x.max_solar_battery > y.max_solar_battery
            x_score = score_result(x)
            y_score = score_result(y)
            # if x_score != y_score:
            return x_score > y_score
            # Reward filling the battery at some point during the day

            # If they score equal, choose the one with the larger amount of charge held in the batter for the longest
            # This inventivises runs which charge the battery earlier, which reduces risk
            # TODO: However, this isn't currently working
            # print(f"Bleh. {x_score}, {y_score}, {x.battery_cumulative_charge}, {y.battery_cumulative_charge}")
            # return x.battery_cumulative_charge > y.battery_cumulative_charge

        visited_actions_hashes = set()
        action_type_set = [ActionType.SELF_USE, ActionType.CHARGE]
        best_result_ever: RunResult | None = None
        best_actions_ever: list[Action] = []
        slots = list(range(len(segments)))
        for _ in range(20):
            # actions = [Action.SELF_USE] * 2 + [Action.BACKUP] * 3 + [Action.SELF_USE] * 11 + [Action.FEED_IN] * 3 + [Action.SELF_USE] * 5
            # Keeping a fair number of "Do last action" seems to make it easier for it to find solutions which only work
            # if you consistently do the same thing a lot.
            actions = [None] * len(segments)
            # actions = [Action(ActionType.SELF_USE, 0.2, 1.0) for _ in range(len(segments))]
            # We look at 48 hours at a time. I've noticed that just seeding the first 24 hours works well: it speeds things up, without
            # compromising the quality of the first 24 hours. Of course the second 24 hours suffers, but we don't care about that really.
            for _ in range(floor(24 * 0.5)): # Seeding about half seems to work well
                action_type = random.choice(action_type_set)
                # No point having a min soc when charging
                min_soc_percent = MIN_SOC_PERMITTED_PERCENT if action_type == ActionType.CHARGE else random.randrange(MIN_SOC_PERMITTED_PERCENT, 101, SOC_STEP_PERCENT)
                actions[random.randint(0, 24)] = Action(
                    action_type,
                    min_soc = min_soc_percent / 100.0,
                    max_soc = random.randrange(min_soc_percent, 101, SOC_STEP_PERCENT) / 100.0,
                )
            # print(actions)
            # actions = [random.choice(actions_set) for _ in range(len(segments))]
            # actions = [Action.CHARGE] * len(segments)
            best_actions = actions.copy()
            best_result = self.run(segments, actions, initial_battery)
            # print(f"Starting best score: {best_score}")
            while True:
                found_better = False
                # We evaluate each of the possible changes, and see which one has the greatest effect
                best_improved_result = best_result
                best_improved_actions: list[Action] | None = None
                # Shuffling these means we choose a random action from those with the best score
                random.shuffle(slots)
                for slot in slots:
                    if actions[slot] is None:
                        old_action = None
                        actions[slot] = Action(ActionType.FEED_IN, MIN_SOC_PERMITTED_PERCENT / 100, 1.0) # All these properties are going to be overridden shortly
                    else:
                        old_action = actions[slot]
                        actions[slot] = actions[slot].clone()
                    for new_action_type in action_type_set:
                        # TODO: Efficiency
                        # if actions[slot] is not None and actions[slot] == new_action_type:
                        #     continue
                        actions[slot].type = new_action_type
                        for new_min_soc_percent in [MIN_SOC_PERMITTED_PERCENT] if new_action_type == ActionType.CHARGE or segments[slot].generation > segments[slot].consumption / DC_TO_AC_EFFICIENCY else range(MIN_SOC_PERMITTED_PERCENT, 101, SOC_STEP_PERCENT):
                            actions[slot].min_soc = new_min_soc_percent / 100
                            for new_max_soc_percent in range(new_min_soc_percent, 101, SOC_STEP_PERCENT) if new_action_type == ActionType.CHARGE or segments[slot].generation > segments[slot].consumption  / DC_TO_AC_EFFICIENCY else [100]:
                            # for new_max_soc_percent in range(new_min_soc_percent, 100, 20):
                                actions[slot].max_soc = new_max_soc_percent / 100
                                new_result = self.run(segments, actions, initial_battery)
                                if is_better(new_result, best_improved_result):
                                    # print(f"Changing {slot} from {prev_action} to {new_action} gives {new_score} >= {best_improved_score}")
                                    found_better = True
                                    best_improved_result = new_result
                                    best_improved_actions = actions.copy()
                                    # Since we're going to be further mutating this action, we need to clone it now
                                    actions[slot] = actions[slot].clone()
                    actions[slot] = old_action
                hash = self.create_hash(actions)
                if hash in visited_actions_hashes:
                    break
                visited_actions_hashes.add(hash)
                if found_better:
                    # Did we find an improvement? Keep going
                    best_result = best_improved_result
                    best_actions = actions = best_improved_actions
                else:
                    # No? We've reached a local maximum
                    break
            if best_result_ever is None or is_better(best_result, best_result_ever):
                best_result_ever = best_result
                best_actions_ever = best_actions

        # Do a final pass. This time, try and simplify: if changing a slot to a "lower" action doesn't hurt the score, do it
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
        # best_result_ever = run(segments, best_actions_ever, initial_battery, debug=True)
        # print(best_result_ever)

        print(repr(best_actions_ever))


        for slot in range(len(actions)):
            old_action = best_actions_ever[slot]

            copied_another_action = False

            # Are we able to bring the next charge period forward?
            # Otherwise we can end up with e.g. a 3-hour low-rate charge period, but we settle on a result which just
            # charges during the final hour of that
            # If this is a charge period, then look for the last in the current sequence of charge periods: we can end up with
            # charges with max_soc of e.g. 0.3, 0.3, 0.4
            # candidate_charge_period_slot = next((i for i in range(slot+1, len(actions)) if best_actions_ever[i].type == ActionType.CHARGE and (i == len(actions) - 1 or best_actions_ever[i+1].type != ActionType.CHARGE)), None)
            # if candidate_charge_period_slot is not None:
            #     best_actions_ever[slot] = best_actions_ever[candidate_charge_period_slot].clone()
            #     new_result = run(segments, best_actions_ever, initial_battery)
            #     if not is_better(best_result_ever, new_result):
            #         copied_another_action = True
            #     else:
            #         best_actions_ever[slot] = old_action

            # If we can make it the same as the previous action, do that
            if not copied_another_action and slot > 0:
                best_actions_ever[slot] = best_actions_ever[slot - 1].clone()
                new_result = self.run(segments, best_actions_ever, initial_battery)
                if not is_better(best_result_ever, new_result):
                    copied_another_action = True
                else:
                    best_actions_ever[slot] = old_action

            if not copied_another_action:
                for action_type in action_type_set:
                    if int(action_type) >= int(best_actions_ever[slot].type):
                        break
                    prev_action_type = best_actions_ever[slot].type
                    best_actions_ever[slot].type = action_type
                    new_result = self.run(segments, best_actions_ever, initial_battery)
                    # If the old result was better, go back to it and continue. Otherwise go for the new result
                    if not is_better(best_result_ever, new_result):
                        break
                    # assert(new_score < best_score_ever)
                    best_actions_ever[slot].type = prev_action_type

        # The step above will have removed any unnecessary charge periods (which do pop up, as a means to prevent discharge)
        # However, we do want charge periods to extend backwards as far as possible. If we have a 3-hour cheap period say, we want the charge
        # period to extend across all of it
        ends_of_charge_periods = [i for i in range(1, len(actions)) if best_actions_ever[i].type == ActionType.CHARGE and (i == len(actions) - 1 or best_actions_ever[i+1].type != ActionType.CHARGE)]
        for end_of_charge_period in ends_of_charge_periods:
            for candidate in range(end_of_charge_period - 1, -1, -1):
                if best_actions_ever[candidate].type == ActionType.CHARGE:
                    continue
                prev_action = best_actions_ever[candidate]
                best_actions_ever[candidate] = best_actions_ever[end_of_charge_period].clone()
                new_result = self.run(segments, best_actions_ever, initial_battery)
                if is_better(best_result_ever, new_result):
                    best_actions_ever[candidate] = prev_action
                    break

        # Now that we've got the charge periods in place, try and optimize the min/max socs
        # This time we can lower it to 10%. We didn't want to do that during planning to as to leave a margin.
        for slot in range(len(actions)):
            # If we can decrease the min soc without hurting the score, do that
            prev_min_soc = best_actions_ever[slot].min_soc
            for min_soc_percent in range(round(prev_min_soc * 100) - SOC_STEP_PERCENT, 10 - 1, -SOC_STEP_PERCENT):
                best_actions_ever[slot].min_soc = min_soc_percent / 100
                new_result = self.run(segments, best_actions_ever, initial_battery)
                if not is_better(best_result_ever, new_result):
                    break
                best_actions_ever[slot].min_soc = prev_min_soc

            # If this is a charge period, just make it as high as it can be.
            # Othewise, we want to try the max and min before anything in between. If we're just charging normally it should be 1.0, if we're using it to prevent
            # discharge it should be min_soc, and more specialised cases take intermediate values.
            prev_max_soc = best_actions_ever[slot].max_soc
            if best_actions_ever[slot].type == ActionType.CHARGE and slot > 0:
                max_soc_percents = range(100, round(prev_max_soc * 100), -SOC_STEP_PERCENT) # [round(best_actions_ever[slot - 1].max_soc * 100)]
            else:
            #     # Try 1.0 first, then the min soc, then everything in between
                max_soc_percents = [100, round(best_actions_ever[slot].min_soc * 100)] + list(range(100 - SOC_STEP_PERCENT, round(prev_max_soc * 100), -SOC_STEP_PERCENT))
            for max_soc_percent in max_soc_percents:
                best_actions_ever[slot].max_soc = max_soc_percent / 100
                new_result = self.run(segments, best_actions_ever, initial_battery)
                if not is_better(best_result_ever, new_result):
                    break
                best_actions_ever[slot].max_soc = prev_max_soc


        if self.debug:
            for i, action in enumerate(best_actions_ever[:24]):
                print(f"{i}: {action}")

            final_result = self.run(segments[:24], best_actions_ever[:24], initial_battery, debug=True)
            print(final_result)
            print(score_result(final_result))

            print(f"Number of runs: {self.num_runs}")

        return best_actions_ever[:24]
