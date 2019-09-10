import torch
import copy

from JT.Utils import RecGetattr, RecSetattr

def Breed(parent_1, parent_2, p_1, p_mutate):
    """
    Breeds two tensors.

    Elements are randomly selected from each parent tensor to be passed on to the child tensor.

    Some of the elements are set to zero to "mutate" the child a bit.

    Note: Tensors must be the same shape.

    :param parent_1: The first parent tensor.
    :param parent_2: The second parent tensor.
    :param p_1: Proportion of the child that should come from the first parent.
    :param p_mutate: Proportion of the child to be set to zero (mutated).
    :return: The child tensor.
    """
    rng = torch.rand(parent_1.shape).cuda()
    bool_1 = rng < p_1
    bool_2 = rng > (p_1 + p_mutate)
    return parent_1 * bool_1.double().cuda() + parent_2 * bool_2.double().cuda()


def ModelBreed(model_1, model_2, mutation_rate):
    """
    Breeds two models.
    The models must have been built using the torch.nn.Module framework.

    Each parameter in the models are bred together using Breed().

    The influence of each parent is derived from fitness and performance attributes in the models.

    Note: The models need to be exactly the same type.

    :param model_1: The first parent model.
    :param model_2: The second parent model.
    :param mutation_rate: The mutation rate.
    :return: The child model.
    """
    model_child = copy.copy(model_1)
    p_0 = (1 - model_1.performance - model_2.performance) * mutation_rate
    p_male = model_1.fitness / (model_1.fitness + model_2.fitness) * (1 - p_0)
    for name, param in model_child.named_parameters():
        child = torch.nn.Parameter(Breed(RecGetattr(model_1, name), RecGetattr(model_2, name), p_male, p_0))
        RecSetattr(model_child, name, child)
    return model_child