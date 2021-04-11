import json
from collections.abc import Iterable
import random
from time import time

def get_model_from_file(model_name="model.json"):
    with open(model_name, "r") as f:
        return json.load(f)

def get_model_template(learning_rate=0.1, discount_factor=0.5, epsilon=0.5):
    return {
        'params': {
            'learning_rate': learning_rate,
            'discount_factor': discount_factor,
            'epsilon': epsilon,
        },
        'q_table': {},
    }

def get_model_template_sqlite(learning_rate=0.1, discount_factor=0.5, epsilon=0.5, sqlitedb='./qtable.sqlite'):
    from sqlitedict import SqliteDict
    return {
        'params': {
            'learning_rate': learning_rate,
            'discount_factor': discount_factor,
            'epsilon': epsilon,
        },
        'q_table': SqliteDict(sqlitedb, autocommit=True),
    }

def write_model_to_file(model, model_name='model.json'):
    with open(model_name, "w+") as f:
        json.dump(model, f)

def train_model_once(model, gameclass):
    game = gameclass()
    p1 = True
    p1moves = []
    p2moves = []
    while not game.over:
        move = get_training_move(model, game)
        if p1:
            p1moves.append((str(game), move))
        else:
            p2moves.append((str(game), move))
        game.do_move(move)
        p1 = not p1
    
    train_callback(model, p1moves, p2moves, game.outcome())

def lists_are_equal(l1, l2):
    for a, b in zip(l1, l2):
        if isinstance(a, Iterable) and isinstance(b, Iterable):
            if not lists_are_equal(a, b):
                return False
        else:
            if a != b:
                return False
    return True

def train_callback(model, p1, p2, outcome):
    params = model["params"]
    learning_rate = params["learning_rate"]
    max_next = 0
    discount_factor = params["discount_factor"]
    q_table = model["q_table"]

    if outcome == None:
        return
    
    rewards = (1, -1) if outcome else (-1, 1)
    for reward, path in zip(rewards, (p1, p2)):
        for game, move in path:
            entries = q_table[str(game)]
            move_entry = None

            for entry in entries:
                if lists_are_equal(entry[0], move):
                    move_entry = entry 

            move_entry[1] = move_entry[1] + learning_rate * (
                reward + discount_factor * max_next - move_entry[1]
            )

            max_next = 0
            for entry in entries:
                if entry[1] > max_next:
                    max_next = entry[1]

def get_training_move(model, game):
    q_table = model["q_table"]
    epsilon = model["params"]["epsilon"]
    if str(game) not in q_table:
        q_table[str(game)] = [
                [move, 0] for move in game.get_playable_moves()
            ]
        return game.random_move()
    else:
        if random.random() > epsilon:
            return get_move(model, game)
        else:
            return game.random_move()
    
def get_move(model, game, approximator=None, random_override=False):
    q_table = model["q_table"]
    if not str(game) in q_table and approximator:
        if random_override:
            return game.random_move()
        else:
            return approximate(q_table, game, approximator)
    return  [
        x[0]
        for x in sorted(q_table[str(game)], reverse=True, key=lambda x: x[1])
    ][0]

def approximate(q_table, game, approximator):
    moves = game.get_playable_moves()
    move_scores = [[move, [0,0]] for move in moves]
    ngame =  (str(game), move_scores)
    for entry in q_table.items():
        approximator(entry, ngame)
    move_scores.sort(key=lambda ms: ms[1][0] / ms[1][1] if ms[1][1] > 0 else 0, reverse=True)
    return move_scores[0][0]

def play_test(model, gameclass, p1=True):
    game = gameclass()
    if not p1:
        game.do_move(get_move(model, game, approximator=gameclass.approximator))
    while not game.over:
        print(game.__repr__())
        moves = game.get_playable_moves()
        for i, move in enumerate(moves):
            print(f"{i+1}: {move}")
        sel = int(input("Select a move: "))
        game.do_move(moves[sel-1])
        if game.over:
            break
        tmove = get_move(model, game, approximator=gameclass.approximator)
        game.do_move(tmove)
        print(f"Computer played: {tmove}")
    print(f"Winner is {game.winner}")

def random_test(model, gameclass, p1=True, random_override=False, verbose=False):
    start = time()
    game = gameclass()
    if not p1:
        if verbose:
            print("Model is black")
        game.do_move(get_move(model, game, approximator=gameclass.approximator, random_override=random_override))
    else:
        if verbose:
            print("Model is white")
    while not game.over:
        game.do_move(game.random_move())
        if game.over:
            break
        game.do_move(get_move(model, game, approximator=gameclass.approximator, random_override=random_override))
    if verbose:
        print(f"Winner is {game.winner}")
    return p1 == (game.winner == 'white'), time() - start

if __name__ == '__main__':
    pass
