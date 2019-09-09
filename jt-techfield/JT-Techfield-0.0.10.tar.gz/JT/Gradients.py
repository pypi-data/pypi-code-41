"""
Jacob Thompson

Gradients.py
"""

import numpy as np

class Gradient:
    def __init__(self):
        self.change = 0

    def Evaluate(self, grad, learning_rate):
        return grad * learning_rate

class Momentum(Gradient):
    def __init__(self, velocity_rate = 0.9):
        self.velocity_rate = velocity_rate

        self.velocity = 0
        self.change = 0

    def Evaluate(self, grad, learning_rate):
        self.velocity = self.velocity_rate * self.velocity + learning_rate * grad
        return self.velocity

class Ada_Grad(Gradient):
    def __init__(self, adaptive_rate = 1, epsilon = 1e-8):
        self.adaptive_rate = adaptive_rate
        self.epsilon = epsilon

        self.ada_grad = 0
        self.change = 0

    def Evaluate(self, grad, learning_rate):
        self.ada_grad = self.adaptive_rate * self.ada_grad + grad ** 2
        learning_rate = learning_rate / np.sqrt(self.ada_grad + self.epsilon)
        return learning_rate * grad

class Momentum_Ada_Grad(Gradient):
    def __init__(self, velocity_rate = 0.9, adaptive_rate = 1, epsilon = 1e-8):
        self.velocity_rate = velocity_rate
        self.adaptive_rate = adaptive_rate
        self.epsilon = epsilon

        self.velocity = 0
        self.ada_grad = 0
        self.change = 0

    def Evaluate(self, grad, learning_rate):
        self.ada_grad = self.adaptive_rate * self.ada_grad + grad ** 2
        learning_rate = learning_rate / np.sqrt(self.ada_grad + self.epsilon)
        self.velocity = self.velocity_rate * self.velocity + learning_rate * grad
        return self.velocity

class RMS_Prop(Gradient):
    def __init__(self, adaptive_rate = 0.5, epsilon = 1e-8):
        self.adaptive_rate = adaptive_rate
        self.epsilon = epsilon

        self.grad = 0

        
        self.change = 0

    def Evaluate(self, grad, learning_rate):
        self.grad = self.adaptive_rate * self.grad + (1 - self.adaptive_rate) * grad ** 2
        learning_rate = learning_rate / np.sqrt(self.grad + self.epsilon)
        return learning_rate * grad

class Momentum_RMS_Prop(Gradient):
    def __init__(self, velocity_rate = 0.9, adaptive_rate = 0.5, epsilon = 1e-8):
        self.velocity_rate = velocity_rate
        self.adaptive_rate = adaptive_rate
        self.epsilon = epsilon

        self.velocity = 0
        self.grad = 0

        
        self.change = 0

    def Evaluate(self, grad, learning_rate):
        self.grad = self.adaptive_rate * self.grad + (1 - self.adaptive_rate) * grad ** 2
        learning_rate = learning_rate / np.sqrt(self.grad + self.epsilon)
        self.velocity = self.velocity_rate * self.velocity + learning_rate * grad
        return self.velocity

class Nesterov_Momentum(Gradient):
    def __init__(self, velocity_rate = 0.9):
        self.velocity_rate = velocity_rate
        self.velocity = 0

        
        self.change = 0

    def Evaluate(self, grad, learning_rate):
        out = -self.change
        self.change = self.velocity_rate * self.change + learning_rate * grad
        return out + self.change * 2


class Nesterov_RMS_Prop(Gradient):
    def __init__(self, velocity_rate = 0.9, adaptive_rate = 0.5, epsilon = 1e-8):
        self.velocity_rate = velocity_rate
        self.adaptive_rate = adaptive_rate
        self.epsilon = epsilon

        self.velocity = 0
        self.grad = 0
        
        self.change = 0

    def Evaluate(self, grad, learning_rate):
        out = -self.change

        self.grad = self.adaptive_rate * self.grad + (1 - self.adaptive_rate) * grad ** 2
        learning_rate = learning_rate / np.sqrt(self.grad + self.epsilon)

        self.change = self.velocity_rate * self.change + learning_rate * grad
        return out + self.change * 2

class Adam(Gradient):
    def __init__(self, velocity_rate = 0.9, adaptive_rate = 0.5, epsilon = 1e-8):
        self.velocity_rate = velocity_rate
        self.adaptive_rate = adaptive_rate
        self.epsilon = epsilon

        self.velocity = 0
        self.grad = 0

        self.i = 0

        self.change = 0

    def Evaluate(self, grad, learning_rate):
        self.i += 1

        self.grad = self.adaptive_rate * self.grad + (1 - self.adaptive_rate) * grad ** 2
        grad_hat = self.grad / (1 + self.adaptive_rate ** self.i)
        learning_rate = learning_rate / np.sqrt(grad_hat + self.epsilon)

        self.velocity = self.velocity_rate * self.velocity + (1 - self.velocity_rate) * grad
        velocity_hat = self.velocity / (1 + self.velocity_rate ** self.i)

        return learning_rate * velocity_hat


class Nesterov_Adam(Gradient):
    def __init__(self, velocity_rate = 0.9, adaptive_rate = 0.5, epsilon = 1e-8):
        self.velocity_rate = velocity_rate
        self.adaptive_rate = adaptive_rate
        self.epsilon = epsilon

        self.velocity = 0
        self.grad = 0
        self.out = 0

        self.i = 0

        self.change = 0

    def Evaluate(self, grad, learning_rate):
        self.i += 1

        out = -self.change

        self.grad = self.adaptive_rate * self.grad + (1 - self.adaptive_rate) * grad ** 2
        grad_hat = self.grad / (1 + self.adaptive_rate ** self.i)
        learning_rate = learning_rate / np.sqrt(grad_hat + self.epsilon)

        self.velocity = self.velocity_rate * self.velocity + (1 - self.velocity_rate) * grad
        velocity_hat = self.velocity / (1 + self.velocity_rate ** self.i)

        self.change = learning_rate * velocity_hat

        return out + self.change * 2


class Nesterov_Ada_Grad(Gradient):
    def __init__(self, adaptive_rate = 1, epsilon = 1e-8):
        self.adaptive_rate = adaptive_rate
        self.epsilon = epsilon

        self.ada_grad = 0

    def Evaluate(self, grad, learning_rate):
        out = -self.change

        self.ada_grad = self.adaptive_rate * self.ada_grad + grad ** 2
        learning_rate = learning_rate / np.sqrt(self.ada_grad + self.epsilon)

        self.change = self.velocity_rate * self.change + learning_rate * grad
        return out + self.change * 2

