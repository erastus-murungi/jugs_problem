from collections import deque
from dataclasses import dataclass
from pprint import pprint
from random import randint
from typing import Optional


@dataclass(frozen=True)
class Action:
    prev_state: tuple[int, ...]
    curr_state: tuple[int, ...]
    description: str

    @staticmethod
    def fill_jug(previous_state, current_state, filled_capacity, jug_index) -> "Action":
        return Action(
            previous_state,
            current_state,
            f"Fill {filled_capacity} liters from the river to jug {jug_index}",
        )

    @staticmethod
    def empty_jug(
        previous_state, current_state, poured_capacity, jug_index
    ) -> "Action":
        return Action(
            previous_state,
            current_state,
            f"Empty {poured_capacity} liters from jug {jug_index} to the river",
        )

    @staticmethod
    def transfer(
        previous_state,
        current_state,
        transferred_capacity,
        src_jug_index,
        dst_jug_index,
    ) -> "Action":
        return Action(
            previous_state,
            current_state,
            f"Transfer {transferred_capacity} liters from jug {src_jug_index} to the jug {dst_jug_index}",
        )


def get_action_sequence(
    pred: dict[Action, Action], current_state: Optional[Action]
) -> list[Action]:
    action_sequence = []
    while current_state is not None and current_state in pred:
        action_sequence.append(current_state)
        current_state = pred[current_state]
    action_sequence.reverse()
    return action_sequence


def can_measure_water(
    capacities: tuple[int, ...], target_capacity: int
) -> tuple[bool, list[Action]]:

    print(f"capacities={capacities}, target_capacity={target_capacity}")

    if sum(capacities) < target_capacity:
        raise ValueError(
            f"Sum of all capacities ({sum(capacities)}) is less than target capacity {target_capacity}"
        )

    states_queue, seen_states, predecessors = (
        deque([(None, (0,) * len(capacities))]),
        set(),
        {},
    )

    while len(states_queue):
        trigger, jugs_volumes = states_queue.popleft()

        if jugs_volumes in seen_states:
            continue

        seen_states.add(jugs_volumes)

        if sum(jugs_volumes) == target_capacity:
            return True, get_action_sequence(predecessors, trigger)

        for jug_index, volume in enumerate(jugs_volumes):
            if volume == 0:
                updated: tuple[int, ...] = tuple(
                    capacities[jug_index] if index == jug_index else volume
                    for index, volume in enumerate(jugs_volumes)
                )
                action: Action = Action.fill_jug(
                    jugs_volumes, updated, capacities[jug_index], jug_index
                )
                states_queue.append((action, updated))
                predecessors[action] = trigger

        for jug_index, volume in enumerate(jugs_volumes):
            if volume > 0:
                updated = tuple(
                    0 if index == jug_index else volume
                    for index, volume in enumerate(jugs_volumes)
                )
                action = Action.empty_jug(
                    jugs_volumes, updated, jugs_volumes[jug_index], jug_index
                )
                states_queue.append((action, updated))
                predecessors[action] = trigger

        for src_jug_index, src_jug_volume in enumerate(jugs_volumes):
            if src_jug_volume > 0:
                for dst_jug_index, dst_jug_volume in enumerate(jugs_volumes):
                    if dst_jug_index == src_jug_index:
                        continue
                    dst_jug_capacity = capacities[dst_jug_index]
                    if dst_jug_volume < dst_jug_capacity:
                        offer = min(dst_jug_capacity - dst_jug_volume, src_jug_volume)
                        updated = tuple(
                            dst_jug_volume + offer
                            if index == dst_jug_index
                            else src_jug_volume - offer
                            if index == src_jug_index
                            else current_volume
                            for index, current_volume in enumerate(jugs_volumes)
                        )
                        action = Action.transfer(
                            jugs_volumes, updated, offer, src_jug_index, dst_jug_index
                        )
                        states_queue.append((action, updated))
                        predecessors[action] = trigger
    return False, []


if __name__ == "__main__":
    pprint(can_measure_water(tuple(randint(0, 100) for _ in range(8)), 103))
