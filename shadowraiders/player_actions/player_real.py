import random
import numpy as np

#Playerの情報を保持し、Playerの選択を行うクラス
class PlayerReal:  
    def __init__(self, character, verbose=False, player_number=5):
        self.verbose = verbose
        self.player_number = player_number
        self.character = character
        self.area = 0
        self.equipment = {}
        self.damage = 0
        self.death = False
        self.detective = [{"C","S","R"} for _ in range(player_number)]
        # 市民プレイヤは1人のみのため、他プレイヤの推定陣営はシャドウかレイダーのみ
        if self.character[1] == "C":
            self.detective = [{"S", "R"} for _ in range(player_number)]
        self.attack_damage = 1 # 攻撃時のダメージ量(通常1に固定)(装備カード所持時増加)
        self.guardian_angel = False
        self.seal_of_wisdom = False
        self.excalibur = False
    

    def _enemy_friend(self, players):
        """
        プレイヤの敵と味方を見つけます。
        敵は自分の陣営と異なり、生存しているプレイヤです。
        味方は自分の陣営と同じで生存しているプレイヤです。
        ただし、市民の可能性があるなど、確定していない場合はリストに含めません。

        Returns:
            (list, list): 敵プレイヤのリストと味方プレイヤのリストを返します。
        """
        enemies=[]
        friends=[]
        for i in range(self.player_number):
            if len(self.detective[i]) == 1:
                detective = next(iter(self.detective[i])) # player iの推定結果
                if detective != self.character[1] and not players[i].death:
                    enemies.append(players[i])
                    if self.verbose:
                        print("enemies : player", i+1)
                elif detective == self.character[1] and not players[i].death:
                    friends.append(players[i])
                    if self.verbose:
                        print("friends : player", i+1)
        random.shuffle(enemies)
        random.shuffle(friends)
        return enemies,friends
    

    def _detective_enemy_friend(self, estimated_camp, players):
        """
        プレイヤの行動から敵と味方を推定し、それぞれの陣営に応じてプレイヤをリストに格納します。

        Args:
            estimated_camp (list): プレイヤの推定を表すリスト。学習結果をもとに与えられます。

        Returns:
            (list, list): 推定された敵プレイヤのリストと味方プレイヤのリストを返します。
                            それぞれより敵らしい、味方らしい順に返されます。
        """
        enemy_dict = {}
        friend_dict = {}
        j = 1
        #print(estimated_camp)
        
        for i in range(0, len(estimated_camp), 3):
            if estimated_camp[i] > estimated_camp[i+1]:
                friend_dict[j] = estimated_camp[i]
            else:
                enemy_dict[j] = estimated_camp[i+1]
            j += 1
            
        # enemyとfriendのディクショナリを項目の大きい順にソートし、キーを取り出した配列を得る
        enemy_keys = sorted(enemy_dict, key=enemy_dict.get, reverse=True)
        friend_keys = sorted(friend_dict, key=friend_dict.get, reverse=True)

        enemies = [players[key] for key in enemy_keys if not players[key].death]
        friends = [players[key] for key in friend_keys if not players[key].death]

        return enemies,friends
    
    
    def _citizen_enemy_friend(self, players):
        """
        市民の場合の攻撃すべき敵と回復すべき味方を見つけます。
        アリスの場合、敵は先に脱落しそうな陣営のプレイヤ、味方は脱落しなさそうな陣営のプレイヤです。
        ダニエルの場合、味方は先に脱落しそうな陣営のプレイヤ、敵は脱落しなさそうな陣営のプレイヤです。

        Returns:
            (list, list): 敵プレイヤのリストと味方プレイヤのリストを返します。
        """
        shadows = []
        raiders = []
        high_damage_camp = []
        low_damage_camp = []
        for i in range(self.player_number):
            if len(self.detective[i]) == 1:
                detective = next(iter(self.detective[i]))
                if detective == 'R':
                    raiders.append(players[i])
                else:
                    shadows.append(players[i])

        # 同じ数の陣営の推定ができている場合は、各陣営プレイヤのダメージを足して、多い方を敵とする
        if len(raiders) == len(shadows):
            raiders_alive_players = [player for player in raiders if not player.death]
            shadows_alive_players = [player for player in shadows if not player.death]
            # もし陣営のプレイヤが2人も絞れていた場合、片方が脱落していればその陣営のプレイヤを返す
            if len(raiders_alive_players) == 1 and len(shadows_alive_players) != 1:
                return raiders_alive_players,shadows_alive_players
            elif len(shadows_alive_players) == 1 and len(raiders_alive_players) != 1:
                return shadows_alive_players,raiders_alive_players
            else:
                raiders_damage = sum(player.damage for player in raiders)
                shadows_damage = sum(player.damage for player in shadows)
                if raiders_damage > shadows_damage:
                    high_damage_camp = raiders
                    low_damage_camp = shadows
                else:
                    high_damage_camp = shadows
                    low_damage_camp = raiders
        # 推定ができている陣営の数が異なる場合は、プレイヤの中でダメージが一番大きいプレイヤのいる陣営を敵とする
        else:
            # 脱落しているプレイヤがいる場合、その陣営を敵とする
            if len(raiders) == 2:
                raiders_death_players = [player for player in raiders if player.death]
                shadows_death_players = [player for player in shadows if player.death]
                if raiders_death_players:
                    high_damage_camp = raiders
                    low_damage_camp = shadows
                elif shadows_death_players:
                    high_damage_camp = shadows
                    low_damage_camp = raiders
                    
            max_damage_player = max(shadows+raiders, key=lambda x: x.damage)
            if max_damage_player in raiders:
                high_damage_camp = raiders
                low_damage_camp = shadows
            else:
                high_damage_camp = shadows
                low_damage_camp = raiders

        # 脱落しているプレイヤを除外
        high_damage_camp = [player for player in high_damage_camp if not player.death]
        low_damage_camp = [player for player in low_damage_camp if not player.death]

        # ダメージ順に並び替え
        high_damage_camp = sorted(high_damage_camp, key=lambda x: x.damage, reverse=True)
        low_damage_camp = sorted(low_damage_camp, key=lambda x: x.damage, reverse=False)

        if self.character[0] == 'Alice':
            return high_damage_camp,low_damage_camp
        elif self.character[0] == 'Daniel':
            return low_damage_camp,high_damage_camp
        else:
            print('---error---')
            print("character:", self.character[0])
            return high_damage_camp,low_damage_camp

    
    def _return_enemy_friend_list(self, estimated_camp, players):
        """
        学習対象の場合とそうでない場合、市民の場合のそれぞれの敵味方のリストを返します。

        Args:
            estimated_camp (list): プレイヤの推定を表すリスト。学習結果をもとに与えられます。
                                    学習対象のとき以外はNoneとなります。

        Returns:
            (list, list): 推定された敵プレイヤのリストと味方プレイヤのリストを返します。
        """
        
        if estimated_camp:
            enemies, friends = self._detective_enemy_friend(estimated_camp, players)

        elif self.character[1] == 'C':
            enemies, friends = self._citizen_enemy_friend(players)
        
        else:
            enemies, friends = self._enemy_friend(players)
        return enemies, friends

    
    def _select_random_player(self, players):
        select_player = [p for p in players if p != self and not p.death]

        if select_player:
            return random.choice(select_player)
        else:
            print("!!! 自分以外のプレイヤが全員死んでいます !!!")

    
    def _select_validate_random(self, friends, players):
        """
        プレイヤの選択条件に従ってランダムにプレイヤを選択します。
        ここでは、自分以外の死んでもいないプレイヤという条件のもと、friendに入っていないプレイヤを優先して返します。

        Args:
            friends (list): 味方プレイヤのリスト。

        Returns:
            Player: 選択されたプレイヤ。
        """
        # 条件を満たすpを格納するリスト
        valid_candidates = []
        # 条件を満たすプレイヤを valid_candidates リストに追加
        for p in players:
            if (p is not self) and (p not in friends) and not p.death:
                valid_candidates.append(p)

        # 条件を満たすプレイヤがいた場合valid_candidatesからランダムに1つを選択
        if valid_candidates:
            return random.choice(valid_candidates)
        
        # 条件を満たすプレイヤがいない場合、自分以外の死んでいないプレイヤを選択
        else:
            # この場合friendの条件がおかしい可能性があるため、警告文を出力
            if self.verbose:
                print("!!! friendがおかしい可能性があります !!!")
            return self._select_random_player(players)

    def _select_attack_validate_random(self, friends, players):
        """
        プレイヤの選択条件に従ってランダムにプレイヤを選択します。
        ここでは、自分以外の死んでもいないプレイヤという条件のもと、friendに入っていないプレイヤを優先して返します。

        Args:
            friends (list): 味方プレイヤのリスト。

        Returns:
            Player: 選択されたプレイヤ。
        """
        # 条件を満たすpを格納するリスト
        valid_candidates = []

        # 条件を満たすプレイヤを valid_candidates リストに追加
        for p in players:
            if (p is not self) and (p not in friends) and self.is_value_attack(self, p) and not p.death:
                valid_candidates.append(p)

        # 条件を満たすプレイヤがいた場合valid_candidatesからランダムに1つを選択
        if valid_candidates:
            return random.choice(valid_candidates)
        
        # 条件を満たすプレイヤがいない場合、自分以外の死んでいないプレイヤを選択
        else:
            return None
            # この場合friendの条件がおかしい可能性があるため、警告文を出力
            if self.verbose:
                print("!!! friendがおかしい可能性があります !!!")
            return self._select_random_player(players)
    
    def blackmist_choice(self):
        """
        ブラックミスト：カードを選択します。役職と情報の収集状況に応じて選択肢を調整します。
        情報が少なければ推理カード、多ければレイダーなら白、シャドウなら黒のカードを引きやすくしています。

        Returns:
            str: 選ばれたブラックミストのカード ('W', 'B', 'D')。
        """        
        card = ['B','W','D']
        
        # 役職が1回でも絞れているプレイヤの数をカウント
        k = sum(1 for i in range(self.player_number) if len(self.detective[i]) != 3)
        
        # 全く絞れていない場合は確定で推理カード
        if k == 0:
            chosen_card = 'D'

        # プレイヤ人数の半分未満しか役職が判明していない場合は推理カードを選択する確率を高めとする
        if self.character[1] == 'S':
            if k < self.player_number/2:
                chosen_card = random.choices(card, weights = [1,0,9])[0]
            else:
                chosen_card = random.choices(card, weights = [6,4,0])[0]
        elif self.character[1] == 'R':
            if k < self.player_number/2:
                chosen_card = random.choices(card, weights = [0,1,9])[0]
            else:
                chosen_card = random.choices(card, weights = [4,6,0])[0]
        elif self.character[1] == 'C':
            if k < self.player_number/2:
                chosen_card = random.choices(card, weights = [0.5,0.5,9])[0]
            else:
                chosen_card = random.choices(card, weights = [5,5,0])[0]
        else:
            print('---error---')
            print("character:", self.character[1])
            chosen_card = 'D'  # エラー時はデフォルトで'D'カードを選択
            
        return chosen_card

    
    def city_hall_choice(self, estimated_camp, players):       
        """
        シティーホール：敵への攻撃または味方への回復を行います。推定に応じて選択肢を調整します。

        Args:
            estimated_camp (list): プレイヤの推定を表すリスト。学習結果をもとに与えられます。
                                    学習対象のとき以外はNoneとなります。

        Returns:
            tuple: 選ばれたプレイヤとアクションのペア (Playerオブジェクト, アクション)。
        """
        # 敵と味方を判定
        enemies, friends = self._return_enemy_friend_list(estimated_camp, players)
        
        if self.character[0] == 'Alice':
            # 自分の回復を優先
            if self.damage != 0:
                return self, "heal"
            # 敵（残りHPの少ない陣営）がいる場合、攻撃を選択
            elif enemies:
                return enemies[0], "attack"
            # 味方（残りHPの多い陣営）がいる場合、回復を選択
            elif friends:
                return friends[0], "heal"
            else:
                # 上記の条件に該当しない場合、自分、味方、死んでいるプレイヤ以外からランダムに選択して攻撃
                p = self._select_validate_random(friends, players)
                return p,"attack"
            
        if self.character[0] == 'Daniel':
            # あと残り２ダメージで死ぬ場合は自分を攻撃
            if self.character[2] - self.damage <= 2:
                return self, "attack"
            
            # 他プレイヤが死なないようにするため、friend(残りHPの少ない陣営)の回復を優先
            if friends:
                return friends[0], "heal"
            elif enemies:
                return enemies[0], "attack"
            # 自傷は目的が分かりやすすぎるので避ける
            else:
                return self, "attack"


        # 自身の残りHPが半分未満の場合、自己治癒を選択
        if self.damage > self.character[2] / 2:
            return self,"heal"
            
        # 敵がいる場合、攻撃を選択
        if enemies:
            for enemy in enemies:
                if "幸運のブローチ" not in enemy.equipment:
                    return enemy, "attack"
        # 味方がいてかつダメージがプレイヤ自身以上のプレイヤがいる場合、治癒を選択
        elif friends:
            for friend in friends:
                if friend.damage >= self.damage:
                    return friend, "heal"
        
        # 自身にダメージがある場合、自己治癒を選択
        if self.damage > 0:
            return self,"heal"
        
        # 上記の条件に該当しない場合、自分、味方、死んでいるプレイヤ以外からランダムに選択して攻撃
        p = self._select_validate_random(friends, players)
        return p,"attack"
    
            
    def reveal_recover_choice(self):
        """
        正体を公開したら回復できるカード:HP回復を選択するかどうかを評価し、選択の結果をTrueまたはFalseで返します。

        Returns:
            bool: 耐久力回復を選択する場合はTrue、しない場合はFalse。
        """
        #ダメージが半分以上のとき回復を選択
        if self.damage > self.character[2] / 2:
            return True
        else:
            return False    


    def first_aid_choice(self, estimated_camp, players):
        """
        応急手当：使用するターゲットを選択します。

        Args:
            estimated_camp (list): プレイヤの推定を表すリスト。学習結果をもとに与えられます。

        Returns:
            Player: ターゲットプレイヤ。
        """
        # 自分のダメージが7を超えていたら自分の回復として使う
        # ただしダニエルの場合は自分の回復を選ばない
        if self.character[0] != 'Daniel' and self.damage > 7:
            return self 
        else:
            enemies, friends = self._return_enemy_friend_list(estimated_camp, players)
            
            # 味方が7以上のダメージの場合、味方に回復として使う
            for friend in friends:
                if friend.damage > 7:
                    return friend
                
            # ダニエルの場合、誰であれ回復を優先する
            if self.character[0] == 'Daniel':
                target = []
                for p in players:
                    if p.damage > 7 and p != self:
                        target.append(p)
                if target:
                    return random.choice(target)
                    
            # 敵が7未満のダメージの場合、敵に攻撃として使う
            for enemy in enemies:
                if enemy.damage < 7:
                    return enemy

        # 条件を満たすプレイヤがいない場合、ランダムなプレイヤを選択
        alive_players = [p for p in players if not p.death]
        if alive_players:
            p = random.choice(alive_players)
        else:
            print("!!! 全員死んでいます !!!")
        return p
        

    def select_recovery_target(self, estimated_camp, players):
        """
        回復を行うターゲットを選択します。一番ダメージの大きい味方を選びます。

        Args:
            estimated_camp (list): プレイヤの推定を表すリスト。学習結果をもとに与えられます。(学習対象以外はNone)

        Returns:
            Player: ターゲットプレイヤ
        """
        enemies, friends = self._return_enemy_friend_list(estimated_camp, players)
        # 学習対象の選択方法。本来味方は一人しかいないため、一番味方らしい人を選択
        if estimated_camp:
            # 味方らしい人がいれば味方、味方らしい人がいなければ一番敵らしくない人を返す
            if friends:
                return friends[0]
            else:
                return enemies[-1]
        
        # そうでない場合は、味方の中でダメージが大きい人を選択
        else:
            # 味方の中でダメージが大きい方を選ぶ
            if len(friends) >= 1:
                target = max(friends, key=lambda x: x.damage)
                return target
        
        # 味方がいない場合、自分以外のランダムなプレイヤを選択
        return self._select_random_player(players)
    

    def select_attack_target(self, estimated_camp, players):
        """
        攻撃：攻撃対象のターゲットを選択します。できるだけ敵を選びます。

        Args:
            estimated_camp (list): プレイヤの推定を表すリスト。学習結果をもとに与えられます。(学習対象以外はNone)

        Returns:
            Player: ターゲットプレイヤ。
        """
        enemies, friends = self._return_enemy_friend_list(estimated_camp, players)
        # 敵がいる場合、敵を選ぶ
        if enemies:
            for enemy in enemies:
                # ”守護天使”を持っていない敵を選ぶ
                if not enemy.guardian_angel and self.is_value_attack(self, enemy):
                    return enemy
        
        # 敵がいない場合、死んでいない自分や味方以外のランダムなプレイヤを選択
        p = self._select_attack_validate_random(friends, players)
        return p 

    def is_value_attack(self, player, target):
        if target.death:
            if self.verbose:
                print(f"!!! not variable target! !!!")
            return False
        
        else:
            self_place = player.area
            target_place = target.area
            if self_place == 2 or self_place == 3:
                if target_place == 6 or target_place == 2 or  target_place == 3:
                    return True
            elif self_place == 6:
                if target_place == 6 or target_place == 4 or target_place == 5:
                    return True        
            elif self_place == 4 or self_place == 5:
                if target_place == 4 or target_place == 5 or target_place == 7:
                    return True
            elif self_place == 7:
                if target_place == 7 or target_place == 9:
                    return True
            elif self_place == 9:
                if target_place == 9 or target_place == 8:
                    return True
            elif self_place == 8:
                if target_place == 8 or target_place == 2 or target_place == 3:
                    return True
            else:
                print("not variable area!")
                
            return False

    def select_black_card_target(self, estimated_camp, players):
        """
        黒のカードで攻撃対象を選ぶ場合のターゲットを選択します。
        できるだけ敵、かつ"いにしえの聖杯"を持っていないプレイヤを選びます。

        Args:
            estimated_camp (list): プレイヤの推定を表すリスト。学習結果をもとに与えられます。(学習対象以外はNone)

        Returns:
            Player: ターゲットプレイヤ
        """
        enemies, friends = self._return_enemy_friend_list(estimated_camp, players)
        
        # 敵がいる場合、敵を選ぶ
        if enemies:
            for enemy in enemies:
                if "いにしえの聖杯" not in enemy.equipment:
                    return enemy
        
        # 敵がいない場合、死んでいない自分や味方以外のランダムなプレイヤを選択
        p = self._select_validate_random(friends, players)
        return p
    
    def steal_equipment_card_target(self, estimated_camp, players):
        """
        装備カードを奪う相手を選ぶ(できるだけ敵から奪う)

        Args:
            estimated_camp (list): プレイヤの推定を表すリスト。学習結果をもとに与えられます。(学習対象以外はNone)

        Returns:
            Player: ターゲットプレイヤ
        """   
        enemies, friends = self._return_enemy_friend_list(estimated_camp, players)
        
        # 敵がいて装備カードを持っている場合、敵を選ぶ
        if enemies:
            for enemy in enemies:
                if enemy.equipment:
                    return enemy
        
        # 装備カードを持っている敵がいない場合、それ以外で装備カードを持っているプレイヤを選択
        for friend in friends:
            if friend.equipment:
                return friend
        
        # 装備カードを持っているプレイヤがいない場合、自分以外のランダムなプレイヤを選択
        return self._select_random_player(players)
    
    def give_equipment_card_target(self, estimated_camp, players):
        """
        装備カードを渡す相手を選ぶ(できるだけ味方に渡す)

        Args:
            estimated_camp (list): プレイヤの推定を表すリスト。学習結果をもとに与えられます。(学習対象以外はNone)

        Returns:
            Player: ターゲットプレイヤ

        """   
        enemies, friends = self._return_enemy_friend_list(estimated_camp, players)
        
        # 味方がいる場合、敵を選ぶ
        if friends:
            return friends[0]
        
        # 味方がいない場合、死んでいない自分や味方以外のランダムなプレイヤを選択
        p = self._select_validate_random(enemies, players)
        return p

    def excalibur_choice(self, target, damage):
        """
        エクスカリバー:正体を公開し、ダメージ増加させるかどうかを評価し、選択の結果をTrueまたはFalseで返します。

        Returns:
            bool: 正体を公開したらダメージが2増加する場合はTrue、しない場合はFalse。
        """
        # ダニエルの場合は選択しない
        if self.character[0] == 'Daniel':
            return False
        #現状のダメージを2増やすことでターゲットを倒せる場合はTrue
        if target.damage + damage <  target.character[2] and target.damage + damage + 2 >= target.character[2]:
            return True
        else:
            return False
        

    def select_area(self, dice_list):
        """
        プレイヤの移動先エリアを選択します。

        Args:
            dice_lit: プレイヤが選択可能なエリアのリスト。

        Returns:
            int: 移動先エリア。
        """

        if 10 in dice_list:
            return 10

        # 陣営が1回でも絞れているプレイヤの数をカウント
        k = sum(1 for i in range(self.player_number) if len(self.detective[i]) != 3)
        
        # 他のプレイヤの陣営が全く絞れていない場合は推理カードを引けるエリアをできるだけ選択
        if k == 0:
            for dice in dice_list:
                if dice in [2, 3, 4, 5]:
                    return dice
                
        # 陣営が絞れている、または推理カードを引けるエリアがない場合、市庁舎を優先
        if 8 in dice_list:
            return 8
            
        # 市庁舎がない場合はブラックミストを優先
        if 4 in dice_list or 5 in dice_list:
            return 4

        # 次は陣営に応じてエリアを選ぶ
        if self.character[1] == 'R':
            if 6 in dice_list:
                return 6
            elif 7 in dice_list:
                return 7
        elif self.character[1] == 'S':
            if 7 in dice_list:
                return 7
            elif 6 in dice_list:
                return 6
        elif self.character[1] == 'C':
            for dice in dice_list:
                if dice in [6, 7]:
                    return dice
                
        # 次にオリバーの隠れ家
        if 9 in dice_list:
            return 9
        
        # 陣営が絞れているかつここまでののどれにも当てはまらなっ他場合は探偵事務所
        if 2 in dice_list or 3 in dice_list:
            return 2
        
        # この時点でどれにも当てはまらない場合はエラーを出力
        else:
            print('---error---')
            print("character:", self.character[1])
            return dice_list[0]  # エラー時はデフォルトで選べるダイス片方を選択

    def select_damage_or_card(self, target, players):
        """
        ダメージを受けるか装備カードを渡すか選択し、それに伴った行動をとる。
        Args:
            target (Player): 装備カードを渡す相手
        """
        # ダニエルの場合はダメージを受ける
        if self.character[0] == 'Daniel':
            self.damage += 1
            return

        # カードを渡す場合のカードの選択（優先順位の低いカードを渡す）
        select_card = max(self.equipment, key=lambda k: self.equipment[k])

        # アリスの場合は装備カードを優先
        if self.character[0] == 'Alice':
            if self.equipment:
                
                self.equipment.remove(select_card)
                target.equipment.append(select_card)
                return
            else:
                self.damage += 1

        # 相手が味方の場合はカードを渡す
        target_index = self.get_index(target, players)
        if len(self.detective[target_index]) == 1 and  next(iter(self.detective[target_index])) == self.character[1]:
            self.equipment.remove(select_card)
            target.equipment.append(select_card)

        else:
            # ダメージが半分以上の場合はカードを渡す
            if self.damage > self.character[2] / 2:
                self.equipment.remove(select_card)
                target.equipment.append(select_card)
            else:
                self.damage += 1
        
    # playerのインデックスを返す
    def get_index(self, player, players):
        for i in range(self.player_number):
            if player == players[i]:
                return i