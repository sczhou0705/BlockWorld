

import heapq
import copy
import time

class BlockWorldAgent:
    def solve(self, initial_arrangement, goal_arrangement):
        self.goal_arrangement = goal_arrangement
        # self.step_trace = []  # To store each state and move for HTML output

        initial_tuple = self.convert_to_hashable_state(initial_arrangement)
        goal_tuple = self.convert_to_hashable_state(goal_arrangement)
        # Initialize the priority queue
        unexplored_state = []
        # f = 0,g = 0,and an empty path 
        heapq.heappush(unexplored_state, (0, 0, initial_tuple, []))
        visited = set()

        start_time = time.time()

        while len(unexplored_state) > 0:
            elapsed_time = time.time() - start_time
            if elapsed_time > 45:
                raise RuntimeError("Search exceeded 45 seconds runtime limit.")

            f, g, current_tuple, path = heapq.heappop(unexplored_state)

            if current_tuple == goal_tuple:
                # self.step_trace.append({'state': self.tuple_to_state(current_tuple), 'move': None})
                return path

            if current_tuple in visited:
                continue
            visited.add(current_tuple)

            current_state = self.convert_to_mutable_state(current_tuple)
            moves = self.possible_moves(current_state)

            for move in moves:
                self.push_move(current_state, move, g, path, visited, unexplored_state)

        return []

    def convert_to_hashable_state(self, state):
        frozen_stacks = []
        for stack in state:
            frozen_stacks.append(tuple(stack))
        return tuple(frozen_stacks)

    def convert_to_mutable_state(self, state_tuple):
        mutable_stacks = []
        for stack in state_tuple:
            mutable_stacks.append(list(stack))
        return mutable_stacks

    def get_block_support_map(self, state):
        parent = {}
        for stack in state:
            for i, block in enumerate(stack):
                if i == 0:
                    parent[block] = "Table"
                else:
                    parent[block] = stack[i - 1]
                # print(f"{block} is on {parent[block]}") 
      
        return parent

    def heuristic(self, state):
        current_map = self.get_block_support_map(state)
        goal_map = self.get_block_support_map(self.goal_arrangement)
        # print(goal_map)
        mismatches = 0
        for block in current_map:
            current_parent = current_map[block]
            goal_parent = goal_map.get(block)
            if current_parent != goal_parent:
                mismatches += 1

        return mismatches

    def possible_moves(self, state):
        valid_moves = []
        goal_map = self.get_block_support_map(self.goal_arrangement)

        # 获取堆顶积木 [(index, top_block)]
        top_blocks = []
        for i, stack in enumerate(state):
            if stack:
                top_blocks.append((i, stack[-1]))

        # 允许 move 的前缀堆判定函数
        def is_prefix(stack, goal_stack):
            return stack == goal_stack[:len(stack)]

        # 建立目标堆列表
        goal_stacks = self.goal_arrangement

        for i, block in top_blocks:
            # 桌面动作
            if goal_map.get(block) == "Table":
                valid_moves.append((block, "Table"))

            # 目标结构堆叠动作（基于前缀结构匹配）
            for j, target_stack in enumerate(state):
                if i == j or not target_stack:
                    continue

                for goal_stack in goal_stacks:
                    if is_prefix(target_stack, goal_stack):
                        expected_parent = goal_map.get(block)
                        if target_stack[-1] == expected_parent:
                            valid_moves.append((block, target_stack[-1]))
                        break  # 一旦匹配一个目标堆前缀就跳出

        return valid_moves


    def apply_move(self, state, move):
        block, destination = move

        # shallow copy 
        new_state = []
        for stack in state:
            copied_stack = stack[:]
            new_state.append(copied_stack)

    
        source_index = None
        for i, stack in enumerate(new_state):
            if stack and stack[-1] == block:
                stack.pop()
                if not stack:
                    source_index = i 
                break
        if source_index is not None:
            del new_state[source_index]

     
        if destination == "Table":
            new_state.append([block]) 
        else:
            for stack in new_state:
                if stack and stack[-1] == destination:
                    stack.append(block)
                    break

        return new_state


    def push_move(self, current_state, move, g, path, visited, heap):
        next_state = self.apply_move(current_state, move)
        next_tuple = self.convert_to_hashable_state(next_state)

        if next_tuple in visited:
            return
        else:
                new_g = g + 1
                h = self.heuristic(next_state)
                new_f = new_g + h
                new_path = path + [move]
                heapq.heappush(heap, (new_f, new_g, next_tuple, new_path))
