import random

class BlackCards:
    black_cards = [
        'Vampire Bat',
        'Vampire Bat',
        'Vampire Bat',
        'Olivers Henchman',
        'Olivers Henchman',
        'Three-eyed Black Dog',
        'Riot',
        'Banana Peel',
        'Cursed Doll',
        'Horror Ritual',
        'Sabre',
        'Handgun',
        'Handgun',
    ]
    
    def __init__(self, verbose=False, player_number=5, players=None):
        self.verbose = verbose
        self.disposable_card_functions = {
            'Vampire Bat': self._vampire_bat,
            'Olivers Henchman': self._olivers_henchman,
            'Three-eyed Black Dog': self._three_eyed_black_dog,
            'Riot': self._riot,
            'Banana Peel': self._banana_peel,
            'Cursed Doll': self._cursed_doll,
            'Horror Ritual': self._horror_ritual,
        }
        self.equipment_card = {
            'Sabre': 2, 
            'Handgun': 2,
            'Crossbow': 2,
        }
        self.player_number = player_number
        self.players = players
        
    def process_card(self, name, player, estimated_camp):
        if name in self.disposable_card_functions:
            self.disposable_card_functions[name](player, estimated_camp)
        elif name in self.equipment_card:
            player.equipment[name] = self.equipment_card[name]
            if self.verbose:
                print(f"player {self._get_index(player) + 1} の装備カード {player.equipment}")
        else:
            print(f"Error: Unknown card '{name}'")
        
    def _vampire_bat(self, player, estimated_camp):
        # 自分以外の任意のプレイヤに２ダメージ与え、自分は１回復
        target = player.select_black_card_target(estimated_camp, self.players)
        if self.verbose:
            target_index = self._get_index(target)
            print("player",target_index + 1,"に2ダメージ与える、playerは1回復する")
        if 'Ancient Holy Grail' in target.equipment:
            if self.verbose:
                print("いにしえの聖杯を装備しているため、ダメージを受けない")
        else:
            target.damage += 2
            player.damage = max(0, player.damage-1)

    def _three_eyed_black_dog(self, player, estimated_camp):
        #自分と任意のプレイヤに２ダメージ
        target = player.select_black_card_target(estimated_camp, self.players)         
        player.damage += 2
        target_index = self._get_index(target)
        if self.verbose:
            print("player",target_index + 1,"とplayerに2ダメージ与える")  
        if 'Ancient Holy Grail' in target.equipment:
            if self.verbose:
                print("いにしえの聖杯を装備しているため、ダメージを受けない")
        else:
            target.damage += 2

    def _riot(self, player, _):
        # ２つのダイスの出目の合計値のエリアにいるプレイヤに３ダメージ    
        dice6 = random.randint(1,6)
        dice4 = random.randint(1,4)
        sum_dice=dice6+dice4
        if self.verbose:
            print(f"{sum_dice} エリアにいる全てのplayerに3ダメージ与える")
        for p in self.players:
            if p.area == sum_dice:
                p.damage += 3

    def _cursed_doll(self, player, estimated_camp):
        #ダイスの目が４より大きければ自分に、小さければ任意のプレイヤに３ダメージ
        dice6 = random.randint(1,6)
        if dice6 > 4:
            if 'Ancient Holy Grail' in player.equipment:
                if self.verbose:
                    print("Ancient Holy Grailを装備しているため、ダメージを受けない")
            else:
                if self.verbose:
                    print("playerに3ダメージ与える")
                player.damage += 3
        else:
            target = player.select_black_card_target(estimated_camp, self.players)
            if 'Ancient Holy Grail' in target.equipment:
                if self.verbose:
                    print(f"Ancient Holy Grailを装備しているため、ダメージを受けない")
            else:
                if self.verbose:
                    print(f"player {self._get_index(target) + 1} に3ダメージ与える")
            target.damage += 3

    def _horror_ritual(self, player, _):
        # シャドウの場合、正体を公開したらダメージ全回復
        if player.character[1] == 'S':
            #正体を公開したら
            is_revealed = player.reveal_recover_choice()
            if is_revealed:
                if self.verbose:
                    print("playerはシャドウである。公開したためplayerのダメージを0にする。")
                player.damage = 0
                player_index = self._get_index(player)
                for p in self.players:
                    p.detective[player_index]={'S'}

    def _olivers_henchman(self, player, equipment_camp):
        # 任意の装備カードを1枚奪う
        target = player.steal_equipment_card_target(equipment_camp, self.players)
        if target.equipment:
            # 装備カードの中で一番優先順位の高いものを選ぶ
            select_card = min(target.equipment, key=target.equipment.get)
            if self.verbose:
                target_index = self._get_index(target)
                print(f"player {target_index + 1} から装備カード {select_card} を奪う")
            player.equipment[select_card] = target.equipment[select_card]
            del player.equipment[select_card]

    def _banana_peel(self, player, estimated_camp):
        # 装備カードの一つを他の任意のプレイヤに渡す、なければ1ダメージ受ける
        if player.equipment:
            target = player.give_equipment_card_target(estimated_camp, self.players)
            # 装備カードの中で一番優先順位の低いものを選ぶ
            select_card = max(player.equipment, key=player.equipment.get)
            if self.verbose:
                target_index = self._get_index(target)
                print(f"player {target_index + 1} に装備カード {select_card} を渡す")
            target.equipment[select_card] = player.equipment[select_card]
            del player.equipment[select_card]
        else:
            if self.verbose:
                print("装備カードがないため1ダメージ受ける")
            player.damage += 1


    def attack_damage(self, player):
        # playerの攻撃時の黒のカードでのダメージ増加量を返す
        black_equipment_count = sum(1 for item in player.equipment if item in self.equipment_card)
        return black_equipment_count


    def _get_index(self, player):
        # playerのindexを返す
        for i in range(self.player_number):
            if player == self.players[i]:
                return i
