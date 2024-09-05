import unittest
import random
import gym
import numpy as np
from unittest.mock import patch
from shadowraiders.game.env import MyEnv

class TestMyEnv(unittest.TestCase):

    def setUp(self):
        """ テスト用の環境をセットアップ """
        self.env = MyEnv(verbose=False)

    def test_reset(self):
        """ゲームのリセットが正しく行われるか"""
        self.env.reset()
        for player in self.env.players:
            self.assertIsNotNone(player.character)

    def test_deck_initialization(self):
        """デッキが正しく初期化されるか"""
        expected_white_cards = 16
        expected_black_cards = 13
        expected_detective_cards = 16
        self.env.reset()
        self.assertEqual(len(self.env.white_deck), expected_white_cards)
        self.assertEqual(len(self.env.black_deck), expected_black_cards)
        self.assertEqual(len(self.env.detective_deck), expected_detective_cards)

    def test_damage_death(self):
        """プレイヤーのダメージと死亡判定をテスト"""
        self.env.reset()
        player = self.env.players[0]
        player.character[2] = 1
        player.damage = 1
        self.env.check_death(player)
        self.assertTrue(player.death)

    def test_randomness(self):
        """ランダム性がゲームに適切に反映されるか"""
        results = []
        for _ in range(100):
            self.env.reset()
            results.append(self.env.players[0].character[0])
        self.assertGreater(len(set(results)), 1)

    def test_invalid_action(self):
        """無効なアクションが適切に処理されるか"""
        self.env.reset()
        action = {'player': 0, 'target': -1, 'action_type': 'attack'}
        with self.assertRaises(ValueError):
            self.env.step(action)

if __name__ == '__main__':
    unittest.main()
