import os

from assertpy import assert_that

from netboot_config import Config


class TestConfig(object):

    def setup_method(self):
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, 'netboot-config.yml')
        self.uut = Config(filename)

    def test_netboot_ip(self):
        assert_that(self.uut.netboot_ip).is_equal_to("10.0.10.5")

    def test_hosts_names(self):
        hosts = self.uut.hosts
        assert_that([host.host_name for host in hosts]).contains("abc1110", "abc1111", "abc1120")

    def test_hosts_image_types(self):
        hosts = self.uut.hosts
        assert_that([host.image_type for host in hosts]).contains("type1", "type1", "type2")

    def test_hosts_image_config(self):
        hosts = self.uut.hosts
        assert_that([host.config for host in hosts]).contains((), (), (('src', 'tgt'),))

    def test_static_hosts_names(self):
        hosts = self.uut.static_hosts
        assert_that([host.host_name for host in hosts]).contains("abc1005", "abc1020", "abc1021", "abc1030", "abc1040")

    def test_static_hosts_image_types(self):
        hosts = self.uut.static_hosts
        assert_that([host.image_type for host in hosts]).contains(None, None, None, None, None)

    def test_static_hosts_image_aliases(self):
        hosts = self.uut.static_hosts
        assert_that([host.aliases for host in hosts]).contains((), (), (), ('foo',), ('bar', 'baz'))

    def test_all_hosts(self):
        assert_that(len(self.uut.all_hosts)).is_equal_to(8)

    def test_get_undefined_host_in_static_network(self):
        host = self.uut.get_host('10.0.10.99')
        assert_that(host.host_name).is_equal_to("abc1099")
        assert_that(host.aliases).is_empty()

    def test_get_defined_host_in_static_network(self):
        host = self.uut.get_host('10.0.10.30')
        assert_that(host.host_name).is_equal_to("abc1030")
        assert_that(host.aliases).contains("foo")

    def test_get_undefined_host_in_dynamic_network(self):
        host = self.uut.get_host('10.0.11.99')
        assert_that(host.host_name).is_equal_to("abc1199")
        assert_that(host.image_type).is_none()

    def test_get_defined_host_in_dynamic_network(self):
        host = self.uut.get_host('10.0.11.10')
        assert_that(host.host_name).is_equal_to("abc1110")
        assert_that(host.image_type).is_equal_to("type1")

    def test_host_outside_networks(self):
        host = self.uut.get_host('10.0.12.99')
        assert_that(host).is_none()

    def test_aliases(self):
        aliases = self.uut.aliases
        assert_that(aliases).contains(('foo', 'abc1030'), ('bar', 'abc1040'), ('baz', 'abc1040'))

    def test_render_hosts(self):
        result = self.uut.render_hosts()

        hosts = {}
        for line in result.split("\n"):
            parts = line.split("\t")
            if len(parts) == 2:
                hosts[parts[0]] = parts[1].split(" ")

        assert_that(hosts).contains_entry(
            {'127.0.0.1': ['localhost']},
            {'::1': ['localhost', 'ip6-localhost', 'ip6-loopback']},
            {'fe00::0': ['ip6-localnet']},
            {'ff00::0': ['ip6-mcastprefix']},
            {'ff02::1': ['ip6-allnodes']},
            {'ff02::2': ['ip6-allrouters']},
            {'ff02::3': ['ip6-allhosts']},

            {'10.0.11.10': ['abc1110']},
            {'10.0.11.11': ['abc1111']},
            {'10.0.11.20': ['abc1120']},
            {'10.0.10.5': ['abc1005', 'netboot']},
            {'10.0.10.20': ['abc1020']},
            {'10.0.10.21': ['abc1021']},
            {'10.0.10.30': ['abc1030', 'foo']},
            {'10.0.10.40': ['abc1040', 'bar', 'baz']})

    def test_find_alias_by_name(self):
        result = self.uut.alias('foo')

        assert_that(result.host_name).is_equal_to("abc1030")

    def test_find_alias_by_name_no_result(self):
        result = self.uut.alias('qux')

        assert_that(result).is_none()
