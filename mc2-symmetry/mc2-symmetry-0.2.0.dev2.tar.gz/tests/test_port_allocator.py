import time
import unittest
from typing import List

from symmetry.api import ServiceMetadataRepository, ServiceDescription
from symmetry.nrg import LeasingPortAllocator


# noinspection PyAbstractClass
class MockMetadataRepository(ServiceMetadataRepository):

    def __init__(self) -> None:
        super().__init__()
        self.used_ports = set()

    def get_services(self) -> List[ServiceDescription]:
        result = list()

        for port in self.used_ports:
            service_id = ('service-%d' % port)
            result.append(ServiceDescription(service_id, service_id, None, None, symmetry_port=port))
        return result


class LeasingPortAllocatorTest(unittest.TestCase):

    def setUp(self) -> None:
        self.repo = MockMetadataRepository()

    def test_allocate_port_behaves_correctly(self):
        allocator = LeasingPortAllocator(self.repo)
        allocator.port_range = range(1, 3)

        self.repo.used_ports.add(1)

        p = allocator.allocate_port()
        self.assertEqual(2, p)

    def test_leases_work(self):
        allocator = LeasingPortAllocator(self.repo)
        allocator.port_range = range(1, 3)

        p = allocator.allocate_port()

        if p == 1:
            n = 2
        else:
            n = 1

        p = allocator.allocate_port()
        self.assertEqual(n, p)

        try:
            allocator.allocate_port()
            self.fail('Should not be able to allocate another port')
        except:
            pass

    def test_leases_expires_works(self):
        allocator = LeasingPortAllocator(self.repo)
        allocator.port_range = range(1, 3)
        allocator.timeout = 0.25

        allocator.allocate_port()
        time.sleep(0.5)
        allocator.allocate_port()
        allocator.allocate_port()  # would throw an exception if the lease for the first hasn't expired


if __name__ == '__main__':
    unittest.main()
