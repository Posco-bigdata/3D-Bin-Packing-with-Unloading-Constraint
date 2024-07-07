import numpy as np
import tensorflow as tf
from heuristics import PackingAlgorithm, Item
from unload import unload_items
from given_data import container_size, data
import json
import random

class ContainerEnvironment:
    def __init__(self, data, container_size):
        self.container_size = container_size
        self.items = [Item(int(key), value['width'], value['length'], value['height'], value['weight'], value['location'])
                      for key, value in data.items()]
        self.packing_algorithm = PackingAlgorithm(*container_size)
        self.state_shape = self.get_state().shape
        self.action_shape = len(self.items)  # 각 아이템의 배치 순서를 결정하는 액션

    def reset(self):
        random.shuffle(self.items)
        return self.get_state()

    def step(self, action):
        # action을 사용하여 아이템 순서 재배열
        self.items = [self.items[i] for i in action]
        
        self.packing_algorithm.pack_items_with_permutations(self.items)
        packed_items = self.packing_algorithm.best_packed_items

        # packed_items를 JSON으로 저장
        with open('packed_items.json', 'w') as f:
            json.dump(packed_items, f)

        # unload.py를 사용하여 언로딩 작업 횟수 계산
        total_operations, _ = unload_items(packed_items)

        # 보상 계산 (작업 횟수의 역수)
        reward = 1.0 / total_operations if total_operations > 0 else 0

        done = True  # 한 번의 배치로 에피소드 종료
        next_state = self.get_state()

        return next_state, reward, done

    def get_state(self):
        # 현재 아이템 순서를 상태로 사용
        return np.array([item.id for item in self.items])

class DQN(tf.keras.Model):
    def __init__(self, state_shape, action_shape):
        super(DQN, self).__init__()
        self.fc1 = tf.keras.layers.Dense(128, activation='relu')
        self.fc2 = tf.keras.layers.Dense(128, activation='relu')
        self.fc3 = tf.keras.layers.Dense(action_shape)

    def call(self, inputs):
        x = self.fc1(inputs)
        x = self.fc2(x)
        return self.fc3(x)

    def get_action(self, state, epsilon=0.1):
        if random.random() < epsilon:
            return list(range(len(state)))
        q_values = self(tf.convert_to_tensor([state], dtype=tf.float32))
        return tf.argsort(q_values[0]).numpy()

def train_model(env, model, num_episodes):
    optimizer = tf.keras.optimizers.Adam()
    loss_fn = tf.keras.losses.MeanSquaredError()
    
    for episode in range(num_episodes):
        state = env.reset()
        total_reward = 0

        with tf.GradientTape() as tape:
            action = model.get_action(state)
            next_state, reward, done = env.step(action)
            
            # Q-learning update
            q_values = model(tf.convert_to_tensor([state], dtype=tf.float32))
            next_q_values = model(tf.convert_to_tensor([next_state], dtype=tf.float32))
            target = reward + 0.99 * tf.reduce_max(next_q_values)
            
            # Compute loss
            loss = loss_fn(target, tf.reduce_max(q_values))

        # Gradient descent
        grads = tape.gradient(loss, model.trainable_variables)
        optimizer.apply_gradients(zip(grads, model.trainable_variables))

        total_reward += reward
        print(f"Episode {episode + 1}, Total Reward: {total_reward}, Loss: {loss.numpy()}")

    return model

# 메인 실행 부분
env = ContainerEnvironment(data, container_size)
model = DQN(env.state_shape, env.action_shape)
trained_model = train_model(env, model, num_episodes=1000)

# 학습된 모델을 사용하여 최종 배치 수행
final_state = env.reset()
final_action = trained_model.get_action(final_state, epsilon=0)
env.step(final_action)

print("최적화된 배치 완료. 'packed_items.json'에서 결과를 확인하세요.")