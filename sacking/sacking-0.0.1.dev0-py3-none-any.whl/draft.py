


env = Env()

buf = deque()


# initial random exploration
random_policy(buf, env)


# init model
policy = ...
q_network = ...
optimizers = ...

for step in range(1000000):
    batch = sample_batch(buf)
    update_model(policy, q_network, optimizers)
    evaluate(...)
    generate episode
    save checkpoint

XXXXXXXXXXXX

policy API


gaussian trainer:
1. run policy batched, get reparametrized samples and log probs, both differentiable
2. choose one noisy action, not differentiable

gaussian evaluator:
1. choose one best action, not differentiable


discrete trainer:
1. run policy batched, get (categorical) distribution, differentiable
2. choose one noisy action, not differentiable

discrete evaluator:
1. choose one best action, not differentiable

gaussian trainer:

