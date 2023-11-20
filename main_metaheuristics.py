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

import random
import typing
import copy


# info is called when you create your Battlesnake on play.battlesnake.com
# and controls your Battlesnake's appearance
# TIP: If you open your Battlesnake URL in a browser you should see this data
def info() -> typing.Dict:
    print("INFO")

    return {
        "apiversion": "1",
        "author": "",  # TODO: Your Battlesnake Username
        "color": "#888888",  # TODO: Choose color
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

    max = -1
    next_move = "down"
    num_steps = len(game_state["you"]["body"])
    runner = 0
    while max == -1 and runner < 5:
        if num_steps == 2:
            runner += 1

        moves = [generate_moves(game_state,num_steps),
                 generate_moves(game_state,num_steps),
                 generate_moves(game_state,num_steps),
                 generate_moves(game_state,num_steps),
                 generate_moves(game_state,num_steps),
                 generate_moves(game_state,num_steps)]
    
        move_set = None
        for move in moves:
            if len(move) == 0:
                continue
            move_val = assess_cost(game_state, move)
            #print(move, move_val)
            if move_val > max:
                max = move_val
                next_move = move[0]
                move_set = None
            if move_val == max:
                if move_set is None:
                    move_set = [next_move, move[0]]   
                else:
                    move_set.append(move[0])
    
        if move_set is not None:
            next_move = random.choice(move_set)
        num_steps = num_steps - 1 if num_steps > 2 else num_steps
    
    print(f"MOVE {game_state['turn']}: {next_move}")
    return {"move": next_move}

def genetic_decider(game_state: typing.Dict, hyper_params: typing.Dict) -> typing.Dict:
    return {"move": "left"}

def generate_moves(game_state: typing.Dict, k: int) -> typing.List:
    moves = ["up","down","right","left"]
    x_max = game_state["board"]["width"] - 1
    y_max = game_state["board"]["height"] - 1
    body = copy.copy(game_state["you"]["body"])
    pos_x = copy.copy(body[0]["x"])
    pos_y = copy.copy(body[0]["y"])
    
    moves_out = []
    for k_i in range(k):
        safe_moves = copy.copy(moves)
        if pos_x == 0:
            safe_moves.remove("left")
        elif pos_x == x_max:
            safe_moves.remove("right")

        if pos_y == 0:
            safe_moves.remove("down")
        elif pos_y == y_max:
            safe_moves.remove("up")

        if k_i == 0:
            moves_out.append(random.choice(safe_moves))
        else:
            if "left" in safe_moves and (moves_out[-1] == "right" or is_in_body(body, [pos_x - 1, pos_y])):
                safe_moves.remove("left")
            if "right" in safe_moves and (moves_out[-1] == "left" or is_in_body(body, [pos_x + 1, pos_y])):
                safe_moves.remove("right")
            if "down" in safe_moves and (moves_out[-1] == "up" or is_in_body(body, [pos_x, pos_y - 1])):
                safe_moves.remove("down")
            if "up" in safe_moves and (moves_out[-1] == "down" or is_in_body(body, [pos_x, pos_y + 1])):
                safe_moves.remove("up")
            
            if len(safe_moves) == 0:
                return []
            moves_out.append(random.choice(safe_moves))
        
        if moves_out[-1] == "up":
            pos_y += 1
        elif moves_out[-1] == "down":
            pos_y -= 1
        elif moves_out[-1] == "right":
            pos_x += 1
        elif moves_out[-1] == "left":
            pos_x -= 1

        grow = False
        body.insert(0,{"x": pos_x, "y": pos_y})
        for food_pos in game_state["board"]["food"]:
            if food_pos["x"] == pos_x and food_pos["y"] == pos_y:
                grow = True
        if grow is False:
            body.pop()
        
    return moves_out



def is_in_body(body: typing.Dict, cell: typing.List) -> bool:
    for body_segment in range(len(body) - 1):
        if body[body_segment]["x"] == cell[0] and body[body_segment]["y"] == cell[1]:
            return True
    return False

def assess_cost(game_state: typing.Dict, proposed_moves: typing.List):
    if len(proposed_moves) == 0:
        return -1
    est_cost = 0
    grow = False
    x_max = game_state["board"]["width"] - 1
    y_max = game_state["board"]["height"] - 1
    body = copy.copy(game_state["you"]["body"])
    pos_x = copy.copy(body[0]["x"])
    pos_y = copy.copy(body[0]["y"])
    for move in proposed_moves:
        if move == "up":
            pos_y += 1
        elif move == "down":
            pos_y -= 1
        elif move == "right":
            pos_x += 1
        elif move == "left":
            pos_x -= 1

        if pos_y > y_max or pos_y < 0 or pos_x > x_max or pos_x < 0 or is_in_body(body, [pos_x, pos_y]):
            return -1

        body.insert(0,{"x": pos_x, "y": pos_y})
        for food_pos in game_state["board"]["food"]:
            if food_pos["x"] == pos_x and food_pos["y"] == pos_y:
                est_cost += 5
                grow = True
        if grow is False:
            body.pop()
        
        est_cost += 1
        
    return est_cost

# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server

    run_server({"info": info, "start": start, "move": move, "end": end})