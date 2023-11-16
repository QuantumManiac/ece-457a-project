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


# move is called on every turn and returns your next move
# Valid moves are "up", "down", "left", or "right"
# See https://docs.battlesnake.com/api/example-move for available data
def move(game_state: typing.Dict) -> typing.Dict:
    game_state = simplify_game_state(game_state)
    state_tree = State(game_state, None, 0)

    # Are there any safe moves left?
    possible_moves = get_possible_moves(game_state)

    # create first layer
    for move in possible_moves:
        coords  = get_snake_move_coord(game_state, move)
        move_reward = coord_to_reward(game_state, coords['x'], coords['y'])

        state = State(move_snake(game_state, move), move, move_reward)
        state_tree.next_states.append(state)

    # create second layer
    for next_state in state_tree.next_states:
        next_possible_moves = get_possible_moves(next_state)        

        for move in next_possible_moves:
            coords  = get_snake_move_coord(next_state, move)
            move_reward = coord_to_reward(next_state, coords['x'], coords['y'])

            state = State(move_snake(next_state, move), move, move_reward)
            next_state.next_states.append(state)


    if len(possible_moves) == 0:
        print(f"MOVE {game_state['turn']}: No safe moves detected! Moving down")
        return {"move": "down"}

    move_rewards = {}

    for move in possible_moves:
        coords  = get_snake_move_coord(game_state, move)
        move_reward = coord_to_reward(game_state, coords['x'], coords['y'])
        move_rewards[move] = move_reward

    best_move = max(move_rewards, key=move_rewards.get)
    move_rewards_string = ' | '.join(f'{move}: {move_rewards[move]:2f}' for move in move_rewards)
    # print(f"{move_rewards_string} | MOVE {game_state['turn']}: {best_move}")
    print(move_snake(simplify_game_state(game_state), best_move))
    if game_state['turn'] == 5:
        exit(0)
    return {"move": best_move}


def get_possible_moves(game_state):
    safe_moves = set(['up', 'left', 'down', 'right'])
    # We've included code to prevent your Battlesnake from moving backwards
    my_head = game_state["you"]["body"][0]  # Coordinates of your head
    my_neck = game_state["you"]["body"][1]  # Coordinates of your "neck"

    # Check if snake goes out of bounds
    if my_head["x"] <= 0 :  # Neck is left of head, don't move left
        safe_moves.discard('left')

    if my_head["x"] >= game_state["board"]["width"]-1:  # Neck is right of head, don't move right
        safe_moves.discard('right')

    if my_head["y"] <= 0:  # Neck is below head, don't move down
        safe_moves.discard('down')

    if my_head["y"] >= game_state["board"]["height"]-1:  # Neck is above head, don't move up
        safe_moves.discard('up')

    safe_moves_temp = safe_moves.copy()

    # Check if snake hits its body
    for safe_move in safe_moves_temp:
        safe_move_coord = get_snake_move_coord(game_state, safe_move)
        for body_coords in game_state["you"]["body"][1:]:
            if safe_move_coord == body_coords:
                safe_moves.discard(safe_move)

    return safe_moves

def get_snake_move_coord(game_state, direction):
    snake_head_pos = game_state["you"]["head"]
    x = snake_head_pos['x']
    y = snake_head_pos['y']
    if direction == 'left':
        return {"x": x-1, "y": y}
    elif direction == 'down':
        return {"x": x, "y": y-1}
    elif direction == 'right':
        return {"x": x+1, "y": y}
    elif direction == 'up':
        return {"x": x, "y": y+1}
    else:
        raise Exception('Invalid direction')

def get_manhattan_distance(x1: int, y1: int, x2: int, y2: int) -> int:
    return abs(x2 - x1) + abs(y2 - y1)

def get_pythagorean_distance(x1: int, y1: int, x2: int, y2: int) -> int:
    return math.sqrt( (x2 - x1) ** 2 + (y2 - y1) ** 2 )
    
def coord_to_reward(game_state, x, y):
    reward = 0
    
    for food_coord in game_state["board"]["food"]:
        food_x = food_coord["x"]
        food_y = food_coord["y"]
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
            "snakes": [simplify_snake(snake) for snake in game_state["board"]["snakes"][1:]], 
        },
        "you": simplify_snake(game_state["you"]),
    }

    return simplified_game_state

def move_snake(game_state, direction):

    new_head_coord  = get_snake_move_coord(game_state, direction)

    game_state["you"]["body"].insert(0, new_head_coord)
        
    # If there's a food at the location that the snake is moving to, remove it and extend the snake's length
    if new_head_coord not in game_state["board"]["food"]:
        game_state["you"]["body"].pop()
    else:
        game_state['board']['food'].remove(new_head_coord)

    return game_state

def generate_next_game_states(current_game_state, possible_moves):
    next_game_states = {}
    for move in possible_moves:
        next_game_states[move] = next_game_state(current_game_state, move)

def next_game_state(simplified_game_state, move):
    move_coord = get_snake_move_coord(simplified_game_state, move)
    return [(move_snake(simplified_game_state, move), coord_to_reward(move_coord['x'], move_coord['y']))]

class State:
    def __init__(self, state, direction, reward) -> None:
        self.state = state
        self.reward = reward
        self.direction = direction
        self.next_states = []

# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server

    run_server({"info": info, "start": start, "move": move, "end": end})
