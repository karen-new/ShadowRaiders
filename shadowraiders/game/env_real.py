#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 25 15:35:23 2022

@author: karen
"""

import random
import gym
import numpy as np
from more_itertools import distinct_permutations
from shadowraiders.cards.black_cards import BlackCards
from shadowraiders.cards.white_cards import WhiteCards
from shadowraiders.cards.detective_cards import DetectiveCards
from shadowraiders.player_actions.player_real import Player

#名前：陣営：HP：特殊効果
shadow_characters = [
    'Ulrich:S:11:lie',
    'Vampire:S:13:bloodsucking',
    'Werewolf:S:14:counterattack'
    ]

raider_characters = [
    'Emi:R:10:teleport',
    'Felix:R:12:astralmace',
    'Gordon:R:14:invinciblebarrier'
    ]

citizen_characters = [
    'Alice:C:8:rabbitheal',
    'Daniel:C:13:exclamation'
]

shadow_characters = [s.split(':') for s in shadow_characters]
raider_characters = [r.split(':') for r in raider_characters]
citizen_characters = [c.split(':') for c in citizen_characters]

shadow_characters = [[s[0],s[1],int(s[2]),s[3]] for s in shadow_characters]
raider_characters = [[r[0],r[1],int(r[2]),r[3]] for r in raider_characters]
citizen_characters = [[c[0],c[1],int(c[2]),c[3]] for c in citizen_characters]

#プレイヤ人数
player_number = 5


class RealEnv(gym.Env):   
    #キャラクター：エリア：装備:ダメージ量  
    
    def __init__(self, verbose=True):
        # 状態空間を定義
        # 各プレイヤの観測空間
        player_obs_space = gym.spaces.Dict({
            'card': gym.spaces.Box(low=-1, high=1, shape=(3,), dtype=np.float32),
            'blackmist': gym.spaces.Box(low=-1, high=1, shape=(), dtype=np.float32),
            'attack': gym.spaces.Box(low=-1, high=1, shape=(), dtype=np.float32)
        })

        # 観測空間の形状を定義
        self.observation_space = gym.spaces.Tuple([player_obs_space] * (player_number - 1))

        # 状態の範囲を定義
        # self.observation_space.shape=(20,)
        # 行動空間を定義
        self.action_space = gym.spaces.Box(low=0,high=1,shape=((player_number-1)*4,))
        # 報酬の範囲を定義       
        self.reward_range = (0,1)
        
        self.verbose = verbose    
        self.players = [None] * player_number
        self.index = []
        self.white_deck = []
        self.black_deck = []
        self.detective_deck = []
        

    def reset(self):
#         print(f"***game reset***")
        if self.verbose:
            print(f"***** game reset *****")
        
        # 市民以外の各陣営から必要な数のキャラクターをランダムに選択
        non_citizen_characters = random.sample(shadow_characters, 2) + random.sample(raider_characters, 2)
        # 順番をランダムに変更
        random.shuffle(non_citizen_characters)
        
        # self.players[0]（テストの対象）は市民以外から選択し、選択されたキャラクターはキャラクターのリストから削除
        self.players[0] = Player(non_citizen_characters.pop(0))
        
        #市民を加えた陣営からなるキャラクターのリストを作成
        characters = non_citizen_characters + random.sample(citizen_characters, player_number - (len(non_citizen_characters)+1))
        random.shuffle(characters)

        # 選択されたキャラクターをself.player[0]以外のプレイヤに割り当てる
        for i in range(player_number-1):
            self.players[i+1] = Player(characters[i])

        self.white = WhiteCards(self.verbose, player_number, self.players)
        self.black = BlackCards(self.verbose, player_number, self.players)
        self.role_estimates = DetectiveCards(self.verbose, player_number, self.players)

        # 白のカードの初期設定
        self.white_deck = WhiteCards.white_cards.copy()
        random.shuffle(self.white_deck)
        
        # 黒のカードの初期設定
        self.black_deck = BlackCards.black_cards.copy()
        random.shuffle(self.black_deck)

        # 推理カードの初期設定
        self.detective_deck = DetectiveCards.detective_cards.copy()
        random.shuffle(self.detective_deck)

        self.index = list(range(player_number)) # playの順番
        random.shuffle(self.index)
        
        if self.verbose:
            print(f"agent role: {self.players[0].character[1]}")
        
        return self.get_obs()
    
    
    def step(self, action, estimation_precision = False):
        done = False # ゲームが終了したかどうかを示すフラグ
        info = None # 追加情報
        reward=0 # 報酬の初期値を設定
        target=None # 攻撃の対象プレイヤ
        estimated_camp = None # 推定陣営のリスト(学習結果から与えられる)

        # 推定精度を設定して行う場合
        if estimation_precision:
            action = self.get_estimated_camp(estimation_precision)
        if self.verbose:
            print(f"action: {action}")

        # 各プレイヤのHPを表示
        if self.verbose:
            print(f"各プレイヤの体力")
            for player in self.players:
                print(f"player {self.get_index(player) + 1} : {player.character[2]-player.damage}" )   
        
        # プレイヤごとにループ
        for i in self.index:
            # プレイヤが生存している場合
            player = self.players[i]
            if not player.death:
                while(True): # 封印の知恵を引いた場合の処理を行うためのループ
                    if self.verbose:
                        print(f"-player {i + 1} turn-")
                        print(f"プレイヤの陣営: {player.character[1]}")

                    if player == self.players[0]: # 学習対象のエージェントの場合
                        estimated_camp = action
                    else:
                        estimated_camp = False
                        
                    self.play(player, estimated_camp)              

                    #まだ勝敗がついていなければ攻撃も行う
                    if not self.win_lose(self.players[0]):
                        target = player.select_attack_target(estimated_camp, self.players)
                        if self.verbose:
                            print(f"攻撃対象: player {self.get_index(target) + 1}")

                        if target and self.is_value_attack(player, target):
                            self.attack(player, target)
                        else:
                            if self.verbose:
                                print(f"not target")
                        
                    # 勝敗の判定
                    win_lose = self.win_lose(self.players[0])
                    if win_lose:
                        done = True
                        info = self.get_info(action)
                        if win_lose == 'win':
                            reward = 1
                        else:
                            reward = 0
                        if self.verbose:
                            print(f"obs: {self.get_obs()}, reward: {reward}")
                        return self.get_obs(), reward, done, info

                    # 封印の知恵を引いた場合、もう一度手番を行う
                    if player.seal_of_wisdom:
                        player.seal_of_wisdom = False
                        if self.verbose:
                            print(f"player {i + 1} はもう一度手番を行う")
                        continue
                    else:
                        break


        # 勝敗が決まらなかった場合
        done = False
        if self.verbose:
            print(f"obs: {self.get_obs()}")
        reward=0
        return self.get_obs(), reward, done, info
    
    # 現在は各プレイヤのダメージのみ返す
    def get_obs(self):
        return np.array([player.damage for player in self.players])

    # 3bit / 正しく推定できているプレイヤーの数を返す
    def get_info(self, estimate_camp): 
        correct = [0,0,0]
        j = 0
        for i, player in enumerate(self.players[1:], start=1):
            camp = player.character[1]
            if camp == 'C':
                if estimate_camp[(i - 1) * 3 + 2] > 0.5:
                    correct[2] += 1
            elif camp == self.players[0].character[1]:
                if estimate_camp[(i - 1) * 3] > 0.5:
                    correct[0] += 1
            else:
                if estimate_camp[(i - 1) * 3 + 1] > 0.5:
                    correct[1] += 1

        if self.verbose:
            print(f"correct: {correct}")
        return correct, sum(correct)/4 # 推定の正しい数を返す

    # playerのインデックスを返す
    def get_index(self, player):
        for i in range(player_number):
            if player == self.players[i]:
                return i

    # 推定精度を設定してテストを行う場合。推定精度に応じた推定陣営リストを返す
    def get_estimated_camp(self, estimation_precision):
        """
        推定精度に応じた推定陣営リストを返します。
        estimation_precision が推定結果が分かっている人数を示します。
        """
        estimated_camp = [0] * (player_number - 1) * 3
        i = 0
        known_count = 0

        for p in self.players:
            if not p is self.players[0]:
                if known_count < estimation_precision:
                    if p.character[1] == "C":
                        estimated_camp[i] = 0
                        estimated_camp[i + 1] = 0
                        estimated_camp[i + 2] = 1
                    elif p.character[1] == self.players[0].character[1]:
                        estimated_camp[i] = 1
                        estimated_camp[i + 1] = 0
                        estimated_camp[i + 2] = 0
                    else:
                        estimated_camp[i] = 0
                        estimated_camp[i + 1] = 1
                        estimated_camp[i + 2] = 0
                    known_count += 1
                else:
                    estimated_camp[i] = 0.3
                    estimated_camp[i + 1] = 0.3
                    estimated_camp[i + 2] = 0.3
                i += 3
        # print(estimated_camp)
        return estimated_camp

    # targetに攻撃できるか
    # 全てのエリアのプレイヤに攻撃可能
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
        
    
    # プレイヤがターゲットに攻撃を行う際の処理を行う
    def attack(self, player, target):
        # 本来のゲーム設定での攻撃の場合(サイコロの出目でダメージを決定)
        dice6 = random.randint(1,6)
        dice4 = random.randint(1,4)
        damage = abs(dice6 - dice4)

        # ダメージは基本地1で固定
        # 装備カードを持っている場合のみ、ダメージを変更
        damage += self.black.attack_damage(player)
        if "Excalibur" in player.equipment and player.character[1] == 'R':
            self.white.excalibur(player, target, damage)
            if player.excalibur:
                damage += 2

        if target.guardian_angel:
            if self.verbose:
                print(f"守護天使を装備しているため、ダメージを受けない")
        else:
            if self.verbose:
                print(f"{damage}ダメージ")
            target.damage += damage

        # もし攻撃によりターゲットが脱落した場合、ターゲットの装備を１つ奪う
        if self.check_death(target):
            # 銀のロザリオを装備している場合、全ての装備を奪う
            if  "Silver Rosary" in player.equipment:
                player.equipment.update(target.equipment)
                if self.verbose:
                    print(f"player {self.get_index(player) + 1} から装備カード {target.equipment} を奪う")
            else:
                if target.equipment:
                    # 装備カードの中で一番優先順位の高いものを選ぶ
                    select_card = min(target.equipment, key=target.equipment.get)
                    player.equipment[select_card] = target.equipment[select_card]
                    del player.equipment[select_card]
                    if self.verbose:
                        print(f"player {self.get_index(target) + 1} から装備カード {select_card} を奪う")
    
    # プレイヤの死亡判定
    def check_death(self, player):
        if player.damage >= int(player.character[2]):
            player.death = True
            if self.verbose:
                print(f"--player {self.get_index(player) + 1} is death--")
            for t in self.players:
                t.detective[self.get_index(player)] = {player.character[1]}
            return True
        else:
            return False


    #プレイヤ全員の生死の確認し、死亡しているプレイヤを検出して各処理を行う
    def get_all_life_conditions(self): 
        for player in self.players:
            # プレイヤの生死状態を確認し、死亡プレイヤを検出
            if not player.death:
                self.check_death(player)

    
    #targetの勝敗を返す
    def win_lose(self, target):
        winner = 'N'
        r = 0
        s = 0
        death_count = 0
        daniel_flag = False
        alice_flag = True

        self.get_all_life_conditions()
        
        # 各陣営の死亡人数を確認
        for player in self.players:
            if player.death:
                death_count +=1
                if player.character[1] == 'R':
                    r += 1
                elif player.character[1] == 'S':
                    s += 1
                elif player.character[0] == 'Daniel':
                    daniel_flag = True
                elif player.character[0] == 'Alice':
                    alice_flag = False

        if daniel_flag and death_count == 1:
            if self.verbose:
                print(f"Daniel win")
            winner = 'Daniel'
                    
        elif r<2 and s<2: # 勝者がいない場合
            return False
        
        else:
            if winner == 'N':
                if r >= 2: #レイダーが全員死んでいる場合、シャドウの勝利
                    if self.verbose:
                        print(f"Shadow win")
                    if alice_flag:
                        if self.verbose:
                            print(f"Alice win")
                    winner = 'S'
                if s >= 2: #シャドウが全員死んでいる場合、レイダーの勝利
                    if self.verbose:
                        print(f"Raiders win")
                    if alice_flag:
                        if self.verbose:
                            print(f"Alice win")
                    winner = 'R'
                
        # プレイヤが勝者か敗者かを判定して返す
        # TODO: aliceが勝利した場合は返せてない
        if target.character[1] == winner or target.character[0] == winner:
            return 'win'
        else:
            return 'lose'
        
            
    def play(self, player, estimated_camp):
        # 6面と4面のダイスを振る
        dice6 = random.randint(1,6)
        dice4 = random.randint(1,4)
        sum_dice = dice6 + dice4
        if self.verbose:
            print(f"ダイスの目：{dice4} , {dice6} , 合計：{sum_dice}")

        # プレイヤが神秘のコンパスを装備している場合、ダイスをもう一度振って好きな方を選択
        if "'Mystic Compass'" in player.equipment:
            dice6 = random.randint(1,6)
            dice4 = random.randint(1,4)
            sum_dice_2 = dice6 + dice4
            sum_dice = player.select_area([sum_dice, sum_dice_2])
            if self.verbose:
                print(f"player {self.get_index(player) + 1} は神秘のコンパスを装備している。エリアを{sum_dice}、{sum_dice_2}から選ぶ")


        # ダイスの目が10の場合、今いる場所以外どのエリアにも行ける、今はランダム
        if sum_dice == 10:
            inaccessible_area = [player.area]
            if player.area == 2 or 3:
                inaccessible_area = [2,3]
            elif player.area == 4 or 5:
                inaccessible_area = [4,5]
            accessible_area = [x for x in [2,4,6,7,8,9] if not x in inaccessible_area]
            sum_dice = player.select_area(accessible_area)

        player.area = sum_dice

        self.area(player, estimated_camp)
        
    
    def area(self, player, estimated_camp):
        area_actions = {
            2: self.detective_agency, #探偵事務所
            3: self.detective_agency,
            4: self.blackmist, #ブラックミスト地区
            5: self.blackmist,
            6: self.cathedral, #大聖堂
            7: self.underground_passage, #地下通路
            8: self.city_hall,  #市庁舎
            9: self.olivers_hideout #オリバーの隠れ家
        }
        
        if player.area in area_actions:
            area_actions[player.area](player, estimated_camp)
        else:
            print(f"!!! area error !!!")

    # 推理カードを引くエリア
    def detective_agency(self, player, _):
        if self.verbose and player.area in [2,3]:
            print(f"プレイヤのエリア：探偵事務所")
        # 山札がなくなった場合、山札を最初の状態にリセット
        if not self.detective_deck :
            self.detective_deck = DetectiveCards.detective_cards.copy()
            
        # ランダムに推理カードを選択し、デッキから削除
        detective_card = random.choice(self.detective_deck)
        self.detective_deck.remove(detective_card)
        if self.verbose:
            print(f"推理カード: {detective_card}")
        self.role_estimates.process_card(detective_card, player)


    # 白のカード、黒のカード、推理カードのうちいずれか一枚を引くエリア
    def blackmist(self, player, estimated_camp):
        if self.verbose:
            print(f"プレイヤのエリア： ブラックミスト地区")

        #３種類のうち好きなカードを選ぶ
        card = player.blackmist_choice()
        
        if card == "W":
            # 白のカードを引く処理
            self.cathedral(player, estimated_camp)
            
        if card == "B":
            # 黒のカードを引く処理
            self.underground_passage(player, estimated_camp)
                
        if card == "D":
            # 推理カードを引く処理
            self.detective_agency(player, estimated_camp)
    

    # 白のカードを引くエリア        
    def cathedral(self, player, estimated_camp):
        if self.verbose and player.area == 6:
            print(f"プレイヤのエリア： 大聖堂")

        # "白"のデッキがない場合
        if not self.white_deck:
            self.white_deck = WhiteCards.white_cards.copy()
        
        # "白"のデッキからランダムにカードを選択し、デッキから削除
        white_card = random.choice(self.white_deck)
        self.white_deck.remove(white_card)
        if self.verbose:
            print(f"白のカード: {white_card}")
        self.white.process_card(white_card, player, estimated_camp)


    # 黒のカードを引くエリア
    def underground_passage(self, player, estimated_camp):
        if self.verbose and player.area == 7:
            print(f"プレイヤのエリア： 地下通路")

        # "黒"のデッキがない場合
        if not self.black_deck:
            self.black_deck = BlackCards.black_cards.copy()
        
        # "黒"のデッキからランダムにカードを選択し、デッキから削除
        black_card = random.choice(self.black_deck)
        self.black_deck.remove(black_card)
        if self.verbose:
            print(f"黒のカード: {black_card}")
        self.black.process_card(black_card, player, estimated_camp)

            
    # 任意のプレイヤに2ダメージ与えるか1ダメージ回復するエリア
    def city_hall(self, player, estimated_camp):
        if self.verbose:
            print(f"プレイヤのエリア： 市庁舎")
        
        target, act = player.city_hall_choice(estimated_camp, self.players)
        target_index = self.get_index(target)
        
        if act == "heal":
            if self.verbose:
                print(f"市庁舎： player {target_index + 1} を回復")
            if target.damage>0:
                target.damage -= 1
                        
        elif act == "attack":
            if self.verbose:
                print(f"市庁舎： player {target_index + 1} を攻撃")
            if "Lucky Brooch" in target.equipment:
                if self.verbose:
                    print(f"幸運のブローチを装備しているため、ダメージを受けない")
            else:
                target.damage += 2

    
    # 任意のプレイヤから装備カードを奪えるエリア
    def olivers_hideout(self, player, estimated_camp):
        if self.verbose:
            print(f"プレイヤのエリア： オリバーの隠れ家")

        target = player.steal_equipment_card_target(estimated_camp, self.players)
        if target.equipment:
            # 装備カードの中で一番優先順位の高いものを選ぶ
            select_card = min(target.equipment, key=target.equipment.get)
            player.equipment[select_card] = target.equipment[select_card]
            del player.equipment[select_card]
            if self.verbose:
                print(f"オリバーの隠れ家： player {self.get_index(target) + 1} から装備カード[ {select_card} ]を奪う")
        else:
            if self.verbose:
                print(f"オリバーの隠れ家： 装備カードを所持するプレイヤがいません")
            player.damage += 1

