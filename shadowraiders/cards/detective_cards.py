import random
import numpy as np

class DetectiveCards:
    detective_cards = [
        'citizen or shadow',
        'citizen or shadow',
        'citizen or raider',
        'citizen or raider',
        'shadow or raider',
        'shadow or raider',
        'raider',
        'raider',
        'raider2',
        'shadow1',
        'shadow2',
        'shadow3',
        'citizen',
        'HP11',
        'HP12',
        'open'
    ]
    detective_cards = [b.split(':') for b in detective_cards]

    def __init__(self, verbose = False, player_number = 5, players = None):
        self.verbose = verbose
        self.player_number = player_number
        self.players = players
    
    # 推理カードを引いた際の処理
    def process_card(self, name, player):
        # 回復系の推理カードの場合healをtrueに、そうでない場合falseにする
        heal = name in ['raider2', 'shadow3', 'citizen']
    
        # ターゲットをプレイヤーの detective リストの状態に応じて選ぶ
        target, target_index = self.select_target(player, heal)
        
        if self.verbose:
            print("推理カードを渡す相手 : player", target_index + 1)
            
        if name == 'citizen or shadow':
            if target.character[1] == 'S' or target.character[1] == 'C':
                player.detective[target_index].discard("R")
                #装備カードを渡す、または１ダメージ受ける
                target.select_damage_or_card(player)
            else:
                player.detective[target_index] = {'R'}
            
        if name == 'citizen or raider':
            if target.character[1] == 'R' or target.character[1] == 'C':
                player.detective[target_index].discard("S")
                #装備カードを渡す、または１ダメージ受ける
                target.select_damage_or_card(player)          
            else:
                player.detective[target_index] = {"S"}
        
        if name == 'shadow or raider':
            if target.character[1] == 'R' or target.character[1] == 'S':
                player.detective[target_index].discard("C")
                #装備カードを渡す、または１ダメージ受ける
                target.select_damage_or_card(player)   
            else:
                player.detective[target_index] = {'C'}
                
        if name == 'raider':
            if target.character[1] =='R':
                player.detective[target_index] = {'R'}
                target.damage += 1
            else:
                player.detective[target_index].discard('R')
                
        if name == 'raider2':
            if target.character[1] =='R':
                player.detective[target_index] = {'R'}
                if target.damage == 0:
                    target.damage += 1
                else:
                    target.damage -= 1
            else:
                player.detective[target_index].discard('R')
                    
        if name == 'shadow1':
            if target.character[1] == 'S':
                player.detective[target_index] = {'S'}
                target.damage += 1
            else:
                player.detective[target_index].discard('S')
            
        if name == 'shadow2':
            if target.character[1] == 'S':
                player.detective[target_index] = {'S'}
                target.damage += 2
            else:
                player.detective[target_index].discard('S')
        
        if name == 'shadow3':
            if target.character[1] == 'S':
                player.detective[target_index] = {'S'}
                if target.damage == 0:
                    target.damage += 1
                else:
                    target.damage -= 1   
            else:
                player.detective[target_index].discard('S')
                    
        if name == 'citizen':
            if target.character[1] == 'C':
                player.detective[target_index] = {'C'}
                if target.damage == 0:
                    target.damage += 1
                else:
                    target.damage -= 1   
            else:
                player.detective[target_index].discard('C')
                
        if name == 'HP11':
            if target.character[0] in ['Ulrich', 'Emi']:
                #player.detective[target_index].append('under11')
                target.damage += 1
            #else:
            #   player.detective[target_index].append('above12')
                    
        if name == 'HP12':
            if target.character[0] in ['Vampire', 'Werewolf', 'Felix', 'Gordon']:
            #  player.detective[target_index].append('above12')
                target.damage += 2
            #else:
            #   player.detective[target_index].append('under11')
                
        if name =='open':
            player.detective[target_index] = {target.character[1]}
            
            
        # 味方は一人しかいないため除く
        for de in player.detective:
            if len(de) == 1:
                character = next(iter(de))
                if character == player.character[1]:
                    for d in player.detective:
                        if d is not de:
                            d.discard(character)

    
    # ターゲットを選択し、ターゲットとそのインデックスを返す
    def select_target(self, player, heal):
        target = None
        target_index = -1
        #プレイヤーの順番を固定にならないようにする
        index = [i for i in range(0, self.player_number)]
        np.random.shuffle(index)

        # まだひとつも絞れていないプレイヤーがいる場合そのプレイヤーをターゲットとする
        for i in range(self.player_number):
            j = index[i]
            if player != self.players[j]:
                if len(player.detective[j]) == 3:
                    target = self.players[j]
                    target_index = j
                    return target, target_index

        # 全く絞れていないプレイヤーがいない場合、2つまでしか絞れていないプレイヤーをターゲットとする
        if target is None:
            for i in range(self.player_number):
                j = index[i]
                if player != self.players[j]:
                    if len(player.detective[j]) == 2:
                        target = self.players[j]
                        target_index = j
                        return target, target_index

        # 全員完全に推定できている場合、攻撃になるカードは敵に、回復になるカードは味方に使う
        if target is None:
            for i in range(self.player_number):
                j = index[i]
                if player != self.players[j]:
                    if len(player.detective[j]) == 1:
                        if heal:
                            if player.character[1] == next(iter(player.detective[j])):
                                target = self.players[j]
                                target_index = j
                                return target, target_index
                        else:
                            if player.character[1] != next(iter(player.detective[j])):
                                target = self.players[j]
                                target_index = j
                                return target, target_index

        if target is None:
            target = random.choice(self.players)
            while target is player:
                target = random.choice(self.players)
            target_index = self.get_index(target)

        return target, target_index