#coding:utf-8

import random

'''
スロットの情報を扱うクラス
'''
class SlotObject(object):
    def __init__(self):
        # 外れ時の抽選で使用する出目
        self._slot_list = [
            '🎃',
            '<:omatsuri:608412168639217731>',
            '🍉',
            '🍏',
            '🍇',
            '🍒',
            '🤤',
            '💰',
            '🌞',
            '😈',
            '✨',
            '<:tip_kenj_1000000:533845372674768896>',
            '<:kenja:608412274897453076>'
        ]

        # 指定絵柄が揃った時に表示されるリアクションボタン(※任意の絵柄に変更してください。)
        self._rb_list = [
            '👻',
            '👺',
            '🤖',
            '💀'
        ]

        # 出現した時にリアクションボタンを表示させる対象の絵柄(※必要に応じてカンマ区切りで追加してください。)
        self._special_production_pictures = [
            '<:reachan:547382291945488404><:reachan:547382291945488404><:reachan:547382291945488404>'
        ]

        # 出現した時にRUSHに突入する対象の絵柄
        self._rush_pictures = [
            '<:eve2:586454031132655626><:eve2:586454031132655626><:eve2:586454031132655626>'
        ]

    # rb_listのゲッター
    @property
    def rb_list(self):
        return self._rb_list

    # special_production_picturesのゲッター
    @property
    def special_production_pictures(self):
        return self._special_production_pictures

    # rush_picturesのゲッター
    @property
    def rush_pictures(self):
        return self._rush_pictures

    # 各当たり情報を保持する辞書を返す
    def get_hit_dict(self, mention):
        CONTENT_1 = 'picture'
        CONTENT_2 = 'tip'
        CONTENT_3 = 'tip_command'
        return {
            '激賢者ボーナス':{
                CONTENT_1:'<:geki1:586454165728002058><:geki2:586454242236039168><:geki3:586454304492355584>',
                CONTENT_2:'sprts×10000000\nkenj×1000000\nuzz×200000',
                CONTENT_3:f'/tip sprts 10000000 @{mention}\n/tip kenj 1000000 @{mention}\n/tip uzz 200000 @{mention}'
            },
            '超賢者ボーナス':{
                CONTENT_1:'<:tip_kenj_1000000:533845372674768896><:tip_kenj_1000000:533845372674768896><:tip_kenj_1000000:533845372674768896>',
                CONTENT_2:'sprts×1000000\neveryone×300000\neverycond×30000',
                CONTENT_3:f'/tip sprts 1000000 @{mention}\n/tip everyone 300000 @{mention}\n/tip everycond 30000 @{mention}'
            },
            '大賢者ボーナス':{
                CONTENT_1:'<:kenja:608412274897453076><:kenja:608412274897453076><:kenja:608412274897453076>',
                CONTENT_2:'sprts×200000\neveryloto×100000\nkoukou×50000',
                CONTENT_3:f'/tip sprts 200000 @{mention}\n/tip everyloto 100000 @{mention}\n/tip koukou 50000 @{mention}'
            },
            'れあchance':{
                CONTENT_1:'<:reachan:547382291945488404><:reachan:547382291945488404><:reachan:547382291945488404>',
                CONTENT_2:'スタンプを１つ選んでね',
                CONTENT_3:''
            },
            '??×500':{
                CONTENT_1:'🍒🍒🍒',
                CONTENT_2:'sprts×500',
                CONTENT_3:f'/tip sprts 500 {mention}'
            },
            '??×2000':{
                CONTENT_1:'🍇🍇🍇',
                CONTENT_2:'umi×2000',
                CONTENT_3:f'/tip umi 2000 {mention}'
            },
            '??×1500':{
                CONTENT_1:'<:omatsuri:608412168639217731><:omatsuri:608412168639217731><:omatsuri:608412168639217731>',
                CONTENT_2:'祭りだ×1500',
                CONTENT_3:f'/tip 祭りだ 1500 {mention}'
            },
            '??×800':{
                CONTENT_1:'🍉🍉🍉',
                CONTENT_2:'koukou×800',
                CONTENT_3:f'/tip koukou 800 {mention}'
            },
             'エブリーRUSH':{
                CONTENT_1:'<:eve2:586454031132655626><:eve2:586454031132655626><:eve2:586454031132655626>',
                CONTENT_2:'kenj×10000',
                CONTENT_3:f'/tip kenj 10000 {mention}'
            },
            '??×50':{
                CONTENT_1:'🍏🍏🍏',
                CONTENT_2:'dos×50',
                CONTENT_3:f'/tip dos 50 {mention}'
            },
            '??×1000':{
                CONTENT_1:random.choice(self._get_small_hit_pictures()),
                CONTENT_2:'gdrh×1000',
                CONTENT_3:f'/tip gdrh 1000 {mention}'
            },
            'ハズレじゃ':{
                CONTENT_1:''.join(self._get_slot_result().values()),
                CONTENT_2:f'{mention}',
                CONTENT_3:f''
            }
        }

    # リアクションボタンのオッズをランダムで返す
    def get_random_odds(self):
        random_num = random.randint(1,4)
        random_dict = {
            1:'kenj×500000',
            2:'uzz×50000',
            3:'sprts×500000',
            4:'kenj×1000000'
        }
        return random_dict[random_num]

    # 外れ時の出目の辞書を返す
    def _get_slot_result(self):
        """
        ばらばらの出目を返す
        出目が揃った場合はばらばらの出目になるまで抽選する
        """
        while True:
            result = {
                'slot_button_left':random.choice(self._slot_list),
                'slot_button_center':random.choice(self._slot_list),
                'slot_button_right':random.choice(self._slot_list)
            }
            result_set = list(set(result.values()))
            if len(result_set) > 1:
                break

        return result

    # 小当たりの出目のリストを返す
    def _get_small_hit_pictures(self):
        return [
            '🎃🎃🎃',
            '🤤🤤🤤',
            '💰💰💰',
            '🌞🌞🌞',
            '😈😈😈',
            '✨✨✨'
        ]