import json
import random

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
                if entry[0] == move:
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
    if str(game) not in q_table.keys():
        q_table[str(game)] = [
                [move, 0] for move in game.get_playable_moves()
            ]
    if random.random() > epsilon:
        return get_move(model, game)
    else:
        return game.random_move()
    
def get_move(model, game):
    q_table = model["q_table"]
    return  [
        x[0]
        for x in sorted(q_table[str(game)], reverse=True, key=lambda x: x[1])
    ][0]

def playtest(model, gameclass, p1=True):
    game = gameclass()
    if not p1:
        game.do_move(get_training_move(model, game))
    while not game.over:
        print(game.__repr__())
        moves = game.get_playable_moves()
        for i, move in enumerate(moves):
            print(f"{i+1}: {move}")
        sel = int(input("Select a move: "))
        game.do_move(moves[sel-1])
        if game.over:
            break
        tmove = get_move(model, game)
        game.do_move(tmove)
        print(f"Computer played: {tmove}")

if __name__ == '__main__':
    import checkersgame
    from tqdm import tqdm
    import os
    if not os.path.isfile('model.json'):
        model = get_model_template()
    else:
        model = get_model_from_file()
    reps = 1000000
    model['params']['epsilon'] = 0.5
    model['params']['discount_factor'] = 0.1
    init_df = model['params']['discount_factor']
    for _ in tqdm(range(reps)):
        model['params']['discount_factor'] += (1/reps)*(1-init_df)
        train_model_once(model, checkersgame.Game)
    write_model_to_file(model)
    playtest(model, checkersgame.Game, p1=False)
    
