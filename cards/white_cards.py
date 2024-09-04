import random

class WhiteCards:
    white_cards = [
        'Healing Holy Water',
        'Healing Holy Water',
        'Judgment Flash',
        'Advent',
        'Guardian Angel',
        'Wisdom of Sealing',
        'First Aid',
        'Happy Cookie',
        'Grace',
        'Mirror of Dispelling Darkness',
        'Silver Rosary',
        'Excalibur',
        'Mystic Compass',
        'Lucky Brooch',
        'Ancient Holy Grail',
        'Mystic Compass'
    ]
    
    def __init__(self, verbose=False, player_number=5, players=None):
        self.verbose = verbose
        self.disposable_card_functions = {
            'Healing Holy Water': self._healing_holy_water,
            'Judgment Flash': self._judgment_flash,
            'Advent': self._advent,
            'Guardian Angel': self._guardian_angel,
            'Wisdom of Sealing': self._wisdom_of_sealing,
            'First Aid': self._first_aid,
            'Happy Cookie': self._happy_cookie,
            'Grace': self._grace,
            'Mirror of Dispelling Darkness': self._mirror_of_dispelling_darkness,
        }
        self.equipment_card = {
            'Silver Rosary': 4, # 攻撃によってプレイヤが脱落した場合、そのプレイヤの装備カードを全て獲得する
            'Excalibur': 6, # レイダーの場合、正体を公開したらダメージが2増加する
            'Lucky Brooch': 5, # 市庁舎によるダメージを受けない(回復は可能)
            'Ancient Holy Grail': 1, # 三つ目の黒犬、吸血コウモリ、呪いの人形の効果を無効化
            'Mystic Compass': 3, # 移動する際、ダイスを２度振り、どちらかの出目を選んで移動する
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
        
    def _healing_holy_water(self, player, _):
        # 自分のＨＰを2回復
        if self.verbose:
            print("自分のHPを2回復")
        # プレイヤのダメージを2回復（0未満にはならない）
        player.damage = max(0, player.damage - 2)

    def _judgment_flash(self, player, _):
        # 自分以外全員に２ダメージ
        if self.verbose:
            print("自分以外全員に２ダメージ")
        for p in self.players:
            if p is not player:
                p.damage += 2

    def _advent(self, player, _):
        # レイダーの場合、正体を公開したらダメージ０にできる
        if player.character[1] == 'R':
            is_revealed = player.reveal_recover_choice()
            if is_revealed:
                if self.verbose:
                    print("playerはレイダーである。公開したためplayerのダメージを0にする。")
                player.damage = 0
                player_index = self._get_index(player)
                for p in self.players:
                    p.detective[player_index]={'R'}

    def _first_aid(self, player, estimated_camp):
        # 任意のプレイヤのダメージを７にする（自分でも可）
        target = player.first_aid_choice(estimated_camp, self.players)
        if self.verbose:
            target_index = self._get_index(target)
            print("player", target_index + 1, "のダメージを7にする")
        target.damage = 7

    def _happy_cookie(self, player, _):
        # レイダーの場合、正体を公開したらダメージ０にできる
        if player.character[0] == 'Alice' or player.character[0] == 'Ulrich':
            is_revealed = player.reveal_recover_choice()
            if is_revealed:
                if self.verbose:
                    print("playerはレイダーである。公開したためplayerのダメージを0にする。")
                player.damage = 0
                player_index = self._get_index(player)
                for p in self.players:
                    p.detective[player_index]={'R'}

    def _grace(self, player, estimated_camp):
        # 自分以外の任意のプレイヤのダメージをサイコロの出目分回復
        target = player.select_recovery_target(estimated_camp, self.players)
        dice6 = random.randint(1,6)
        if self.verbose:
            target_index = self._get_index(target)
            print("player", target_index + 1, "のダメージを", dice6, "回復する")
        target.damage = max(0, target.damage - dice6)

    def _mirror_of_dispelling_darkness(self, player, _):
        # シャドウの場合正体を公開しなければならない
        if player.character[0] == 'Vampire' or player.character[0] == 'Werewolf':
            if self.verbose:
                print("playerはシャドウである")
            player_index = self._get_index(player)
            for p in self.players:
                    p.detective[player_index]={'S'}

    def _guardian_angel(self, player, _):
        # 次の手番の最初まで攻撃によるダメージを受けない
        # 市庁舎やカードによる攻撃は受ける
        if self.verbose:
            print("次の手番の最初まで攻撃によるダメージを受けない")
        player.guardian_angel = True

    def _wisdom_of_sealing(self, player, _):
        # この手番の終了後、もう一度手番を行う
        if self.verbose:
            print("この手番の終了後、もう一度手番を行う")
        player.seal_of_wisdom = True

    def excalibur(self, player, target, damage):
        # レイダーの場合、正体を公開したらダメージが2増加する
        # 既に公開している場合は変更不可能
        if not player.excalibur:
            is_revealed = player.excalibur_choice(target, damage)
            if is_revealed:
                if self.verbose:
                    print("playerはレイダーである。公開したためplayerの攻撃ダメージを2増加する。")
                player.excalibur = True
                player_index = self._get_index(player)
                for p in self.players:
                    p.detective[player_index]={'R'}

    def _get_index(self, player):
        # playerのindexを返す
        for i in range(self.player_number):
            if player == self.players[i]:
                return i