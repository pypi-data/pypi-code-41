"""
pipdeps
"""
import argparse
import json
import distutils.version
import os
import pprint
import re
import subprocess
import sys
import urllib2
import tarfile
import tempfile
import zipfile
import wheel.metadata

import tabulate
import packaging.specifiers
import packaging.version

def arg_parse():
    """
    argument parser
    """
    parser = argparse.ArgumentParser(
        description="Pipdeps shows/upgrades outdated packages with respect to existing \
                     dependencies."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-l', '--list',
                       action='store_true',
                       help="show upgradeable packages and versions")
    group.add_argument('-u', '--upgrade',
                       action='store_true',
                       help="upgrade upgradeable packages")
    group.add_argument('-s', '--show',
                       nargs='+',
                       help="show detailed info about upgradeable packages")
    return parser.parse_args()

def get_pyver():
    """
    return running python version
    """
    return ".".join(map(str, sys.version_info[:3]))

def is_strict_version(version):
    """
    Return true if version is strict, otherwise return false
    """
    try:
        distutils.version.StrictVersion(version)
    except ValueError:
        return False
    return True

def version_conform_specifiers(version, specifiers):
    """
    check if version conforms specifiers
    """
    if not specifiers:
        return True
    elif version is None:
        return True
    else:
        ver = packaging.version.Version(version)
        spec = packaging.specifiers.SpecifierSet(",".join(specifiers))
        if spec.contains(ver):
            return True
    return False

def upgrade_package(package, versions):
    """
    pip install --upgrade "<package><versions>"
    """
    subprocess.check_call(
        ["pip", "install", "--upgrade", "%s==%s" % (package, "".join(versions))],
        stderr=subprocess.STDOUT
    )

def get_pip_list():
    """
    pip list
    """
    outdated_packages = subprocess.check_output(["pip", "list"])
    return [line.split()[0] for line in outdated_packages.strip().split("\n")[2:]]

def file_download(url):
    """
    Download file from url as temporary file
    It returns file object
    """
    tmp_file = tempfile.NamedTemporaryFile(delete=False)
    rfile = urllib2.urlopen(url)
    with tmp_file as output:
        output.write(rfile.read())
    return tmp_file

def get_jsonpipdeptree():
    """
    pipdeptree --json-tree
    """
    pipdeptree = subprocess.check_output(
        ["pipdeptree", "--json-tree"],
        stderr=subprocess.STDOUT
    )
    return json.loads(pipdeptree.strip())

def get_json(url):
    """
    Return url json
    """
    return json.load(urllib2.urlopen(urllib2.Request(url)))

def json_search(jsonpipdeptree, package, key):
    """
    find package dependencies in json tree
    """
    if isinstance(jsonpipdeptree, dict):
        keys = jsonpipdeptree.keys()
        if 'package_name' in keys and key in keys:
            if re.search(r'^%s$' % package, jsonpipdeptree['package_name'], re.IGNORECASE):
                yield jsonpipdeptree[key]
        for child_val in json_search(jsonpipdeptree['dependencies'], package, key):
            yield child_val
    elif isinstance(jsonpipdeptree, list):
        for item in jsonpipdeptree:
            for item_val in json_search(item, package, key):
                yield item_val

def get_highest_version(package, data):
    """
    Return upgradeable version if possible, otherwise return installed version
    """
    try:
        version = data[package]['upgradeable_version']
    except KeyError:
        version = data[package]['installed_version']
    return version

def find_available_vers(package_name, pyver):
    """
    Return descending list of available strict version
    """
    versions = []
    try:
        data = get_json("https://pypi.python.org/pypi/%s/json" % (package_name,))
    except urllib2.HTTPError, err:
        print "%s %s" % (err, err.url)
        raise urllib2.HTTPError(err.url, err.code, None, err.hdrs, err.fp)
    releases = data["releases"].keys()
    for release in releases:
        requires_python = []
        for item in data["releases"][release]:
            if item['requires_python'] is not None:
                requires_python.append(item['requires_python'])
        if is_strict_version(release) and version_conform_specifiers(pyver, requires_python):
            versions.append(release)
    return sorted(versions, key=distutils.version.StrictVersion, reverse=True)

def get_newer_vers(available_version, required_version, installed_version=None):
    """
    Return list of newer versions which conforms pipdeptree dependencies, otherwise return none.
    """
    if required_version is None:
        result = [aver for aver in list(available_version)]
        return sorted(result, key=distutils.version.StrictVersion, reverse=True)
    if [rver for rver in required_version if re.search(r'(^==.*|^\d.*)', rver) is not None]:
        return None
    result = []
    av_version = list(available_version)
    while True:
        try:
            version = av_version.pop(0)
        except IndexError:
            break
        aver = packaging.version.Version(version)
        rver = packaging.specifiers.SpecifierSet(",".join(required_version))
        if rver.contains(aver):
            if installed_version is not None:
                iver = packaging.version.Version(installed_version)
                if aver == iver:
                    break
                elif aver > iver:
                    result.append(version)
            else:
                result.append(version)
    if result:
        return sorted(result, key=distutils.version.StrictVersion, reverse=True)
    return None

def write_metadata(tmp_file):
    """
    Write package metadata
    """
    try:
        tar_file = tarfile.open(tmp_file.name, 'r')
        for member in tar_file.getmembers():
            if 'requires.txt' in member.name:
                with open('/tmp/requires.txt', 'w') as tmpf:
                    tmpf.write(tar_file.extractfile(member).read())
            if 'PKG-INFO' in member.name:
                with open('/tmp/PKG-INFO', 'w') as tmpf:
                    tmpf.write(tar_file.extractfile(member).read())
    except tarfile.ReadError:
        zip_file = zipfile.ZipFile(tmp_file.name, 'r')
        for member in zip_file.namelist():
            if 'requires.txt' in member:
                with open('/tmp/requires.txt', 'w') as tmpf:
                    tmpf.write(zip_file.read(member))
            if 'PKG-INFO' in member:
                with open('/tmp/PKG-INFO', 'w') as tmpf:
                    tmpf.write(zip_file.read(member))

def get_metadata(package, version):
    """
    Return package metadata
    """
    metadata = None
    for item in get_json("https://pypi.python.org/pypi/%s/%s/json" % (package, version,)) \
        ['releases'][version]:
        if item['packagetype'] == 'sdist':
            tmp_file = file_download(item['url'])
            write_metadata(tmp_file)
            if os.path.isfile('/tmp/requires.txt') and os.path.isfile('/tmp/PKG-INFO'):
                metadata = [
                    line.decode('utf-8') \
                    for line in wheel.metadata.pkginfo_to_metadata('/tmp', '/tmp/PKG-INFO') \
                    .as_string().splitlines()]
            try:
                os.unlink('/tmp/requires.txt')
            except OSError:
                pass
            try:
                os.unlink('/tmp/PKG-INFO')
            except OSError:
                pass
            os.unlink(tmp_file.name)
            if metadata:
                break
        elif item['packagetype'] == 'bdist_wheel':
            tmp_file = file_download(item['url'])
            zip_file = zipfile.ZipFile(tmp_file.name, 'r')
            for member in zip_file.namelist():
                if 'METADATA' in member:
                    metadata = [line.decode('utf-8') for line in zip_file.read(member).splitlines()]
            os.unlink(tmp_file.name)
            break
    return metadata

def parse_metadata(metadata, pyver):
    """
    Return dependencies parsed from metadata
    """
    for line in metadata:
        if 'Metadata-Version' in line.decode('utf-8'):
            metadata_version = line.replace('Metadata-Version:', '').strip()
            break
    if packaging.version.Version(metadata_version) >= packaging.version.Version('2.0'):
        out = []
        for dep in [
                line.replace('Requires-Dist:', '').strip() \
                for line in metadata if re.search(r'^Requires-Dist:', line)]:
            if ';' in dep:
                dep = dep.split(';')
                if 'python_version' in dep[1]:
                    if packaging.specifiers.SpecifierSet(
                            dep[1].replace('python_version', '').replace('"', '').strip()) \
                        .contains(packaging.version.Version(pyver)):
                        dep = dep[0]
                    else:
                        continue
                else:
                    continue
            dep = dep.split()
            try:
                pkg = re.search(r'(.*)(\[.*\])', dep[0]).group(1)
            except AttributeError:
                pkg = dep[0]
            try:
                pkg = re.search(r'(^[\w\.\-]*)(.*)', dep[0]).group(1)
                dep.append(re.search(r'(^[\w\.\-]*)(.*)', dep[0]).group(2))
            except AttributeError:
                pkg = dep[0]
            try:
                ver = dep[1].replace('(', '').replace(')', '').replace(';', '')
            except IndexError:
                ver = None
            out.append((pkg, ver))
    return out

def find_new_dependencies(package, version, package_list, pyver):
    """
    Return package dependencies parsed from pypi json
    """
    content = parse_metadata(get_metadata(package, version), pyver)
    for pkg, ver in content:
        try:
            if pkg in package_list:
                yield (pkg, ver)
            else:
                try:
                    for child in find_new_dependencies(
                            pkg,
                            get_newer_vers(find_available_vers(pkg, pyver), ver, None)[0],
                            package_list,
                            pyver
                        ):
                        yield child
                except TypeError:
                    pass
        except AttributeError:
            pass

def depless_vers(res):
    """
    If there is no dependencies or versionless dependencies, return the upgradeable version,
    otherwise return None
    """
    depless = []
    for ver, deps in res.iteritems():
        if not deps:
            depless.append(ver)
        else:
            if not [dep for dep in deps if dep[1] is not None]:
                depless.append(ver)
    if depless:
        depless = sorted(depless, key=distutils.version.StrictVersion, reverse=True)[0]
    else:
        depless = None
    return depless

def collect_packages(package_list, jsonpipdeptree, pyver=None):
    """
    Collect data about packages as dictionary
    """
    result = {}
    for package in package_list:
        installed_version = "".join(list(set(
            [_ for _ in json_search(jsonpipdeptree, package, 'installed_version')])))
        required_version = []
        for dep in list(set(
                [_ for _ in json_search(jsonpipdeptree, package, 'required_version')]
            )):
            if 'Any' not in dep:
                required_version.append(dep)
        try:
            available_version = find_available_vers(package, pyver)
        except urllib2.HTTPError:
            available_version = [installed_version]
        newer_version = get_newer_vers(available_version, required_version, installed_version)
        rev = {'installed_version': installed_version,
               'required_version': required_version,
               'available_version': available_version}
        if newer_version is not None:
            res = {}
            for version in newer_version:
                res[version] = [
                    _ for _ in find_new_dependencies(package, version, package_list, pyver)]
            rev['newer_version'] = res

            depless = depless_vers(res)
            if depless:
                rev['upgradeable_version'] = depless

        result[package] = rev
    return result

def check_deps(deps, packages_data):
    """
    Return true, if all package dependencies conforms
    """
    ndeps = []
    for item in deps:
        if item[1] is not None:
            ndeps.append(
                version_conform_specifiers(
                    get_highest_version(item[0], packages_data),
                    packages_data[item[0]]['required_version']+[item[1]]
                )
            )
    return all(ndeps)

def select_pkgs(packages_data, rkey):
    """
    Return data packages having requested key
    """
    result = {}
    for pkg, pkg_data in packages_data.iteritems():
        if rkey in pkg_data.keys():
            result[pkg] = pkg_data
    return result

def print_list(upgradeable_pkgs):
    """
    Provides list option
    """
    if upgradeable_pkgs:
        data = []
        for pkg, pkg_data in sorted(upgradeable_pkgs.iteritems(), key=lambda x: x[0].lower()):
            data.append([pkg, pkg_data['installed_version'], pkg_data['upgradeable_version']])
        print tabulate.tabulate(
            data,
            ['package', 'installed_version', 'upgradeable_version']
        )
        sys.exit(1)
    else:
        print "There is nothing to upgrade."
        sys.exit(0)

def main():
    """
    main function
    """
    os.environ["PYTHONWARNINGS"] = "ignore:DEPRECATION"
    arguments = arg_parse()
    pyver = get_pyver()
    pkglist = get_pip_list()
    jsonpipdeptree = get_jsonpipdeptree()
    packages_data = collect_packages(pkglist, jsonpipdeptree, pyver=pyver)
    for pkg, pkg_data in sorted(
            select_pkgs(packages_data, 'newer_version').iteritems(), key=lambda x: x[0].lower()
        ):
        pkg_keys = pkg_data.keys()
        if 'newer_version' in pkg_keys and 'upgradeable_version' not in pkg_keys:
            for ver, deps in sorted(
                    pkg_data['newer_version'].iteritems(),
                    key=lambda x: distutils.version.StrictVersion(x[0]),
                    reverse=True
                ):
                ndeps = check_deps(deps, packages_data)
                if ndeps:
                    packages_data[pkg]['upgradeable_version'] = ver
                    break
    upgradeable_pkgs = select_pkgs(packages_data, 'upgradeable_version')

    if arguments.list:
        print_list(upgradeable_pkgs)
    if arguments.show:
        for pkg in arguments.show:
            pprint.pprint({pkg: packages_data[pkg]})
        sys.exit(0)
    if arguments.upgrade:
        if 'pip' in upgradeable_pkgs.keys():
            upgrade_package('pip', upgradeable_pkgs['pip']['upgradeable_version'])
            del upgradeable_pkgs['pip']
        for pkg, pkg_data in sorted(upgradeable_pkgs.iteritems(), key=lambda x: x[0].lower()):
            upgrade_package(pkg, pkg_data['upgradeable_version'])
        print "Done."

if __name__ == "__main__":
    main()
