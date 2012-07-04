# -*- encoding: utf-8 -*-
import logging
from mock import Mock, call
from tests import Mockito

from poweradminbf3 import Poweradminbf3Plugin, __file__ as poweradminbf3_file
from b3.config import XmlConfigParser

from tests import Bf3TestCase

class Test_events(Bf3TestCase):

    def setUp(self):
        Bf3TestCase.setUp(self)
        self.conf = XmlConfigParser()
        self.p = Poweradminbf3Plugin(self.console, self.conf)
        logger = logging.getLogger('output')
        logger.setLevel(logging.INFO)
        self.scrambleTeams_mock = self.p._scrambler.scrambleTeams = Mock(name="scrambleTeams", wraps=self.p._scrambler.scrambleTeams)
        self.scrambleTeams_mock.reset_mock()

    ###############################################################
    # utilities
    ###############################################################

    def _assert_scrambleTeams_has_calls_on_level_started(self, scramble_mode, gamemode_blacklist, next_gamemode, next_round_number, expected_calls):
        # Given
        self.conf.loadFromString("""<configuration plugin="poweradminbf3">
                <settings name="scrambler">
                    <set name="mode">%s</set>
                    <set name="strategy">random</set>
                    <set name="gamemodes_blacklist">%s</set>
                </settings>
            </configuration>""" % (scramble_mode, '|'.join(gamemode_blacklist)))
        self.p.onLoadConfig()
        self.p.onStartup()
        self.console.getClient = Mockito(wraps=self.console.getClient)

        # Make sure context is
        self.assertEqual(gamemode_blacklist, self.p._autoscramble_gamemode_blacklist)
        if scramble_mode == 'round':
            self.assertTrue(self.p._autoscramble_rounds)
            self.assertFalse(self.p._autoscramble_maps)
        elif scramble_mode == 'map':
            self.assertFalse(self.p._autoscramble_rounds)
            self.assertTrue(self.p._autoscramble_maps)
        elif scramble_mode == 'off':
            self.assertFalse(self.p._autoscramble_rounds)
            self.assertFalse(self.p._autoscramble_maps)
        else:
            self.fail("unsupported scramble mode : " + scramble_mode)

        # When
        self.joe.connects('joe')
        self.console.write.expect(('serverInfo',)).thenReturn([ 'i3D.net - BigBrotherBot #3 (DE)', '1', '16',
                                                                next_gamemode, 'MP_007', str(next_round_number), '2', '4', '0', '0', '0', '0', '50', '', 'false', 'true',
                                                                'false', '790596', '1484', '', '', '', 'EU', 'AMS', 'DE', 'false'])
        self.console.routeFrostbitePacket(['server.onLevelLoaded', 'MP_007', next_gamemode, str(next_round_number), '2'])
        self.console.getClient.expect('joe').thenReturn(self.joe)
        self.console.routeFrostbitePacket(['player.onSpawn', 'joe', '1'])

        # Then
        self.scrambleTeams_mock.assert_has_calls(expected_calls)


    def assert_scrambleTeams_has_calls_on_round_change(self, scramble_mode, gamemode_blacklist, next_gamemode, expected_calls):
        self._assert_scrambleTeams_has_calls_on_level_started(scramble_mode=scramble_mode,
            gamemode_blacklist=gamemode_blacklist, next_gamemode=next_gamemode, next_round_number=1,
            expected_calls=expected_calls)

    def assert_scrambleTeams_has_calls_on_map_change(self, scramble_mode, gamemode_blacklist, next_gamemode, expected_calls):
        self._assert_scrambleTeams_has_calls_on_level_started(scramble_mode=scramble_mode,
            gamemode_blacklist=gamemode_blacklist, next_gamemode=next_gamemode, next_round_number=0,
            expected_calls=expected_calls)

    ###############################################################
    # Actual tests
    ###############################################################

    def test_auto_scramble_ignore_blacklisted_gamemodes_on_round_change(self):
        self.assert_scrambleTeams_has_calls_on_round_change(
            scramble_mode='round',
            gamemode_blacklist=['SquadDeathMatch0'],
            next_gamemode='SquadDeathMatch0',
            expected_calls=[])

    def test_auto_scramble_on_round_change(self):
        self.assert_scrambleTeams_has_calls_on_round_change(
            scramble_mode='round',
            gamemode_blacklist=['SquadDeathMatch0'],
            next_gamemode='Rush0',
            expected_calls=[call()])
        self.assert_scrambleTeams_has_calls_on_round_change(
            scramble_mode='off',
            gamemode_blacklist=['SquadDeathMatch0'],
            next_gamemode='Rush0',
            expected_calls=[])

    def test_auto_scramble_ignore_blacklisted_gamemodes_on_map_change(self):
        self.assert_scrambleTeams_has_calls_on_map_change(
            scramble_mode='map',
            gamemode_blacklist=['SquadDeathMatch0', 'Conquest0'],
            next_gamemode='SquadDeathMatch0',
            expected_calls=[])

    def test_auto_scramble_on_map_change(self):
        self.assert_scrambleTeams_has_calls_on_map_change(
            scramble_mode='map',
            gamemode_blacklist=['SquadDeathMatch0'],
            next_gamemode='Rush0',
            expected_calls=[call()])
        self.assert_scrambleTeams_has_calls_on_map_change(
            scramble_mode='off',
            gamemode_blacklist=['SquadDeathMatch0'],
            next_gamemode='Rush0',
            expected_calls=[])
