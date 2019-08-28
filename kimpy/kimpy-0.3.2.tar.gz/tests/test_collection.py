# This file is generated automatically by scripts
from __future__ import absolute_import, division, print_function
import kimpy

attributes = [
  kimpy.collection.system,
  kimpy.collection.user,
  kimpy.collection.environmentVariable,
  kimpy.collection.currentWorkingDirectory,
]


str_names = [
  "system",
  "user",
  "environmentVariable",
  "currentWorkingDirectory",
]


def test_main():

    N = kimpy.collection.get_number_of_collections()
    assert N == 4

    all_instances = []
    for i in range(N):
        inst,error = kimpy.collection.get_collection(i)
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
    inst,error = kimpy.collection.get_collection(N)
    assert error == True


if __name__ == '__main__':
  test_main()
