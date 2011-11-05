# -*- encoding: utf-8 -*-
from test import prepare_fakeparser_for_tests
prepare_fakeparser_for_tests()

from b3.fake import fakeConsole, joe, simon, superadmin, moderator
from poweradminbf3 import Poweradminbf3Plugin
from b3.config import XmlConfigParser


conf = XmlConfigParser()
conf.loadFromString("""
<configuration plugin="poweradminbf3">
  <settings name="commands">
    <set name="swap">40</set>
  </settings>
</configuration>
""")

p = Poweradminbf3Plugin(fakeConsole, conf)
p.onLoadConfig()
p.onStartup()

simon.connects("simon")
simon.teamId = 1
simon.squad = 7
joe.connects('Joe')
joe.teamId = 1
joe.squad = 7
moderator.connects('moderator')
moderator.teamId = 2
moderator.squad = 5
superadmin.connects('superadmin')
superadmin.teamId = 2
superadmin.squad = 6
print "Joe's group is " +  joe.maxGroup.name
print "Simon's group is " + simon.maxGroup.name
print "Moderator's group is " + moderator.maxGroup.name
print "superadmin's group is " +  superadmin.maxGroup.name



print "#"*80 ###################################### test !swap
superadmin.teamId = 2
superadmin.squad = 6
print "superadmin.teamId: %s, squad: %s" % (superadmin.teamId, superadmin.squad)
joe.teamId = 1
joe.squad = 7
print "joe.teamId: %s, squad: %s" % (joe.teamId, joe.squad)
superadmin.says('!swap joe')

simon.teamId = 1
simon.squad = 6
joe.teamId = 1
joe.squad = 6
superadmin.says("!swap joe simon")

joe.squad = 2
superadmin.says("!swap joe simon")

# test groups
p._adminPlugin._commands["swap"].level = 0,100
simon.says("!swap moderator")
moderator.says("!swap simon god")