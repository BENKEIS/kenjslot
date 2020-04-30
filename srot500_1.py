import random
import asyncio
import discord
import csv
import pandas as pd
import os
import datetime
import time
from collections import defaultdict
from slot_object import SlotObject
from log_object import LogObject
import yaml

token = os.environ['DISCORD_BOT_TOKEN']

client = discord.Client()
with open(f'{os.getcwd()}/config.yml', 'r', encoding='utf-8') as yml:
    config_dict = yaml.load(yml, Loader=yaml.SafeLoader)

####
##   ConfigKey setting
####

SLOT_CONFIG_KEY = 'slot_info'
RANDOM_SIZE_KEY = 'random_generate_size'
PROBABILITY_KEY = 'key_probabilities'

MESSAGE_CONFIG_KEY = 'message_info'
RECIEVE_KEY = 'recieve'
SEND_KEY = 'send'

ID_CONFIG_KEY = 'id_info'

OTHER_CONFIG_KEY = 'other_info'

RUSH_CONFIG_KEY = 'rush_info'
RUSH_TIP_KEY = 'rush_tips'
RUSH_PICTURE_RANDOM_KEY = 'random_generate_size_key'
RUSH_PICTURE_KEY = 'key_probabilities'

####
##   Global settings
####

RUSH_FLG_FILE_PATH = f'{os.getcwd()}/rush_flg'
DO_SLOT_FILE_PATH = f'{os.getcwd()}/do_slot_flg'
USER_FILE_PATH = f'{os.getcwd()}/user_log'

DATE_USE_LIMIT = config_dict[OTHER_CONFIG_KEY]['date_use_time']
UZURA_CMD_WAIT_SECOND = config_dict[OTHER_CONFIG_KEY]['uzura_command_wait_second']

SLOT_BOT_ID = int(config_dict[ID_CONFIG_KEY]['slot_bot_id'])
UZURA_BOT_ID = int(config_dict[ID_CONFIG_KEY]['uzura_bot_id'])

message_config = config_dict[MESSAGE_CONFIG_KEY]
recieve_messages = message_config[RECIEVE_KEY]
send_messages = message_config[SEND_KEY]

####
##   Functions
####

def check_use_times(author):
    """
    「./user_log/ユーザー名.csv」が存在するか判定し、以下の処理を行う。
    存在しない場合は以下のヘッダーのCSVファイルを出力する。
    ['user_id','date','use_times']

    「./user_log/ユーザー名.csv」を読み込み、「date」、「use_times」列で一意のkeyとして利用回数を判定する
    指定した上限回数より少ない場合は「True」、多い場合はFalseを返す

    Parameters
    ------------------------------
    author : str
        ユーザー名

    Returns
    ------------------------------
    ret_flg : bool
        利用回数が上限回数以内かどうか
    """
    author = str(author).split('#')[0]  #そのまま使うとauthorの末尾に「#xxx」が付いてしまうため取り除く

    if not os.path.exists(f'{USER_FILE_PATH}/{author}.csv'):
        with open(f'{USER_FILE_PATH}/{author}.csv', 'w', encoding='utf-8', newline='') as output_stream:
            writer = csv.writer(output_stream)
            header = [
                'user_id',
                'date',
                'use_times'
            ]
            writer.writerow(header)
    
    current_date = datetime.date.today().strftime('%Y-%m-%d')   #date型のままだとqueryの条件で型が一致しないため、strに変換する
    user_log_data = pd.read_csv(f'{USER_FILE_PATH}/{author}.csv', encoding='utf-8', engine='python')
    current_user_data = user_log_data.query('user_id == @author and date == @current_date')

    ret_flg = None
    log_obj = LogObject()
    log_obj.user_id = author
    log_obj.date = current_date

    if len(current_user_data) == 0:
        # 今日初めての利用の場合
        ret_flg = True

    else:
        if current_user_data['use_times'].values[0] != DATE_USE_LIMIT:
            # 今日の今までの利用回数が指定回数以下の場合
            ret_flg = True
        else:
            # 今日の今までの利用回数が指定回数以上の場合
            ret_flg = False

    if ret_flg:
        user_log_data.to_csv(f'{USER_FILE_PATH}/{author}.csv', encoding='utf-8', index=False)

    return ret_flg

def update_use_times(author):
    """
    「./user_log/ユーザー名.csv」を読み込み、「date」、「use_times」列で一意のkeyとして
    利用回数をインクリメントして更新する

    Parameters
    ------------------------------
    author : str
        ユーザー名

    Returns
    ------------------------------
    Nothing
    """
    current_date = datetime.date.today().strftime('%Y-%m-%d')   #date型のままだとqueryの条件で型が一致しないため、strに変換する
    user_log_data = pd.read_csv(f'{USER_FILE_PATH}/{author}.csv', encoding='utf-8', engine='python')
    current_user_data = user_log_data.query('user_id == @author and date == @current_date')

    log_obj = LogObject()
    log_obj.user_id = author
    log_obj.date = current_date

    if len(current_user_data) == 0:
        # 今日初めての利用の場合は、行が存在しないので、利用回数1回の行を新規で作成し、DataFrameに追加してcsvを更新する
        log_obj.use_times = 1
        s = pd.Series([log_obj.user_id, log_obj.date, log_obj.use_times], index=user_log_data.columns)
        user_log_data = user_log_data.append(s, ignore_index=True)

    elif current_user_data['use_times'].values[0] != DATE_USE_LIMIT:
        # 今日の今までの利用回数が19回以下の場合は、該当ユーザーのDataFrameの利用回数を+1してcsvを更新する
        use_times = current_user_data['use_times'].values[0] + 1
        user_log_data.loc[(user_log_data['user_id'] == author) & (user_log_data['date'] == current_date),['use_times']] = use_times

    user_log_data.to_csv(f'{USER_FILE_PATH}/{author}.csv', encoding='utf-8', index=False)

def get_slot_key():
    """
    スロットの出目のkeyを返す
    """
    slot_config = config_dict[SLOT_CONFIG_KEY]
    random_size_config = slot_config[RANDOM_SIZE_KEY]
    probability_config = slot_config[PROBABILITY_KEY]

    decided_num = random.randint(random_size_config['from'], random_size_config['to'])

    # 数値に応じて当たり辞書のkeyを決定する
    key = None
    for bonus_kind, from_to in probability_config.items():
        if from_to['from'] <= decided_num <= from_to['to']:
            key = bonus_kind
    
    return key

def on_rush_flg(author):
    """
    RUSH中を表す「./rush_flg/ユーザー名.csv」を作成する
    """
    with open(f'{os.getcwd()}/rush_flg/{author}.csv', 'w', encoding='utf-8', newline='') as output_stream:
        pass

def update_slot_flg(path, row_contents):
    with open(path, 'w', encoding='utf-8', newline='') as output_stream:
        writer = csv.writer(output_stream)
        header = [
            'state'
        ]
        writer.writerow(header)
        writer.writerow(row_contents)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def check_reaction(target_msg, slot_obj, mention):
    """
    指定のメッセージにリアクションがついたらメッセージを送る
    """
    while True:
        target_reaction = await client.wait_for_reaction(message=target_msg)
        if target_reaction.user != target_msg.author:
            random_odds = slot_obj.get_random_odds()
            random_odds_arr = random_odds.split('×')
            coin_name = random_odds_arr[0]
            odds = random_odds_arr[1]

            await client.send_message(target_msg.channel, random_odds)
            await client.send_message(target_msg.channel, f'/tip {coin_name} {odds} {mention}')
            await client.remove_reaction(target_msg, target_reaction.reaction.emoji, target_reaction.user)
            break

####
##   Main flow
####

@client.event
async def on_message(message):
    # スロット実行
    if message.content.startswith(recieve_messages['start_slot']) and message.mentions[0].id == SLOT_BOT_ID:
        # 送り主がBotじゃない場合
        if client.user != message.author:
            author = str(message.author).split('#')[0]  #そのまま使うとauthorの末尾に「#xxx」が付いてしまうため取り除く
            if check_use_times(author):
                update_slot_flg(f'{DO_SLOT_FILE_PATH}/{author}.csv', ['ready'])

                pass

            # 今日の利用回数が20回以上の場合はその旨を通知し、tipを返却する
            else:
                await message.channel.send(send_messages['over_use_limit'])
                await message.channel.send(send_messages['return_tip_message'])
                time.sleep(UZURA_CMD_WAIT_SECOND)

                # tipを返却
                return_tip_command = f'{recieve_messages["start_slot"]} {message.author.mention}'
                await message.channel.send(return_tip_command)
                pass
    
    # うずらからの応答の場合
    elif message.author.id == UZURA_BOT_ID:
        # authorとmentionを取得する
        author = None
        mention = None
        for current_mention in message.mentions:
            if current_mention.id != SLOT_BOT_ID:
                author = current_mention.name
                mention = current_mention.mention
                break

        if os.path.exists(f'{DO_SLOT_FILE_PATH}/{author}.csv'):
            # ステータス取得
            do_slot_data = pd.read_csv(f'{DO_SLOT_FILE_PATH}/{author}.csv', encoding='utf-8', engine='python')
            status = do_slot_data['state'].values[0]
            # スロットの出目の応答か判定する
            # スロット実行時のチップコマンドの応答の場合
            if status == 'ready':
                # リンク切れの場合はその旨を通知し、「./do_slot_flg/ユーザー名.csv」を削除する
                if recieve_messages['not_linked_account'] in message.content:
                    os.remove(f'{DO_SLOT_FILE_PATH}/{author}.csv')
                    await message.channel.send(send_messages['not_linked_account'])
                    pass

                # 所持コインが不足している場合はその旨を通知し、「./do_slot_flg/ユーザー名.csv」を削除する
                elif (recieve_messages['short_coin'] in message.content)or('No balance'in message.content):
                    os.remove(f'{DO_SLOT_FILE_PATH}/{author}.csv')
                    await message.channel.send(send_messages['short_coin'])
                    pass

                # リンク切れでない、所持コイン不足していない場合はスロットを実行する
                else:
                    # 「./do_slot_flg/ユーザー名.csv」の「state」列を「execute」に更新する
                    update_slot_flg(f'{DO_SLOT_FILE_PATH}/{author}.csv', ['execute'])

                    # 今日の利用回数を更新する
                    update_use_times(author)

                    key = get_slot_key()
                    # 当たり情報の辞書を取得し、keyに応じた内容を取得する
                    slot_obj = SlotObject()
                    content = slot_obj.get_hit_dict(mention)[key]
                    await message.channel.send(key)
                    msg = await message.channel.send(content['picture'])
                    """if content['picture'] in slot_obj.special_production_pictures:
                        # 出目がリアクションボタン対象の場合、リアクションボタンを出現させ、リアクションボタンのクリックを待つ
                        await message.channel.send(send_messages['choice_stamp'])
                        for rb in slot_obj.rb_list:
                            await msg.add_reaction(rb)

                        client.loop.create_task(check_reaction(msg, slot_obj, mention))"""
                    
                    if content['picture'] in slot_obj.rush_pictures:
                        # 出目がRUSH対象の絵柄の場合特殊演出のフラグcsvを作成する
                        on_rush_flg(author)
                        await message.channel.send(send_messages['rush_message_1'])
                        await message.channel.send(send_messages['rush_message_2'])
                        await message.channel.send(send_messages['rush_message_3'])
                    else:
                        # リアクションボタン対象外、RUSH対象外の場合、チップを表示する(通常の当たり時)
                        if key != 'ハズレじゃ': # ハズレの場合、空文字を送るとエラーになる
                            for tip_command, tip in zip(content['tip_command'].split('\n'), content['tip'].split('\n')):
                                await message.channel.send(tip)
                                await message.channel.send(tip_command)
                                time.sleep(UZURA_CMD_WAIT_SECOND)

            # スロットの出目の応答の場合は何もしない 
            elif status == 'execute':
                pass

    # 「./rush_flg/ユーザー名.csv」が存在する場合のみ「！スタート」でRUSH演出を行う
    elif message.content == recieve_messages['start_rush']:
        author = str(message.author).split('#')[0] # そのまま使うとauthorの末尾に「#xxx」が付いてしまうため取り除く
        RUSH_FLG_PATH = f'{os.getcwd()}/rush_flg/{author}.csv'
        if os.path.exists(RUSH_FLG_PATH):
            rush_config = config_dict[RUSH_CONFIG_KEY]
            random_size_config = rush_config[RANDOM_SIZE_KEY]
            rush_times = random.randint(random_size_config['from'],random_size_config['to'])
            rush_tips = rush_config[RUSH_TIP_KEY]
            rush_picture_rand_size = rush_config[RUSH_PICTURE_RANDOM_KEY]
            rush_pictures = rush_config[RUSH_PICTURE_KEY]

            summary_count = defaultdict(int)
            for current_times in range(1, rush_times + 1):
                tip = None
                key_probability = random.randint(rush_picture_rand_size['from'], rush_picture_rand_size['to'])
                for tip_key, from_to in rush_pictures.items():
                    if from_to['from'] <= key_probability <= from_to['to']:
                        tip = rush_tips[tip_key]
                        break

                #tip = rush_tips[random.randint(1,len(rush_tips))]
                coin_name = tip.split('×')[0]
                odds = tip.split('×')[1]
                await message.channel.send(f'{coin_name}×{odds}')
                summary_count[coin_name] += int(odds)
                time.sleep(1)

            summary_count_str = '終了しました。\n'
            summary_count_str += f' everyone +{summary_count["everyone"]}, everyloto +{summary_count["everyloto"]}, 456coin +{summary_count["456coin"]}, 29coin +{summary_count["29coin"]} 獲得\n'
            await message.channel.send(summary_count_str)
            tip_commands = [
                f'/tip everyone {summary_count["everyone"]} {message.author.mention}\n',
                f'/tip everyloto {summary_count["everyloto"]} {message.author.mention}\n',
                f'/tip 456coin {summary_count["456coin"]} {message.author.mention}\n',
                f'/tip 29coin {summary_count["29coin"]} {message.author.mention}\n'

            ]
            for tip_command in tip_commands:    
                await message.channel.send(tip_command)
                time.sleep(UZURA_CMD_WAIT_SECOND)

            # rush_flgのファイルを消す
            os.remove(RUSH_FLG_PATH)
        else:
            await message.channel.send(send_messages['not_rush_time'])
            # await client.send_message(message.channel, send_messages['not_rush_time'])

client.run(token)
