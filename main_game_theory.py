# Welcome to
# __________         __    __  .__                               __
# \______   \_____ _/  |__/  |_|  |   ____   ______ ____ _____  |  | __ ____
#  |    |  _/\__  \\   __\   __\  | _/ __ \ /  ___//    \\__  \ |  |/ // __ \
#  |    |   \ / __ \|  |  |  | |  |_\  ___/ \___ \|   |  \/ __ \|    <\  ___/
#  |________/(______/__|  |__| |____/\_____>______>___|__(______/__|__\\_____>
#
# This file can be a nice home for your Battlesnake logic and helper functions.
#
# To get you started we've included code to prevent your Battlesnake from moving backwards.
# For more info see docs.battlesnake.com

from typing import Dict, List, Set, Optional, Any, Tuple
import enum
from copy import deepcopy

NUM_LAYERS = 5
"""Number of layers to generate in the state tree"""
LAYER_REWARD_DECAY = 0.5 
"""Decay multiplier for rewards in each layer. This is to put higher value to sooner rewards than later ones"""
AGGRESSION_MULTIPLIER = 0.25
"""Enclosed spaces smaller than this are considered dangerous and therefore to be avoided if the snake can't fit in them"""
DANGEROUS_ENCLOSED_SPACE_REWARD = -100
"""The penalty for moving into a dangerous enclosed space"""
HUNGER_THRESHOLD = 20
"""The health threshold at which the snake is considered hungry and should prioritize food"""
AVOID_EDGE_REWARD = -5
"""The penalty for moving towards the edge of the board"""
BESIDE_FOOD_REWARD = 10
"""The reward for moving to the food when the snake is already beside it"""
AVOID_HEAD_REWARD = -100
"""The penalty for moving towards the opponent's head when the opponent is larger"""

class Player(enum.Enum):
    """The player that is making the move"""
    YOU = 'you'
    OPPONENT = 'opponent'

class Direction(enum.Enum):
    """The direction to move in"""
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"

class State:
    """A state in the state tree"""
    def __init__(self, state: Dict[str, Any], move_made: Optional[Direction], reward: float, player_turn: Player) -> None:
        self.state = state
        """The state of the game"""
        self.player_turn = player_turn
        """The player that is making the move"""
        self.reward = reward
        """The reward the player gets for making the move"""
        self.move_made = move_made
        """The move that was made to get to this state"""
        self.next_states: List[State] = []
        """The next states that can be reached from this state"""


turn_history: List[State] = []

def info() -> Dict[str, Any]:
    print("INFO")

    return {
        "apiversion": "1",
        "author": "",  # TODO: Your Battlesnake Username
        "color": "#800080",  # TODO: Choose color
        "head": "default",  # TODO: Choose head
        "tail": "default",  # TODO: Choose tail
    }


# start is called when your Battlesnake begins a game
def start(game_state: Dict[str, Any]):
    print("GAME START")
    turn_history.clear()


# end is called when your Battlesnake finishes a game
def end(game_state: Dict[str, Any]):
    print(f"GAME OVER. Turns Done: {len(turn_history)}\n\n")
    while True:
        turn = input("Select turn to view: ")
        if turn == "q":
            break
        depth = input("Select depth to view: ")

        visualize_game_state(turn_history[int(turn)], int(depth))


def generate_state_tree(root_state: State, layers: int, is_root = False):
    """Generates a tree of states for the given root state

    Args:
        root_state: The state to generate the tree from
        layers: The number of layers to generate
        is_root: Whether or not the given state is the root state. This is important because the child states of the root are always the player's states

    Returns:
        The generated state tree
    """
    # If we've reached the end of the tree, return the root state
    if layers == 0:
        return root_state

    player_turn = root_state.player_turn
    # If an opponent exists, we need to alternate between players
    if "opponent" in root_state.state:
        if is_root:
            player_turn = Player.YOU
            next_player_turn = Player.YOU
        else:
            next_player_turn = Player.YOU if player_turn == Player.OPPONENT else Player.OPPONENT
    else:
        next_player_turn = player_turn

    next_possible_moves = get_possible_moves(root_state, next_player_turn)

    for next_move in next_possible_moves:
        coords = get_snake_move_coord(root_state.state, next_move, next_player_turn)
        move_reward = coord_to_reward(root_state, coords, next_player_turn)
        next_state = move_snake(root_state.state, next_move, next_player_turn)
        state = State(next_state, next_move, move_reward, next_player_turn)
        root_state.next_states.append(state)

    for next_state in root_state.next_states:
        generate_state_tree(next_state, layers-1)

    return root_state

def get_max_depth(state: State) -> int:
    """Gets the maximum depth of the state tree

    Args:
        state: The state to get the maximum depth from

    Returns:
        The maximum depth of the state tree
    """
    if len(state.next_states) == 0:
        return 1
    return 1 + max(get_max_depth(next_state) for next_state in state.next_states)

def get_max_reward(state: State) -> float:
    """Gets the maximum reward that can be achieved from the given state

    Args:
        state: The state to get the maximum reward from

    Returns:
        The maximum reward that can be achieved from the given state
    """
    if len(state.next_states) == 0:
        return state.reward
    return state.reward + LAYER_REWARD_DECAY * max(get_max_reward(next_state) for next_state in state.next_states)
        
def get_next_moves(state_tree: State) -> Dict[Direction, Tuple[int, float]]:
    """Gets the next moves that can be made from the given state and their rewards

    Args:
        state_tree: The state to get the next moves from

    Returns:
        The next moves that can be made from the given state and their rewards
    """
    if not state_tree.next_states:
        return {}

    next_moves: Dict[Direction, Tuple[int, float]] = {
        next_state.move_made: (get_max_depth(next_state), get_max_reward(next_state)) for next_state in state_tree.next_states if next_state.move_made is not None
    }

    return next_moves
    

# move is called on every turn and returns your next move
# Valid moves are "up", "down", "left", or "right"
# See https://docs.battlesnake.com/api/example-move for available data
def move(game_state: Dict[str, Any]) -> Dict[str, Any]:
    game_state = simplify_game_state(game_state)
    state_tree = State(game_state, None, 0, Player.YOU)
    generate_state_tree(state_tree, NUM_LAYERS, is_root=True)
    turn_history.append(state_tree)

    next_moves = get_next_moves(state_tree)

    if len(next_moves) == 0:
        print(f"MOVE {game_state['turn']}: No safe moves detected! Moving down")
        return {"move": Direction.DOWN.value}

    best_move = max(next_moves, key=lambda k: next_moves.get(k, (0, 0)))
    print(f"MOVE {game_state['turn']}: {best_move.value} |{'|'.join(f' {move.value}: {next_moves[move][0]}/{next_moves[move][1]:2f}' for move in next_moves)}")   
    # print(f"Adjacent move rewards: {'|'.join(f' {move.value}: {coord_to_reward(state_tree, get_snake_move_coord(state_tree, move, Player.YOU), Player.YOU):2f} ' for move in next_moves)}")
    return {"move": best_move.value}


def get_possible_moves(game_state: State, player: Player) -> Set[Direction]:
    """Gets the possible moves that can be made from the given state. Impossible moves are ones that kill the snake.
    Args:
        game_state: The state to get the possible moves from
        player: The player to get the possible moves for

    Returns:
        The possible moves that can be made from the given state
    """
    possible_moves = {direction for direction in Direction}
    safe_moves = possible_moves.copy()

    for move in possible_moves:
        move_coord = get_snake_move_coord(game_state.state, move, player)
        
        # Discard move if it makes snake hit a wall
        if not 0 <= move_coord["x"] < game_state.state["board"]["width"] or not 0 <= move_coord["y"] < game_state.state["board"]["height"]:
            safe_moves.discard(move)
            continue

        # Discard move if it makes snake hit itself
        not_safe = False
        for body_coords in game_state.state[player.value]["body"][1:]:
            if move_coord == body_coords:
                safe_moves.discard(move)
                not_safe = True
                break

        if not_safe:
            continue

        # Discard move if it makes snake hit opponent
        if "opponent" in game_state.state:
            curr_opp = Player.YOU if player.value == Player.OPPONENT else Player.OPPONENT
            pursue_head = 1 if game_state.state[curr_opp.value]["length"] < game_state.state[player.value]["length"] else 0
            for opp_coords in game_state.state[curr_opp.value]["body"][pursue_head:]:
                if move_coord == opp_coords:
                    safe_moves.discard(move)
                    not_safe = True
                    break

    return safe_moves

def can_fit(game_state: Dict[str, Any], size: int, coordinate: Dict[str, int]) -> bool:
    """Utilizes a flood fill algorithm to determine if the snake can fit in the potentially enclosed space at a given coordinate"""

    def dfs(x: int, y: int, visited: Set[Tuple[int, int]]) -> bool:
        if (x, y) in visited:
            return False
        
        if x < 0 or x >= game_state["board"]["width"] or y < 0 or y >= game_state["board"]["height"] \
              or {"x": x, "y": y} in game_state["you"]["body"] \
              or ("opponent" in game_state and {"x": x, "y": y} in game_state["opponent"]["body"]):
            return False
        if len(visited) == size:
            return True

        visited.add((x, y))
        if dfs(x+1, y, visited) or dfs(x-1, y, visited) or dfs(x, y+1, visited) or dfs(x, y-1, visited):
            return True
        visited.remove((x, y))
        return False
    
    return dfs(coordinate["x"], coordinate["y"], set())
    

def get_snake_move_coord(game_state: Dict[str, Any], direction: Direction, player: Player) -> Dict[str, int]:
    """Get the coordinate that the snake will move to if it moves in the given direction

    Args:
        game_state: The state of the game
        direction: The direction to move in
        player: The player that is making the move

    Raises:
        Exception: If the direction is invalid

    Returns: A dictionary containing the x and y coordinates of the move
        
    """
    snake_head_pos = game_state[player.value]["body"][0]

    x = snake_head_pos['x']
    y = snake_head_pos['y']
    if direction == Direction.LEFT:
        return {"x": x-1, "y": y}
    elif direction == Direction.DOWN:
        return {"x": x, "y": y-1}
    elif direction == Direction.RIGHT:
        return {"x": x+1, "y": y}
    elif direction == Direction.UP:
        return {"x": x, "y": y+1}
    else:
        raise Exception(f'Invalid direction: {direction}')

def get_manhattan_distance(x1: int, y1: int, x2: int, y2: int) -> int:
    """Gets the manhattan distance between two points

    Args:
        x1: the x coordinate of the first point
        y1: the y coordinate of the first point
        x2: the x coordinate of the second point
        y2: the y coordinate of the second point

    Returns:
        The manhattan distance between the two points
    """
    return abs(x2 - x1) + abs(y2 - y1)
    
def coord_to_reward(game_state: State, coords: Dict[str, int], player_turn: Player) -> float:
    """Gets the reward for a player if they move to the given coordinates

    Args:
        game_state: The state of the game
        coords: The coordinates to get the reward for
        player_turn: The player that is making the move

    Returns:
        _description_
    """
    reward = 0
    player = player_turn.value
    opponent = Player.YOU.value if player_turn == Player.OPPONENT else Player.OPPONENT.value
    
    # Reward from moving closer to food
    # Only add reward if the snake is smaller or equal to the opponent, or hungry
    if game_state.state[player_turn.value]["health"] < HUNGER_THRESHOLD or \
          ("opponent" in game_state.state and game_state.state[player]["length"] <= game_state.state[opponent]["length"]):
        for food_coord in game_state.state["board"]["food"]:
            food_x = food_coord["x"]
            food_y = food_coord["y"]
            x = coords["x"]
            y = coords["y"]
            dist = get_manhattan_distance(x, y, food_x, food_y)

            if dist == 0:
                reward += BESIDE_FOOD_REWARD
            else:
                reward += 1/dist

    # Reward from moving closer to opponent
    if "opponent" in game_state.state:
        reward += AGGRESSION_MULTIPLIER * aggression_reward(game_state, player_turn)

    # Penalty if the snake is moving towards the opponent's head when the opponent is larger
    if "opponent" in game_state.state and game_state.state[player]["length"] <= game_state.state[opponent]["length"]:
        opp_head = game_state.state[opponent]["body"][0]
        opp_head_x = opp_head["x"]
        opp_head_y = opp_head["y"]
        x = coords["x"]
        y = coords["y"]
        dist = get_manhattan_distance(x, y, opp_head_x, opp_head_y)
        if dist <= 1:
            reward += AVOID_HEAD_REWARD

    # Penalty if the snake is moving into a dangerous enclosed space
    snake_size = game_state.state[player_turn.value]["length"]
    if not can_fit(game_state.state, snake_size, coords):
        reward += DANGEROUS_ENCLOSED_SPACE_REWARD

    # Penalty if the snake is moving towards the edge of the board
    if coords["x"] == 0 or coords["x"] == game_state.state["board"]["width"] - 1 or coords["y"] == 0 or coords["y"] == game_state.state["board"]["height"] - 1:
        reward += AVOID_EDGE_REWARD

    return reward

def simplify_snake(snake: Dict[str, Any]) -> Dict[str, Any]:
    """Simplies the snake object to only contain the relevant information

    Args:
        snake: The snake to simplify

    Returns:
        The simplified snake
    """
    simplified_snake = {
        "health": snake["health"],
        "body": snake["body"],
        "length": snake["length"],
        "latency": snake["latency"],
        "health": snake["health"],
    }
    return simplified_snake

def simplify_game_state(game_state: Dict[str, Any]) -> Dict[str, Any]:
    """Takes the game state sent by the Battlesnake server and simplifies it to only contain the relevant information

    Args:
        game_state: The game state to simplify

    Returns:
        The simplified game state
    """
    simplified_game_state = {
        "turn": game_state["turn"],
        "timeout": game_state["game"]["timeout"],
        "board": {
            "height": game_state["board"]["height"],
            "width": game_state["board"]["width"],
            "food": game_state["board"]["food"],
        },
        "you": simplify_snake(game_state["you"]),
    }

    if len(game_state["board"]["snakes"]) > 1:
        simplified_game_state["opponent"] = simplify_snake(game_state["board"]["snakes"][1])

    return simplified_game_state

def move_snake(game_state: Dict[str, Any], direction: Direction, player: Player) -> Dict[str, Any]:
    """Generates a state that is the result of moving the snake in the given direction

    Args:
        game_state: The initial state of the game
        direction: The direction to move in
        player: The player that is making the move

    Returns:
        The state that is the result of moving the snake in the given direction
    """
    new_head_coord = get_snake_move_coord(game_state, direction, player)

    new_game_state = deepcopy(game_state)
    new_game_state[player.value]["body"].insert(0, new_head_coord) 
    # If there's a food at the location that the snake is moving to, remove it and extend the snake's length
    if new_head_coord not in new_game_state["board"]["food"]:
        new_game_state[player.value]["body"].pop()
    else:
        new_game_state['board']['food'].remove(new_head_coord)
        new_game_state[player.value]["length"] += 1
    return new_game_state

def visualize_game_state(game_state: State, max_depth: int = NUM_LAYERS):
    from graphviz import Digraph
    from collections import deque

    dot = Digraph(comment='Game State')
    
    q: deque[Tuple[State, int]] = deque([(game_state, 0)])

    while len(q) > 0:
        state, depth = q.popleft()
        if depth >= max_depth:
            break

        snake_positions = f"{state.state['you']['body'][0]}"
        if "opponent" in state.state:
            snake_positions += f"\n{state.state['opponent']['body'][0]}"

        dot.node(str(id(state)), f"Snake heads: {snake_positions}\nReward: {state.reward:3f}\nMove: {state.move_made}\nPlayer: {state.player_turn.value}")
        next_depth = depth + 1
        if next_depth >= max_depth:
            continue
        for next_state in state.next_states:
            q.append((next_state, next_depth))
            dot.edge(str(id(state)), str(id(next_state)))

    dot.render('game_state.gv', view=True)
    
def aggression_reward(game_state: State, player: Player) -> float:
    
    player_x = game_state.state[Player.YOU.value]["body"][0]["x"]
    player_y = game_state.state[Player.YOU.value]["body"][0]["y"]


    opp_x = game_state.state[Player.OPPONENT.value]["body"][0]["x"]
    opp_y = game_state.state[Player.OPPONENT.value]["body"][0]["y"]

    # will take tweaking to make sure it's not too aggressive
    curr_opp_value = Player.OPPONENT if player == Player.YOU else Player.YOU
    if game_state.state[curr_opp_value.value]["length"] < game_state.state[player.value]["length"]:
        return get_manhattan_distance(player_x, player_y, opp_x, opp_y)
    else:
        return 0

# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server

    run_server({"info": info, "start": start, "move": move, "end": end},  8080)
