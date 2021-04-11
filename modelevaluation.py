import train
import sys
import checkersgame
from tqdm import tqdm
from statistics import mean, stdev

def train_and_test(reps, kto, testgames):
    print(f"Training {reps} reps and playing {testgames} testgames.")
    model = train.get_model_template()
    model['params']['epsilon'] = 0.5
    model['params']['discount_factor'] = 0.1
    init_df = model['params']['discount_factor']
    print("Training")
    for _ in tqdm(range(reps)):
        model['params']['discount_factor'] += (1/reps)*(1-init_df)
        train.train_model_once(model, checkersgame.Game())

    results = []
    times = []
    print("Playing kto")
    for i in tqdm(range(testgames)):
        r, t = train.random_test(model, checkersgame.Game, p1=i > (testgames/2), keep_training_override=kto)
        results.append(r)
        times.append(t)
    print(f"Won {sum(results)}/{testgames} games, average time of {mean(times)} with stdev {stdev(times)}")

    results = []
    times = []
    print("Playing model")
    for i in tqdm(range(testgames)):
        r, t = train.random_test(model, checkersgame.Game, p1=i > (testgames/2))
        results.append(r)
        times.append(t)
    print(f"Won {sum(results)}/{testgames} games, average time of {mean(times)} with stdev {stdev(times)}")


    results = []
    times = []
    print("Playing random")
    for i in tqdm(range(testgames)):
        r, t = train.random_test(model, checkersgame.Game, p1=i > (testgames/2), random_override=True)
        results.append(r)
        times.append(t)
    print(f"Won {sum(results)}/{testgames} games, average time of {mean(times)} with stdev {stdev(times)}")


if __name__ == '__main__':
    trains = int(sys.argv[1])
    kto = int(sys.argv[2])
    tests = int(sys.argv[3])
    train_and_test(trains, kto, tests)