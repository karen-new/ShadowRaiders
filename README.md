# ShadowRaiders

## 概要
pythonを用いた、ゲームShadowraidersの5人プレイ用のサンプルコード
OpenAIGymを用いており、強化学習用に使用することを前提としています。
actionで推定情報を渡し、obsは現在はHP情報のみを渡しています。
Shadowraidersとは：http://www.cosaic.co.jp/games/sr.html

## 環境
- OS: Windows10  
- Python: 3.9.15  
### 利用ライブラリ
- numpy: 1.19.5  
- OpenAI Gym: 0.26.2

## 使用例
test.pyでゲームを複数回プレイさせることができます。
以下のコマンドで改変ルールをヒューリスティックプレイヤ5人で10000回プレイさせます。
```
$python main.py
```

## ファイル構造
### shadowraiders
ゲームに関するパッケージ
#### game
ゲームの進行や処理等
- env.py : ランダム性を下げた改変ルール
- env_real.py : 本来のルール
#### player_actions
プレイヤの行動選択の処理等
- player.py : 改変ルールでのヒューリスティックプレイヤ
- player_random : ランダムな行動をとるプレイヤ
- player_real.py : 本来のルールでのヒューリスティックプレイヤ
#### cards
各カードの情報や処理等
- black_cards.py : 黒のカード
- detective_cards.py : 推理カード
- white_cards.py : 白のカード

### tests
システムテスト
