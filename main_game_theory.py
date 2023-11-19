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

import typing
import math
import enum

NUM_LAYERS = 2
LAYER_REWARD_DECAY = 0.5

class Player(enum.Enum):
    YOU = 'you'
    OPPONENT = 'opponent'

class Direction(enum.Enum):
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"

# info is called when you create your Battlesnake on play.battlesnake.com
# and controls your Battlesnake's appearance
# TIP: If you open your Battlesnake URL in a browser you should see this data
def info() -> typing.Dict:
    print("INFO")

    return {
        "apiversion": "1",
        "author": "",  # TODO: Your Battlesnake Username
        "color": "#800080",  # TODO: Choose color
        "head": "default",  # TODO: Choose head
        "tail": "default",  # TODO: Choose tail
    }


# start is called when your Battlesnake begins a game
def start(game_state: typing.Dict):
    print("GAME START")


# end is called when your Battlesnake finishes a game
def end(game_state: typing.Dict):
    print("GAME OVER\n")


def generate_state_tree(root_state, layers):
    if layers == 0:
        return root_state

    player_turn = root_state.player_turn
    if "opponent" in root_state.state:
        next_player_turn = Player.OPPONENT if player_turn == Player.YOU else Player.YOU
    else:
        next_player_turn = player_turn

    next_possible_moves = get_possible_moves(root_state.state, next_player_turn)

    for next_move in next_possible_moves:
        coords = get_snake_move_coord(root_state.state, next_move, next_player_turn)
        move_reward = coord_to_reward(root_state.state, coords, next_player_turn)
        next_state = move_snake(root_state.state, next_move, next_player_turn)
        state = State(next_state, next_move, move_reward, next_player_turn)
        root_state.next_states.append(state)

    for next_state in root_state.next_states:
        generate_state_tree(next_state, layers-1)

    return root_state

def get_max_reward(state):
    if len(state.next_states) == 0:
        return state.reward
    # We have a LAYER_REWARD_DECAY multiplier here to put higher value to sooner rewards than later ones
    return state.reward + LAYER_REWARD_DECAY * max(get_max_reward(next_state) for next_state in state.next_states)
        
def get_best_move(state_tree):
    if len(state_tree.next_states) == 0:
        return None

    best_move = max(state_tree.next_states, key=get_max_reward).direction

    return best_move
    

# move is called on every turn and returns your next move
# Valid moves are "up", "down", "left", or "right"
# See https://docs.battlesnake.com/api/example-move for available data
def move(game_state: typing.Dict) -> typing.Dict:
    game_state = simplify_game_state(game_state)
    state_tree = State(game_state, None, 0, Player.YOU)
    generate_state_tree(state_tree, NUM_LAYERS)

    # Are there any safe moves left?
    best_move = get_best_move(state_tree)

    if best_move is None:
        print(f"MOVE {game_state['turn']}: No safe moves detected! Moving down")
        return {"move": Direction.DOWN.value}

    # move_rewards_string = ' | '.join(f'{move}: {move_rewards[move]:2f}' for move in move_rewards)
    # print(f"{move_rewards_string} | MOVE {game_state['turn']}: {best_move}")
    # print(move_snake(simplify_game_state(game_state), best_move))
    return {"move": best_move}


def get_possible_moves(game_state, player: Player):
    possible_moves = [direction.value for direction in Direction]
    safe_moves = possible_moves.copy()

    # Discard move if it makes snake hit its body
    for move in possible_moves:
        move_coord = get_snake_move_coord(game_state, move, player)
        for body_coords in game_state[player.value]["body"][1:]:
            if move_coord == body_coords:
                safe_moves.discard(move)

    return safe_moves

def get_snake_move_coord(game_state, direction, player: Player):
    snake_head_pos = game_state[player.value]["head"]

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
        raise Exception('Invalid direction')

def get_manhattan_distance(x1: int, y1: int, x2: int, y2: int) -> int:
    return abs(x2 - x1) + abs(y2 - y1)

def get_pythagorean_distance(x1: int, y1: int, x2: int, y2: int) -> int:
    return math.sqrt( (x2 - x1) ** 2 + (y2 - y1) ** 2 )
    
def coord_to_reward(game_state, coords, player_turn: Player):
    reward = 0
    
    for food_coord in game_state["board"]["food"]:
        food_x = food_coord["x"]
        food_y = food_coord["y"]
        x = coords["x"]
        y = coords["y"]
        dist = get_manhattan_distance(x, y, food_x, food_y)

        if dist == 0:
            reward += 1
        else:
            reward += 1/dist


    return reward

def simplify_snake(snake):
    simplified_snake = {
        "health": snake["health"],
        "body": snake["body"],
        "head": snake["head"],
        "length": snake["length"],
    }
    return simplified_snake

def simplify_game_state(game_state):
    simplified_game_state = {
        "turn": game_state["turn"],
        "board": {
            "height": game_state["board"]["height"],
            "width": game_state["board"]["width"],
            "food": game_state["board"]["food"],
        },
        "you": simplify_snake(game_state["you"]),
    }

    if len(game_state["board"]["snakes"]) > 1:
        game_state["opponent"] = simplify_snake(game_state["board"]["snakes"][1]),

    return simplified_game_state

def move_snake(game_state, direction, player: Player):

    new_head_coord = get_snake_move_coord(game_state, direction, player)

    game_state[player.value].insert(0, new_head_coord)
        
    # If there's a food at the location that the snake is moving to, remove it and extend the snake's length
    if new_head_coord not in game_state["board"]["food"]:
        game_state[player.value]["body"].pop()
    else:
        game_state['board']['food'].remove(new_head_coord)

    return game_state

class State:
    def __init__(self, state, move_made, reward, player_turn: Player) -> None:
        self.state = state
        self.player_turn = player_turn
        self.reward = reward
        self.move_made = move_made
        self.next_states = []

# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server

    run_server({"info": info, "start": start, "move": move, "end": end})
