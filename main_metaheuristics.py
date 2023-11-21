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
import subprocess
import threading
import time
import sys


class Global:
    hyper_paramerters: typing.Dict = {'value': {'iter': 10, 'mutation_prob': 0.3},
                                      'range': {'iter': [1, 100], 'mutation_prob': [0.0, 1.0]}}
    snake_performance: typing.Dict = {'turns_alive': 0, 'num_kills': 0, 'snake_size': 1, 'avg_health': 100, 'won_game': False}

    @classmethod
    def reset_snake_performance(cls):
        cls.snake_performance = {'turns_alive': 0, 'num_kills': 0, 'snake_size': 1, 'avg_health': 100, 'won_game': False}

    @classmethod
    def get_hyper_parameters(cls):
        return cls.hyper_paramerters
    
    @classmethod
    def set_hyper_parameters(cls, hyper_params: typing.Dict):
        cls.hyper_paramerters = hyper_params
    
    @classmethod
    def get_snake_performance(cls):
        return cls.snake_performance


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

    # iter, mutation_prob = 10, 0.3
    hyper_params = Global.get_hyper_parameters()['value']
    iter, mutation_prob = hyper_params["iter"], hyper_params["mutation_prob"]

    max_while = 25
    best_move_set, best_cost = None, -1
    safe_moves = [generate_moves(game_state,1),
                  generate_moves(game_state,1),
                  generate_moves(game_state,1),
                  generate_moves(game_state,1),
                  generate_moves(game_state,1),
                  generate_moves(game_state,1),
                  generate_moves(game_state,1),
                  generate_moves(game_state,1)]

    while best_move_set is None and max_while > 0:
        for i in range(iter):
            max = -1
            next_move = "down"
            num_steps = len(game_state["you"]["body"])

            if best_move_set is None:
                moves = [generate_moves(game_state,num_steps),
                         generate_moves(game_state,num_steps),
                         generate_moves(game_state,num_steps),
                         generate_moves(game_state,num_steps),  
                         generate_moves(game_state,num_steps),
                         generate_moves(game_state,num_steps)]
            else:
                moves = [best_move_set,
                         generate_moves(game_state,num_steps),
                         generate_moves(game_state,num_steps),
                         generate_moves(game_state,num_steps),
                         mutate(best_move_set, mutation_prob),
                         mutate(best_move_set, mutation_prob),
                         mutate(best_move_set, mutation_prob)]
        
            for move in moves:
                if len(move) == 0:
                    continue
                move_val = assess_cost(game_state, move)
                if move_val > max:
                    max = move_val
                    best_move_set = copy.copy(move)
                    best_cost = move_val

        max_while -= 1

    if best_move_set is not None:
        next_move = best_move_set[0]
    else:
        next_move = random.choice(safe_moves)
        next_move = next_move[0]  

    print(f"MOVE {game_state['turn']}: {next_move}")
    return {"move": next_move}

def mutate(best_moves: typing.List, mutation_prob: float) -> typing.List:
    if len(best_moves) <= 2:
        return best_moves
    random_moveset = ["up", "down", "left", "right"]
    mutation_point = random.choice([*range(len(best_moves) - 1)])
    mutation_point = 1 if mutation_point == 0 else (len(best_moves) - 2 if mutation_point == len(best_moves) - 1 else 1)

    if best_moves[mutation_point + 1] == "left" or best_moves[mutation_point - 1] == "left":
        random_moveset.remove("right")
    elif best_moves[mutation_point + 1] == "right" or best_moves[mutation_point - 1] == "right":
        random_moveset.remove("left")
    elif best_moves[mutation_point + 1] == "up" or best_moves[mutation_point - 1] == "up":
        random_moveset.remove("down")
    elif best_moves[mutation_point + 1] == "down" or best_moves[mutation_point - 1] == "down":
        random_moveset.remove("up")
    
    if random.uniform(0,1) > mutation_point:
        best_moves[mutation_point] = random.choice(random_moveset)
    
    return best_moves

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
                return moves_out
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

def enemy_proximity(game_state: typing.Dict, cell: typing.List) -> int:
    ret = 0
    for enemy in game_state["board"]["snakes"]:
        if enemy["name"] == game_state["you"]["name"]:
            continue
        
        if ret == 2 or ret == 3:
            return ret
        
        e_bod = enemy["body"]
        for seg_i in range(len(e_bod)):
            if cell[0] == e_bod[seg_i]["x"] and cell[1] == e_bod[seg_i]["y"]:
                ret = 2 # Indicate a potential body collision
            if seg_i == 0:
                if (abs(cell[0] - e_bod[seg_i]["x"]) == 1 and cell[1] == e_bod[seg_i]["y"]) or (abs(cell[1] - e_bod[seg_i]["y"]) == 1 and cell[0] == e_bod[seg_i]["x"]):
                    if ret != 2:
                        ret = 1 # Indicate adjacency risk but don't override collision
                    if len(e_bod) < len(game_state["you"]["body"]):
                        ret = 3 # Indicate that you want to eat them as a nice little treat
    return ret

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

        adj_risk = enemy_proximity(game_state, [pos_x, pos_y])

        if pos_y > y_max or pos_y < 0 or pos_x > x_max or pos_x < 0 or is_in_body(body, [pos_x, pos_y]) or adj_risk == 2:
            return -1

        if adj_risk == 1:
            est_cost -= 8
        elif adj_risk == 3:
            est_cost += 15

        body.insert(0,{"x": pos_x, "y": pos_y})
        for food_pos in game_state["board"]["food"]:
            if food_pos["x"] == pos_x and food_pos["y"] == pos_y:
                est_cost += 5
                grow = True
        if grow is False:
            body.pop()
        
        est_cost += 1

    return est_cost

def calculate_fitness(win_time_gain, survival_time_gain, kill_gain, avg_health_gain, won_game: bool):
    a = 0 if not won_game else a
    b = 0 if won_game else b
    snake_performance = Global.get_snake_performance()

    return (win_time_gain / snake_performance['turns_alive']) + \
            survival_time_gain*snake_performance["turns_alive"] + \
            kill_gain*snake_performance["snake_size"] + \
            avg_health_gain*snake_performance['avg_health']

def hyper_parameter_local_search(iter_per_set, total_iter):
    # Cost function gain parameters
    WIN_TIME_GAIN = 1
    SURVIVAL_TIME_GAIN = 1
    KILL_GAIN = 1
    SIZE_GAIN = 1
    AVG_HEALTH_GAIN = 1

    hyper_parameters = Global.get_hyper_parameters()

    # set initial hyperparams
    

    # get fitness for initial params
    Global.set_hyper_parameters(hyper_parameters)

    # run for a set number of iterations

    calculate_fitness(WIN_TIME_GAIN, SURVIVAL_TIME_GAIN, KILL_GAIN, SIZE_GAIN, AVG_HEALTH_GAIN)


    return hyper_parameters

def run_game(run_in_browser: bool):
    command = [
        './battlesnake', 'play',
        '--name', 'meta_snake',
        '--url', 'http://127.0.0.1:8000',
    ]

    command += '--browser' if run_in_browser else command
    subprocess.run(command)

# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server
    HYPER_PARAMETER_OPTIMIZATION = False
    # Add more parameters for more fitness function variables


    server_thread = threading.Thread(target=run_server, args=({"info": info, "start": start, "move": move, "end": end},))
    server_thread.start()
    time.sleep(0.1)

    if HYPER_PARAMETER_OPTIMIZATION == False:
        run_game(run_in_browser=True)
        sys.exit()

    INNER_LOOP_ITERATIONS = 10
    OUTER_LOOP_ITERATIONS = 100

    hyper_parameter_local_search(INNER_LOOP_ITERATIONS, OUTER_LOOP_ITERATIONS)

    for _ in range(3):
        run_game(False)
        Global.hyper_paramerters['value']['mutation_prob'] += 0.3
        Global.reset_snake_performance()
