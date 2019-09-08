class Algebra:
    def __init__(self, a,  b, operation):
        self.a = a
        self.b = b
        self.operaion = operation
    def operate():
        if self.operation ==  'add':
            return self.a + self.b
        if self.operation == 'subtract':
            return self.a - self.b
        if self.operation == 'multiply':
            return self.a * self.b
        if self.operation == 'division':
            if self.b == 0:
                return 'error'
            return self.a / self.b
        if self.operation == 'power':
            return self.a ** self.b