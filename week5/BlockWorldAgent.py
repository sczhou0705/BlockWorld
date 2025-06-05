

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
                end_time = time.time()
                run_time = end_time - start_time
                # print(f"Test case solved in {run_time:.4f} seconds")
                return path

            if current_tuple in visited:
                continue
            visited.add(current_tuple)

            current_state = self.convert_to_mutable_state(current_tuple)
            moves = self.possible_moves(current_state)

            for move in moves:
                self.push_move(current_state, move, g, path, visited, unexplored_state)
        # print(f"No solution found (ran for {run_time:.4f} seconds)")
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
        penalty = 0  # Initialize total penalty score

        current_map = self.get_block_support_map(state)
        goal_map = self.get_block_support_map(self.goal_arrangement)

        # Step 1: Compare block-on-block relationships
        for block in current_map:
            current_support = current_map[block]
            goal_support = goal_map.get(block)

            if current_support != goal_support:
                penalty += 1

        # Step 2: For each stack, check if it matches any goal stack prefix
        for stack in state:
            matched = False  # Assume the stack is incorrect

            for goal_stack in self.goal_arrangement:
                if self.stack_matches_goal_bottom(stack, goal_stack):
                    matched = True
                    break

            if not matched:
                penalty += len(stack)
        return penalty


    def possible_moves(self, state):
        valid_moves = [] 
        goal_map =self.get_block_support_map(self.goal_arrangement)

        for i, stack in enumerate(state):
            if len(stack) == 0:
                continue # skip empty stacks
# A block can be moved only if it is on top and no block aon it.
            block = stack[-1]
            # one option : put it on table
            valid_moves.append((block, "Table"))
# second option : move the block onto the top of another stack 
            for target_index, target_stack in enumerate(state):
                if i == target_index:
                    continue # skip same stack
                if len(target_stack) == 0:
                    continue # skip empty stack

                target_block = target_stack[-1]
                valid_moves.append((block, target_block))

        return valid_moves
    def stack_matches_goal_bottom(self, stack, goal_stack):
        if len(stack) > len(goal_stack):
            return False
        for i in range(len(stack)):
            if stack[i] != goal_stack[i]:
                return False
        return True

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
