# This file is generated automatically by scripts
from __future__ import absolute_import, division, print_function
import kimpy

attributes = [
  kimpy.collection_item_type.modelDriver,
  kimpy.collection_item_type.portableModel,
  kimpy.collection_item_type.simulatorModel,
]


str_names = [
  "modelDriver",
  "portableModel",
  "simulatorModel",
]


def test_main():

    N = kimpy.collection_item_type.get_number_of_collection_item_types()
    assert N == 3

    all_instances = []
    for i in range(N):
        inst,error = kimpy.collection_item_type.get_collection_item_type(i)
        all_instances.append(inst)

        assert error == False
        assert inst == attributes[i]
        assert str(inst) == str_names[i]

    # test operator overloading
    for i in range(N):
        assert all_instances[i] == all_instances[i]
        for j in range(i+1, N):
            assert all_instances[i] != all_instances[j]

    # test known
    for inst in all_instances:
        assert inst.known() == True

    # test out of bound
    inst,error = kimpy.collection_item_type.get_collection_item_type(N)
    assert error == True


if __name__ == '__main__':
  test_main()
