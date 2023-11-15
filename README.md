# ECE457A Project

## Requirements

Running everything on this repo requires:

- Python 3 for running the the snake logic
- Go for running the Battlesnake game server locally

## Getting Started

### Setting up the Project

Instructions for setting up the repo is as follows

```sh
# Clone the repo
git clone https://github.com/QuantumManiac/ece-457a-project
cd ece-457a-project

# Install the battlesnake game engine (added as a git submodule)
git submodule init
git submodule update

# Create a virtualenv
python -m venv venv

# Activate the virtualenv...
# ...on MacOS/Linux
source ./venv/bin/activate
# ...or on Windows
source ./venv/bin/activate.ps1

# Install dependencies
pip install -r requirements.txt

# Build the binaries for the battlesnake engine
cd rules && go build -o ../battlesnake ./cli/battlesnake/main.go
```

### Running the Snakes

#### Everything all at once

The following command run from the repo's root directory will start a game of battlesnake pitting the two battlesnakes against each other. Note that this will start the game server and the two snakes all in one command,

```sh
PORT=8080 python main_game_theory.py & PORT=8081 python main_metaheuristics.py & sleep 1 && ./battlesnake play --name game-theory --url http://127.0.0.1:8080 --name metaheuristics --url http://127.0.0.1:8081 --browser
```

#### Running the snakes

Make sure to run the snakes before the server is started.

```sh
# Run the game theory snake
PORT=8080 python main_game_theory.py

# Run the metaheuristics snake
PORT=8081 python main_metaheuristics.py
```

#### Running the game server

```sh
./battlesnake play --name game-theory --url http://127.0.0.1:8080 --name metaheuristics --url http://127.0.0.1:8081 --browser
```
