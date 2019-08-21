"""
Slack Bot Commands Loader
"""
import os
import module_loader

module_loader.load(os.path.dirname(__file__), "ebr_trackerbot.command")
