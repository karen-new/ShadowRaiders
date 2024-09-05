import random
import numpy as np
from shadowraiders.game.env import MyEnv

class PlayerRandom:
    def blackmist_random(self):
        """
        ブラックミスト：カードをランダムに選択します。

        Returns:
            str: ランダムに選ばれたブラックミストのカード ('W', 'B', 'D')。
        """
        card = ['W','B','D']
        action = random.choice(card)
        return action

    def city_hall_random(self):
        """
        シティーホール:アクションでランダムなプレイヤーを選び、そのプレイヤーに「heal」アクションを適用します。

        Returns:
            tuple: 選ばれたプレイヤーとアクションのペア (Playerオブジェクト, "heal")。
        """        
        p = random.choice(MyEnv.players)
        while p.death:
            p = random.choice(MyEnv.players)
        return p,"heal"  
    
    def reveal_recover_random(self):
        """
        正体を公開したら回復できるカード:HP回復を選択するかどうかを評価し、選択の結果をTrueまたはFalseでランダムに返します。

        Returns:
            bool: 耐久力回復する場合はTrue、しない場合はFalse。
        """

        choice = [True, False]
        return random.choice(choice)
    
    def first_aid_random(self):
        """
        応急手当：使用するターゲットをランダムに選択します。
        
        Returns:
            Player: ターゲットプレイヤー
        """
        return random.choice(MyEnv.players)
    
    def select_recovery_target_random(self):
        """
        回復を行うターゲットをランダムで選択します。

        Returns:
            Player: ターゲットプレイヤー
        """
        return  self.select_random_player()
    
    def select_attack_target_random(self):
        """
        ダメージを与えるカード：使用するターゲットをランダムに選択します。

        Returns:
            Player: ターゲットプレイヤー。
        """
        p = random.choice(MyEnv.players)
        while p is self or p.death:
            p = random.choice(MyEnv.players)
        return p