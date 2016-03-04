#! /usr/bin/env python
import sys
import os

os_cmd = sys.argv[0]

root = os.path.join(os.path.dirname(__file__), '../..')
sys.path.insert(0, root)

from playtag.svf import runsvf
from playtag.lib.userconfig import UserConfig
from playtag.jtag.discover import Chain


config = UserConfig()
config.readargs(parseargs=True)


class SvfDefaults(object):
    SVF = None

config.add_defaults(SvfDefaults)

if not config.SVF:
    print 'Expected SVF=<fname>'

cablemodule = config.getcable()

driver = cablemodule.Jtagger(config)

runsvf(config.SVF,driver)
