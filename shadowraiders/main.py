import random
import numpy as np
from game.env import MyEnv

env=MyEnv(verbose = False)

def test_models(env, num_episodes=10000):
    total_reward = 0
    total_info = np.array([0.0,0.0,0.0])
    total_estimate = 0

    for episode in range(num_episodes):
        done = False
        reward = 0
        episode_reward = 0
        episode_info = [0.0,0.0,0.0]
        env.reset()  
        

        # 4つの要素をランダムに選び、配列に追加
        options = [
            [0, 0, 1],
            [0, 1, 0],
            [1, 0, 0]
        ]

        # 配列を選択する確率
        weights = [0.25, 0.5, 0.25]

        # 選択された配列を格納するリスト
        chosen_arrays = []

        # 4回繰り返す
        for _ in range(4):
            # 配列をランダムに選択
            chosen_array = random.choices(options)[0]
            # 選択された配列をリストに追加
            chosen_arrays.append(chosen_array)
        action = [item for sublist in chosen_arrays for item in sublist]
            
        count = 0
        while not done:
            count += 1

            # 環境内でアクションを実行
            next_state, reward, done, info = env.step(action, estimation_precision=0)

            # 次の状態を新しい状態として設定
            state = next_state
            
            if info is not None: 
                correct = info[0]
                estimate = info[1]
                correct[1] = correct[1]/2
                episode_info = np.add(episode_info, correct)
            
        total_reward += reward
        total_info += episode_info
        total_estimate += estimate
        total_info += episode_info/4
        
    print(f"reward: {total_reward/num_episodes}")
    print(f"info: {total_info/num_episodes}")
    print(f"estimate {total_estimate/num_episodes}")

if __name__ == "__main__":
    test_models(env)
