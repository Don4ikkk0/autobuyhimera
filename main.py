import asyncio
from telethon import TelegramClient
from telethon.tl import functions, types as t
from telethon.errors.rpcerrorlist import AuthKeyUnregisteredError, FloodWaitError
from telethon.errors import RPCError
from datetime import datetime
import pytz
import logging

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram API конфіг
api_id = 19668803
api_hash = '0acbcddb213c3f9c7b5cfdbfaade8fd4'
phone_number = '+380997190277'
session_name = 'user_sessionasd53'

hide_sender_name = True

channel_chat_ids = [
    -1002754320604,
    -1002675115074,
    -1002772373690,
    -1002825865236,
    -1002750117409
]

current_channel_index = 0

# Ігноровані подарунки
ignored_gift_ids = {
    5170250947678437525, 5170314324215857265, 5170564780938756245, 5168103777563050263,
    5170144170496491616, 5168043875654172773, 5170233102089322756, 
    5170690322832818290, 5170521118301225164, 6028601630662853006, 5999277561060787166,
    5999298447486747746, 5999116401002939514, 5902339509239940491, 5898012527257715797,
    5900177027566142759, 5897607679345427347, 5830323722413671504, 5832325860073407546,
    5830340739074097859, 5807641025165919973, 5773668482394620318, 5773725897517433693,
    5773791997064119815, 6042113507581755979, 6005797617768858105, 6005659564635063386,
    6005880141270483700, 6006064678835323371, 6005564615793050414, 6003456431095808759,
    5998981470310368313, 5960747083030856414, 5963238670868677492, 5933793770951673155,
    5933937398953018107, 5933770397739647689, 5933543975653737112, 5935877878062253519,
    5933737850477478635, 5913351908466098791, 5895518353849582541, 5895328365971244193,
    5897593557492957738, 5895544372761461960, 5897581235231785485, 5895603153683874485,
    5872744075014177223, 5870972044522291836, 5871002671934079382, 5870661333703197240,
    5870862540036113469, 5870720080265871962, 5868595669182186720, 5868348541058942091,
    5868220813026526561, 5868503709637411929, 5868561433997870501, 5870784783948186838,
    5868659926187901653, 5870947077877400011, 5868455043362980631, 6028426950047957932,
    6028283532500009446, 6023917088358269866, 6023679164349940429, 6023752243218481939,
    6003373314888696650, 6003767644426076664, 6001538689543439169, 6003643167683903930,
    6003735372041814769, 6001473264306619020, 5983484377902875708, 5983259145522906006,
    5983471780763796287, 5981132629905245483, 5980789805615678057, 5981026247860290310,
    5933590374185435592, 5936017773737018241, 5935936766358847989, 5936043693864651359,
    5936085638515261992, 5933531623327795414, 5933629604416717361, 5933671725160989227,
    5936013938331222567, 5913442287462908725, 5915502858152706668, 5915733223018594841,
    5915521180483191380, 5915550639663874519, 5913517067138499193, 5879737836550226478,
    5882125812596999035, 5882252952218894938, 5859442703032386168, 5857140566201991735,
    5856973938650776169, 5846226946928673709, 5846192273657692751, 5845776576658015084,
    5825895989088617224, 5825801628657124140, 5825480571261813595, 5843762284240831056,
    5841689550203650524, 5841632504448025405, 5841391256135008713, 5839038009193792264,
    5841336413697606412, 5837063436634161765, 5836780359634649414, 5837059369300132790,
    5821384757304362229, 5821205665758053411, 5821261908354794038, 5170594532177215681,
    5167939598143193218, 5783075783622787539, 5782988952268964995, 5782984811920491178,
    6012607142387778152, 6014675319464657779, 6012435906336654262,
    6014591077976114307
}

# Створюємо новий цикл подій
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# Створюємо клієнт Telethon
telethon_client = TelegramClient(session_name, api_id, api_hash, loop=loop)

def get_timestamp():
    kyiv_tz = pytz.timezone('Europe/Kyiv')
    return datetime.now(kyiv_tz).strftime('%Y-%m-%d %H:%M:%S')

def log_print(message: str):
    timestamp = get_timestamp()
    logger.info(f"[{timestamp}] {message}")

async def get_gift_details(gift):
    name = 'Нету названия'
    if hasattr(gift, 'sticker') and gift.sticker and hasattr(gift.sticker, 'alt'):
        name = gift.sticker.alt or 'Без названия'
    elif hasattr(gift, 'description'):
        name = gift.description

    return {
        'id': gift.id,
        'name': name,
        'stars': gift.stars,
        'convert_stars': gift.convert_stars,
        'limited': gift.limited,
        'sold_out': gift.sold_out,
        'availability_total': getattr(gift, 'availability_total', 'Неограничено'),
        'availability_remains': getattr(gift, 'availability_remains', 'Неограничено'),
    }

async def get_all_gifts():
    try:
        result = await telethon_client(functions.payments.GetStarGiftsRequest(hash=0))
        gifts = result.gifts
        logger.info(f"Отримано {len(gifts)} подарунків")
        return [await get_gift_details(gift) for gift in gifts]
    except AuthKeyUnregisteredError:
        log_print("[!] Помилка: API ключ не зареєстровано в системі. Перевірте api_id та api_hash.")
        return []
    except FloodWaitError as e:
        wait_time = e.seconds
        log_print(f"[!] Flood wait: Потрібно зачекати {wait_time} секунд.")
        await asyncio.sleep(wait_time)
        return []
    except Exception as e:
        log_print(f"[!] Помилка отримання подарунків: {e}")
        return []

async def tl_gifts():
    try:
        logger.info("🔄 Отримання списку подарунків...")
        resp = await telethon_client(functions.payments.GetStarGiftsRequest(hash=0))
        gifts = resp.gifts
        filtered = [g for g in gifts if g.id not in ignored_gift_ids]
        logger.info(f"✅ Отримано {len(gifts)} подарунків, доступно {len(filtered)} (відфільтровано {len(gifts) - len(filtered)})")
        return filtered
    except Exception as e:
        logger.error(f"❌ Помилка при отриманні подарунків: {e}")
        return []

async def send_single_gift(gid: int, peer: t.InputPeerChannel, comment: str = "", index: int = 0, total: int = 0):
    logger.info(f"🎁 Відправка {index}/{total} подарунка (id={gid})")
    try:
        inv = t.InputInvoiceStarGift(
            peer=peer,
            gift_id=gid,
            message=(t.TextWithEntities(text=comment, entities=[]) if comment else None),
            hide_name=hide_sender_name
        )
        form = await telethon_client(functions.payments.GetPaymentFormRequest(invoice=inv))
        await telethon_client(functions.payments.SendStarsFormRequest(
            form_id=form.form_id,
            invoice=inv
        ))
        logger.info(f"✅ Відправлено {index}/{total} подарунків id={gid}")
    except RPCError as e:
        if "BALANCE_TOO_LOW" in str(e):
            logger.error(f"[ERROR] Недостатньо зірок для подарунка ID: {gid}.")
            raise
        elif "STARGIFT_USAGE_LIMITED" in str(e):
            logger.warning(f"⚠️ Обмеження на використання подарунка ID: {gid}. Спробуй пізніше.")
            raise
        elif "CHAT_WRITE_FORBIDDEN" in str(e) or "PEER_ID_INVALID" in str(e):
            logger.error(f"[ERROR] Немає прав для відправки подарунка в канал ID: {peer.channel_id}.")
            raise
        else:
            logger.error(f"[!] RPCError при покупці: {e}")
            raise
    except Exception as e:
        logger.error(f"❌ Інша помилка при відправці подарунка ID: {gid}: {e}")
        raise

async def tl_send(gid: int, qty: int, peer: t.InputPeerChannel, comment: str = ""):
    logger.info(f"🚀 Початок відправки подарунка id={gid}, кількість={qty}")
    gifts_list = await tl_gifts()
    gift = next((g for g in gifts_list if g.id == gid), None)
    if not gift:
        logger.error(f"❌ Подарунок id={gid} не знайдено в списку, відправка неможлива")
        return

    tasks = []
    for i in range(qty):
        # Створюємо задачу для відправки одного подарунка
        task = asyncio.create_task(send_single_gift(gid, peer, comment, i + 1, qty))
        tasks.append(task)
        # Затримка 0.1 секунди перед створенням наступної задачі
        await asyncio.sleep(0.05)

    # Чекаємо завершення всіх задач
    for task in tasks:
        try:
            await task
        except Exception:
            # Якщо одна з задач завершилася з помилкою, продовжуємо логування, але не перериваємо інші
            pass

    logger.info(f"🏁 Відправка {qty} подарунків id={gid} завершена")

async def monitor_gifts():
    global current_channel_index
    known_gift_ids = set()

    while True:
        try:
            gifts = await get_all_gifts()
            gifts = sorted(gifts, key=lambda x: x['stars'], reverse=True)
            new_gifts = [gift for gift in gifts if
                         gift['id'] not in known_gift_ids and gift['id'] not in ignored_gift_ids]

            if new_gifts:
                log_print(f"[INFO] Знайдено {len(new_gifts)} нових подарунків.")
                for gift in new_gifts:
                    known_gift_ids.add(gift['id'])
                    current_channel_id = channel_chat_ids[current_channel_index]
                    peer = await telethon_client.get_input_entity(current_channel_id)

                    # Визначаємо кількість покупок на основі ціни та доступності
                    purchase_count = 0
                    if 7000 <= gift['stars'] <= 10000:
                        if isinstance(gift['availability_total'], int) and gift['availability_total'] >= 10001:
                            purchase_count = 1
                        elif isinstance(gift['availability_total'], int) and 5001 <= gift['availability_total'] <= 10000:
                            purchase_count = 2
                        elif isinstance(gift['availability_total'], int) and 0 <= gift['availability_total'] <= 5000:
                            purchase_count = 5
                    elif 4000 <= gift['stars'] <= 6999:
                        if isinstance(gift['availability_total'], int) and gift['availability_total'] >= 10001:
                            purchase_count = 2
                        elif isinstance(gift['availability_total'], int) and 5001 <= gift['availability_total'] <= 10000:
                            purchase_count = 3
                        elif isinstance(gift['availability_total'], int) and 0 <= gift['availability_total'] <= 5000:
                            purchase_count = 5
                    elif 1001 <= gift['stars'] <= 3999:
                        if isinstance(gift['availability_total'], int) and gift['availability_total'] >= 15001:
                            purchase_count = 2
                        elif isinstance(gift['availability_total'], int) and 5001 <= gift['availability_total'] <= 15000:
                            purchase_count = 3
                        elif isinstance(gift['availability_total'], int) and 0 <= gift['availability_total'] <= 5000:
                            purchase_count = 5
                    elif gift['stars'] in [10, 15, 25, 50, 75, 100, 150, 200, 250, 300, 350, 400, 500, 1000]:
                        purchase_count = {
                            10: 1000, 15: 700, 25: 500, 50: 200, 75: 100, 100: 100, 150: 100, 200: 70,
                            250: 60, 300: 25, 350: 25, 400: 20, 500: 20, 1000: 10
                        }.get(gift['stars'], 0)

                    timestamp = get_timestamp()
                    message = (
                        f"\n"
                        f"🎁 Новий подарунок!\n"
                        f"🆔 ID: {gift['id']}\n"
                        f"💫 Ціна: {gift['stars']} Stars\n"
                        f"⏳ Лімітка?: {'так' if gift['limited'] else 'ні'}\n"
                        f"📊 Всього в наявності: {gift['availability_total']}\n"
                        f"📈 Залишилось: {gift['availability_remains']}\n"
                        f"❌ Розпродано?: {'так' if gift['sold_out'] else 'ні'}\n"
                        f"💸 Планую купити: {purchase_count} шт. в канал {current_channel_id}\n"
                        f"💦 Створив - @DKdon4ik\n"
                    )

                    log_print(message)

                    if purchase_count == 0:
                        log_print(
                            f"[INFO] Подарунок ID: {gift['id']} ({gift['stars']} зірок) не відповідає фільтрам (ціна або саплай). Пропускаємо.")
                    else:
                        await tl_send(gift['id'], purchase_count, peer, comment="🎁")

                    current_channel_index = (current_channel_index + 1) % len(channel_chat_ids)

        except Exception as e:
            log_print(f"[!] Помилка в моніторингу подарунків: {e}")

        await asyncio.sleep(1.5)

async def main():
    try:
        log_print("Спроба авторизації...")
        await telethon_client.start(
            phone=phone_number,
            password=lambda: input("Введіть пароль двоетапної верифікації: ")  # Запит пароля
        )
        log_print("✅ Telethon працює.")
        me = await telethon_client.get_me()
        log_print(f"Ви увійшли як {me.first_name} ({me.phone})")
        await monitor_gifts()
    except FloodWaitError as e:
        log_print(f"[!] Flood wait: Потрібно зачекати {e.seconds} секунд.")
        await asyncio.sleep(e.seconds)
        await main()  # Повторна спроба після очікування
    except AuthKeyUnregisteredError:
        log_print("[!] Помилка: API ключ не зареєстровано. Перевірте api_id та api_hash.")
    except Exception as e:
        log_print(f"[!] Помилка в main: {e}")
        raise  # Для детального стеку помилки
    finally:
        if telethon_client.is_connected():
            await telethon_client.disconnect()
            log_print("🛑 Telethon відключено.")

if __name__ == '__main__':
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        log_print("Програму зупинено користувачем.")
    finally:
        loop.close()

        log_print("Цикл подій закрито.")




