import heapq
import time

class BlockWorldAgent:
    def solve(self, initial_arrangement, goal_arrangement):
        self.goal_arrangement = goal_arrangement
        self.goal_support_map = self.get_block_support_map(goal_arrangement)

        initial_list_state = [list(stack) for stack in initial_arrangement]
        initial_tuple_state = self.convert_to_hashable_state(initial_list_state)

        heap = []
        heapq.heappush(heap, (0, 0, initial_tuple_state, initial_list_state, []))
        visited = set()

        start_time = time.time()

        while heap:
            if time.time() - start_time > 45:
                raise RuntimeError("Search exceeded 45 seconds runtime limit.")

            f, g, tuple_state, list_state, path = heapq.heappop(heap)

            if tuple_state == self.convert_to_hashable_state(self.goal_arrangement):
                print(time.time() - start_time)
                return path

            if tuple_state in visited:
                continue
            visited.add(tuple_state)

            for move in self.possible_moves(list_state):
                self.push_move(list_state, tuple_state, move, g, path, visited, heap)

        return []

    def convert_to_hashable_state(self, state):
        return tuple(tuple(stack) for stack in state)

    def get_block_support_map(self, state):
        support = {}
        for stack in state:
            for i, block in enumerate(stack):
                support[block] = stack[i - 1] if i > 0 else "Table"
        return support

    def heuristic(self, state):
        h = 0
        current_map = self.get_block_support_map(state)

        for block, support in current_map.items():
            if self.goal_support_map.get(block) != support:
                h += 1

        for stack in state:
            best_match = 0
            for goal_stack in self.goal_arrangement:
                match = 0
                for a, b in zip(stack, goal_stack):
                    if a == b:
                        match += 1
                    else:
                        break
                best_match = max(best_match, match)
            h += len(stack) - best_match

        return h

    def possible_moves(self, state):
        moves = []
        for i, stack in enumerate(state):
            if not stack:
                continue
            block = stack[-1]
            moves.append((block, "Table"))
            for j, target in enumerate(state):
                if i != j and target:
                    moves.append((block, target[-1]))
        return moves

    def apply_move_efficient(self, list_state, move):
        block, dest = move

        # Identify source and target indices
        source_index = target_index = None
        for i, stack in enumerate(list_state):
            if stack and stack[-1] == block:
                source_index = i
            if stack and stack[-1] == dest:
                target_index = i
        if source_index is None:
            raise ValueError("Invalid move: source not found")

        # Shallow copy state and affected stacks
        new_state = list_state[:]
        new_state[source_index] = new_state[source_index][:-1]

        if not new_state[source_index]:
            new_state = new_state[:source_index] + new_state[source_index+1:]
            if target_index is not None and target_index > source_index:
                target_index -= 1

        if dest == "Table":
            new_state.append([block])
        else:
            new_target = new_state[target_index][:]  # Copy target stack
            new_target.append(block)
            new_state[target_index] = new_target

        return new_state

    def push_move(self, current_list_state, current_tuple_state, move, g, path, visited, heap):
        next_list_state = self.apply_move_efficient(current_list_state, move)
        next_tuple_state = self.convert_to_hashable_state(next_list_state)

        if next_tuple_state in visited:
            return

        new_g = g + 1
        h = self.heuristic(next_list_state)
        f = new_g + h
        heapq.heappush(heap, (f, new_g, next_tuple_state, next_list_state, path + [move]))
