from swimlane_platform.lib.debug_decorators import info_function_start_finish
from swimlane_platform.shared_steps import enable_turbine
from swimlane_platform.upgrade_steps.upgrade_step import UpgradeStep
import semver


class UpgradeFrom910To1000(UpgradeStep):
    FROM = semver.parse_version_info('9.1.0')  # type: semver.VersionInfo
    TO = semver.parse_version_info('10.0.0')  # type: semver.VersionInfo

    @info_function_start_finish('Upgrade From 9.1.0 To 10.0.0.')
    def process(self):
        # type: () -> None
        enable_turbine.run(self.config)
