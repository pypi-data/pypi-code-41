import qcodes.utils.installation_info as ii
import qcodes as qc


# The get_* functions from installation_info are hard to meaningfully test,
# but we can at least test that they execute without errors


def test_get_qcodes_version():
    assert ii.get_qcodes_version() == qc.version.__version__


def test_get_qcodes_requirements():
    reqs = ii.get_qcodes_requirements()

    assert isinstance(reqs, list)
    assert len(reqs) > 0


def test_get_qcodes_requirements_versions():
    req_vs = ii.get_qcodes_requirements_versions()

    assert isinstance(req_vs, dict)
    assert len(req_vs) > 0


def test_is_qcodes_installed_editably():
    answer = ii.is_qcodes_installed_editably()

    assert isinstance(answer, bool)
