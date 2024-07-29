import time
from logging import exception
import asyncio

import aiogram
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter
from aiogram.types import FSInputFile

from utils.scapi import StalcraftAPI
from config import config
from db.models.emissions import Emission
from datetime import datetime, timezone, timedelta
import random
import inflect
import pymorphy3

groups = config['groups']
emission_end_time = 225


def pluralize_noun_en(number, word):
    p = inflect.engine()
    pluralized_word = p.plural(word, number)
    return f"{number} {pluralized_word}"


def pluralize_noun_ru(number, word):
    morph = pymorphy3.MorphAnalyzer()
    parsed_word = morph.parse(word)[0]
    pluralized_word = parsed_word.make_agree_with_number(number).word
    return f"{number} {pluralized_word}"


def time_converter_ru(times):
    if times >= 0:
        if times < 60:
            time_mes = f'{pluralize_noun_ru(times, "секунда")} назад'
        elif times < 3600:
            time_mes = f'{pluralize_noun_ru(times // 60, "минута")} назад'
        else:
            time_mes = f'{pluralize_noun_ru(times // 3600, "час")} назад'
    else:
        times = abs(times)
        if times < 60:
            time_mes = f'через {pluralize_noun_ru(times, "секунда")}'
        elif times < 3600:
            time_mes = f'через {pluralize_noun_ru(times // 60, "минута")}'
        else:
            time_mes = f'через {pluralize_noun_ru(times // 3600, "час")}'
    return time_mes


def time_converter_en(times):
    if times >= 0:
        if times < 60:
            time_mes = f'{pluralize_noun_en(times, "second")} ago'
        elif times < 3600:
            time_mes = f'{pluralize_noun_en(times // 60, "minute")} ago'
        else:
            time_mes = f'{pluralize_noun_en(times // 3600, "hour")} ago'
    else:
        times = abs(times)
        if times < 60:
            time_mes = f'in {pluralize_noun_en(times, "second")}'
        elif times < 3600:
            time_mes = f'in {pluralize_noun_en(times // 60, "minute")}'
        else:
            time_mes = f'in {pluralize_noun_en(times // 3600, "hour")}'
    return time_mes

#
def make_message(region, group, emission_time, online):
    emission_time = int(emission_time)
    damage_phase = 120
    safaty_phase = emission_end_time
    actual_time = int(time.time())
    passed_time = actual_time - emission_time
    
    damage_time = passed_time - damage_phase
    safaty_time = passed_time - safaty_phase
    
    if region == 'RU':
        online = online if online > 0 else 'не установлен'
        if passed_time < emission_end_time:
            message = f'''
<b>💥 Выброс начался!</b>

<b>Время начала: </b>{time_converter_ru(passed_time)}
<b>Урон {"начнётся" if damage_time < 0 else 'начался'}: </b>{time_converter_ru(damage_time)}
<b>Безопасно будет: </b>{time_converter_ru(safaty_time)}
<b>Актуальный онлайн: </b>{online}

t.me/{group[1:]}
            '''
        else:
            spawn_boost_mes = f'<b>Спавн артефактов повышен</b>\n'
            message = f'''
<b>💥 Выброс!</b>

<b>Закончился: </b>{time_converter_ru(passed_time - emission_end_time)}
<b>Актуальный онлайн: </b>{online}
{spawn_boost_mes if (passed_time-emission_end_time)<60*30 else ''}
t.me/{group[1:]}
'''
    
    
    
    else:
        online = online if online > 0 else 'not received'
        if passed_time < emission_end_time:
            message = f'''
<b>💥 An Eruption occurred!</b>

<b>Start time: </b>{time_converter_en(passed_time)}
<b>Damage begins: </b>{time_converter_en(damage_time)}
<b>Will be safe: </b>{time_converter_en(safaty_time)}
<b>Current online: </b>{online}

t.me/{group[1:]}
'''
        else:
            spawn_boost_mes = f'<b>Artifacts Spawn Boosted</b>\n'
            message = f'''
<b>💥 Eruption!</b>

<b>End time: </b>{time_converter_en(passed_time - emission_end_time)}
<b>Current online: </b>{online}
{spawn_boost_mes if (passed_time-emission_end_time)<60*30 else ''}
t.me/{group[1:]}
'''
    return message


async def start_loop(bot: aiogram.Bot):
    sc = StalcraftAPI(
        client_id=config['stalcraft_api']['client_id'],
        client_secret=config['stalcraft_api']['client_secret'],
        debug=config['bot']['debug'],
        stalcraft_status_key=config['stalcraft_api']['stalcraft_status_key']
    )
    await sc.run()
    while True:
        try:
            for region in list(groups.keys()):
                emiss = await sc.get_emission(region)
                if 'currentStart' in emiss:
                    actual_emiss = await Emission.find_one(Emission.emission_time == emiss.get('currentStart'))
                    dt = datetime.strptime(
                        emiss.get('currentStart'),
                        "%Y-%m-%dT%H:%M:%SZ" if not config['bot']['debug'] else '%Y-%m-%dT%H:%M:%S.%fZ'
                    )
                    dt = dt.replace(tzinfo=timezone.utc)
                    emiss_timestamp = int(dt.timestamp())
                    # emiss_timestamp = int(datetime.now(timezone.utc).timestamp())
                    
                    if not actual_emiss:
                        print(f'Emission start, region: {region}, time: {emiss.get("currentStart")} ')
                        image = f'assets/images/emm{random.randint(1, 5)}.png'
                        photo = FSInputFile(image)
                        try:
                            msg = await bot.send_photo(
                                chat_id=groups.get(region),
                                photo=photo,
                                caption=make_message(region, groups.get(region), emiss_timestamp, await sc.get_stalcraft_online())
                            )
                        except TelegramRetryAfter as e:
                            print('Ошибка, попробуйте позже')
                        except Exception as e:
                            print(str(e))
                        last_emis = await Emission.find(
                            Emission.region == region
                        ).sort(-Emission.emission_time).first_or_none()
                        
                        if last_emis:
                            emission_timestamp = last_emis.emission_timestamp
                            dt_utc = datetime.utcfromtimestamp(emission_timestamp)
                            msk_offset = timedelta(hours=3)
                            dt_msk = dt_utc + msk_offset
                            formatted_time_utc = dt_utc.strftime("%H:%M")
                            formatted_time_msk = dt_msk.strftime("%H:%M")
                            online_text = last_emis.last_online
                            
                            if region == 'RU':
                                msg_text = f'''
<b>💥 Выброс!</b>

<b>Время начала: </b>{formatted_time_msk} (МСК)
<b>Игроков онлайн: </b>{online_text if online_text>0 else 'не установлен'}

t.me/{groups.get(region)[1:]}
'''
                            else:
                                msg_text = f'''
<b>💥 Eruption!</b>

<b>Start time: </b>{formatted_time_utc} (UTC)
<b>Players online: </b>{online_text if online_text>0 else 'not received'}

t.me/{groups.get(region)[1:]}
'''
                            try:
                                await bot.edit_message_caption(caption=msg_text, chat_id=last_emis.group,
                                                               message_id=last_emis.message_id)
                            except TelegramBadRequest as e:
                                pass
                            except TelegramRetryAfter as e:
                                print('Ошибка, попробуйте позже '+ e)
                            except Exception as e:
                                print('Критическая ошибка: '+str(e))
                                
                        online = await sc.get_stalcraft_online()

                        emi_db = Emission(
                            region=region,
                            emission_time=emiss.get('currentStart'),
                            emission_timestamp=emiss_timestamp,
                            message_id=msg.message_id,
                            group=groups.get(region),
                            last_online=online
                        )
                        await emi_db.insert()
                        continue
                
                last_emis = await Emission.find(
                    Emission.region == region
                ).sort(-Emission.emission_time).first_or_none()
                if last_emis:
                    msg_text = make_message(region, groups.get(region), last_emis.emission_timestamp, await sc.get_stalcraft_online())
                    try:
                        await bot.edit_message_caption(caption=msg_text, chat_id=last_emis.group,
                                                       message_id=last_emis.message_id)
                    except TelegramBadRequest as e:
                        # print(e)
                        pass
                    except Exception as e:
                        print(e)
            await asyncio.sleep(config['bot']['update_time_sec'])
        except Exception as e:
            exception(e)
