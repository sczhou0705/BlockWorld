from queue import PriorityQueue
from itertools import count
import copy
import time

class BlockWorldAgent:
    def __init__(self):
        pass

    def heuristic(self, config, goal):
        goal_pos = {}
        for i, stack in enumerate(goal):
            for j, block in enumerate(stack):
                goal_pos[block] = (i, j)

        misplaced = 0
        penalty = 0
        bonus = 0
        wrong_stack_penalty = 0  # 新增惩罚项

        for i, stack in enumerate(config):
            for j, block in enumerate(stack):
                if block not in goal_pos:
                    continue

                goal_i, goal_j = goal_pos[block]

                # 位置错了
                if (i, j) != (goal_i, goal_j):
                    misplaced += 1

                    # 踩在错的 block 上
                    if j > 0:
                        below = stack[j - 1]
                        if below in goal_pos:
                            if goal_pos[below][0] != i or goal_pos[below][1] != j - 1:
                                penalty += 2

                    # ➕ 错堆惩罚（新增逻辑）
                    if i != goal_i:
                        wrong_stack_penalty += 1

                else:
                    # 正确位置 + 正确堆叠 → 奖励
                    if j == 0:
                        bonus += 1
                    else:
                        below = stack[j - 1]
                        if below in goal_pos and goal_pos[below] == (i, j - 1):
                            bonus += 1

        return misplaced + penalty + wrong_stack_penalty - bonus

    def get_neighbors(self, current, goal):
        config = current["config"]
        max_stacks = len(config) + 2  # 限制堆数防爆炸
        neighbors = []

        for i, stack in enumerate(config):
            if not stack:
                continue
            block = stack[-1]

            for j in range(len(config) + 1):
                if j == i or j >= max_stacks:
                    continue

                new_config = copy.deepcopy(config)
                new_config[i].pop()

                # 去掉空堆（搬空后）
                if not new_config[i]:
                    new_config.pop(i)
                    if j > i:
                        j -= 1

                if j == len(new_config):
                    new_config.append([block])
                    destination = "Table"
                else:
                    new_config[j].append(block)
                    destination = new_config[j][-2] if len(new_config[j]) > 1 else "Table"

                new_state = {
                    "config": new_config,
                    "moves": current["moves"] + [(block, destination)],
                    "g": current["g"] + 1,
                    "h": self.heuristic(new_config, goal)
                }
                new_state["f"] = new_state["g"] + new_state["h"]
                neighbors.append(new_state)
        return neighbors

    def solve(self, initial_arrangement, goal_arrangement):
        def freeze_config(config):
            return tuple(tuple(stack) for stack in config)

        start_time = time.time()

        start = {
            "config": initial_arrangement,
            "moves": [],
            "g": 0,
            "h": self.heuristic(initial_arrangement, goal_arrangement)
        }
        start["f"] = start["g"] + start["h"]

        pq = PriorityQueue()
        counter = count()
        pq.put((start["f"], next(counter), start))
        visited = set()
        step_count = 0

        while not pq.empty():
            _, _, current = pq.get()
            config_key = freeze_config(current["config"])
            if config_key in visited:
                continue
            visited.add(config_key)

            step_count += 1
            if step_count % 100 == 0:
                print(f"[Step {step_count}] f = {current['f']}, stacks = {len(current['config'])}")

            if current["config"] == goal_arrangement:
                print("Solution found in", step_count, "steps.")
                print("Total time: {:.2f} seconds".format(time.time() - start_time))
                return current["moves"]

            for neighbor in self.get_neighbors(current, goal_arrangement):
                key = freeze_config(neighbor["config"])
                if key not in visited:
                    pq.put((neighbor["f"], next(counter), neighbor))

        print("No solution found after expanding", step_count, "states.")
        print("Total time: {:.2f} seconds".format(time.time() - start_time))
        return []
