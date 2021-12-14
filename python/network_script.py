import sys

import gym
import os
import gym_space_docking
# include Network
import tensorflow as tf
import numpy as np

## !pip install -e ../gym_space_docking/

loc = os.popen('pip3 show gym_space_docking').readlines()[7].split()[1]


sys.path.append(loc)

while True:
    tf.compat.v1.reset_default_graph()
    

    env = gym.make('space_docking-v0')
    env.reset()


    def preprocess_observations(obs):
        # ToDo need love to work
        img = obs
        img = img.mean(axis=2)
        img = (img - 128) / 128 -1

        return img.reshape(88,80,1)
        

    # create network
    input_height = 88
    input_width = 80
    input_channels = 1
    conv_n_maps = [32,64,64]
    conv_kernel_sizes = [(8,8), (4,4), (3,3)]
    conv_strides = [4, 2, 1]
    conv_paddings = ['SAME'] * 3
    conv_activation = [tf.nn.relu] * 3
    n_hidden_in = 64 * 11 * 10 # 64 maps with size 11x10
    n_hidden = 512
    hidden_activation = tf.nn.relu
    n_outputs = env.action_space.n# -> ToDo define in enviroment 
    initializer =  tf.keras.initializers.VarianceScaling()# tf.contrib.layers.variance_scaling_initializer()

    learning_rate = 0.01



    tf.compat.v1.disable_eager_execution()

    def q_network(X_state, name):
        prev_layer = X_state
        with tf.compat.v1.variable_scope(name) as scope:
            for n_maps, kernel_size, strides, padding, activation in zip(
                conv_n_maps, conv_kernel_sizes, conv_strides,
                conv_paddings, conv_activation):
                
                prev_layer = tf.compat.v1.layers.conv2d(
                    prev_layer, filters=n_maps, kernel_size= kernel_size,
                    strides= strides, padding=padding, activation=activation,
                    kernel_initializer= initializer)
                
                last_conv_layer_flat = tf.reshape(prev_layer, shape=[-1, n_hidden_in])
                
                hidden = tf.compat.v1.layers.dense(last_conv_layer_flat, n_hidden, 
                                                    activation=hidden_activation,
                                                    kernel_initializer=initializer)
                
                outputs = tf.compat.v1.layers.dense(hidden, n_outputs, 
                                                    kernel_initializer=initializer)
            
            trainable_vars = tf.compat.v1.get_collection(tf.compat.v1.GraphKeys.TRAINABLE_VARIABLES, 
                                                        scope=scope.name)
            
            trainable_vars_by_name = {var.name[len(scope.name):] : var for var in trainable_vars}

            return outputs, trainable_vars_by_name
                
    X_state = tf.compat.v1.placeholder(tf.float32, shape=[None, input_height, input_width, input_channels])
    online_q_values, online_vars = q_network(X_state=X_state, name='q_networks/online')
    target_q_values, target_vars = q_network(X_state=X_state, name='q_networks/target')

    copy_obs = [target_var.assign(online_vars[var_name]) for var_name, target_var in target_vars.items()]
    copy_online_to_target = tf.group(*copy_obs)

    X_action = tf.compat.v1.placeholder(tf.int32, shape=[None])
    q_value = tf.reduce_sum(target_q_values * tf.one_hot(X_action, n_outputs), axis=1, keepdims=True)

    y = tf.compat.v1.placeholder(tf.float32, shape=[None, 1])
    error = tf.abs(y - q_value)
    clipped_error = tf.clip_by_value(error, 0.0, 1.0)
    linear_error = 2*(error - clipped_error)
    loss = tf.compat.v1.reduce_mean(tf.square(clipped_error) +linear_error)

    global_step = tf.Variable(0, trainable=False, name='global_step')
    optimizer = tf.compat.v1.train.MomentumOptimizer(learning_rate=learning_rate,name='momentum', momentum=0.9, use_nesterov=True)
    training_op = optimizer.minimize(loss, global_step=global_step)

    init = tf.compat.v1.global_variables_initializer()
    saver = tf.compat.v1.train.Saver()

    from collections import deque

    replay_memory_size = 500000
    replay_memory = deque([], maxlen=replay_memory_size)

    def sample_memories(batch_size):
        indicies = np.random.permutation(len(replay_memory))[:batch_size]
        cols = [[], [], [], [], []] # state, action, rewards, next_state, continue
        for idx in indicies:
            memory = replay_memory[idx]
            for col, value in zip(cols, memory):
                col.append(value)
        cols = [np.array(col) for col in cols]
        return (cols[0], cols[1], cols[2].reshape(-1, 1), cols[3], cols[4].reshape(-1,1))

    # actor explore enviroment

    eps_min = 0.1
    eps_max = 1.0
    eps_decay_steps = 2000000

    def epsilon_greedy(q_values, step):
        epsilon = max(eps_min, eps_max - (eps_max-eps_min) * step/eps_decay_steps)
        if np.random.rand() < epsilon:
            return np.random.randint(n_outputs)
        else:
            return np.argmax(q_values)


    n_steps = 400000
    training_start = 10000
    training_interval = 4
    save_steps = 500
    copy_steps = 500
    discont_rate = 0.99
    skip_start = 90
    batch_size = 50
    iteration = 0
    checkpoint_path = './docking_dqn.ckpt'
    done = True
    rewards_counter = []
    reward = 0


    running = True




    
    with tf.compat.v1.Session() as sess:
        if os.path.isfile(checkpoint_path + '.index'):
            print('restore session')
            saver.restore(sess, checkpoint_path)
        else:
            init.run()
            copy_online_to_target.run()
        
        while True:
            step = global_step.eval()
            if step >= n_steps:
                break
            iteration += 1
            if done:
                
                if step > skip_start:
                    print('episode', step, 'iteration', iteration ,'rewards', reward)


                obs = env.reset()
                for skip in range(skip_start):
                    obs, reward, done, info = env.step(0)
                state = preprocess_observations(obs)

            # online dqn evaluate
            q_values = online_q_values.eval(feed_dict={X_state: [state]})
            action = epsilon_greedy(q_values, step)

            # online dqn play
            obs, reward, done, info = env.step(action)
            next_state = preprocess_observations(obs)

            rewards_counter.append(rewards_counter)

            # remember what happend
            replay_memory.append((state, action, reward, next_state, 1.0 - done))
            state = next_state
            

            if iteration < training_start or iteration % training_interval != 0:
                continue # only train after warmup period and at regular intervals

            # get probe from memory
            # use target dqn to get target q value
            X_state_val, X_action_val, rewards, X_next_state_val, continues = (
                sample_memories(batch_size=batch_size))
            
            next_q_values = target_q_values.eval(
                feed_dict={X_state: X_state_val})

            max_next_q_values = np.max(next_q_values, axis=1, keepdims=True)
            y_val = rewards + continues * discont_rate * max_next_q_values

            # train online dqn
            training_op.run(feed_dict={X_state: X_state_val, X_action: X_action_val, y: y_val})

            # copy online dqn to target dqn
            if step % copy_steps == 0:
                print('copy network to target network')
                copy_online_to_target.run()
            
            # save regulary
            if step % save_steps == 0:
                print('save checkpoint')
                saver.save(sess, checkpoint_path)
                break

            