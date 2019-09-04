
class TestClass:
    '''
        Responsible for storing the projects test methods.
    '''
    def __init__(self, test_methods):
        method_id = test_methods[0].id()
        test_class_id_terms = method_id.split('.')[:-1]
        self.id = '.'.join(test_class_id_terms)
        self.method_names = [method.id().split('.')[-1] for method in test_methods]
        self.methods = test_methods

    def serialize(self):
        return {
            'id': self.id, 
            'method_names': self.method_names,
            'method_ids': [method.id() for method in self.methods],
            'type': 'TestClass'
        }
