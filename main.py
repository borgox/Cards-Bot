import disnake
from disnake.ext import commands, tasks
import aiosqlite
import random
import json
1
intents = disnake.Intents.all()
bot = commands.InteractionBot(intents=intents)

RARITIES = {
    "Impossible": 0.02,
    "Leggendario": 0.10,
    "Ultra raro": 0.20,
    "Super raro": 0.40,
    "Raro": 0.55,
    "comune": 0.80,
}

async def get_channel_id():
    async with aiosqlite.connect('cards.db') as db:
        cursor = await db.execute('SELECT channel_id FROM cards')
        channel_id = await cursor.fetchone()

    return channel_id[0] if channel_id else None

async def get_card_by_name(card_name):
    async with aiosqlite.connect('cards.db') as db:
        cursor = await db.execute('SELECT name, photo, rarity FROM cards WHERE name = ?', (card_name,))
        card = await cursor.fetchone()
        return card

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    async with aiosqlite.connect("cards.db") as db:
        await setup_database()
        await setup_card_collection_table()
    spawn_cards.start()

async def setup_database():
    async with aiosqlite.connect('cards.db') as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS cards (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT,
                            photo TEXT,
                            rarity TEXT,
                            channel_id INTEGER)''')
        await db.commit()

@bot.slash_command()
async def setup(inter):
    await setup_database()

    async with aiosqlite.connect('cards.db') as db:
        await db.execute('INSERT INTO cards (channel_id) VALUES (?)', (inter.channel.id,))
        await db.commit()

    await inter.send(f'This channel has been set up to receive cards!')
@bot.slash_command()
async def vedirarita(inter):
    await  inter.send(f"Le rarità sono: {list(RARITIES.keys())}")
@bot.slash_command()
@commands.has_permissions(manage_guild=True)
async def aggiungi(inter, nomecarta: str, foto: disnake.Attachment, rarita: str = commands.Param(choices=list(RARITIES.keys()))):
    #rarita = rarita.lower() # se la rarita non è un param
    if foto.filename.split(".")[1] not in ["png", "jpg"]:
        await inter.send("il file deve essere .png o .jpg")
        return
    if rarita not in list(RARITIES.keys()):
        print(rarita, RARITIES.keys(), RARITIES)
        await inter.send(f'Invalid rarity. Available rarities: {", ".join(RARITIES)}')
        return
    if ' ' in nomecarta or "-" in nomecarta:
        await inter.send("Non puoi avere spazi o '-' nel nome della carta!", ephemeral=True)
        return
    async with aiosqlite.connect('cards.db') as db:
        await db.execute('INSERT INTO cards (name, photo, rarity, channel_id) VALUES (?, ?, ?, ?)',
                         (nomecarta, foto.url, rarita, inter.channel.id))
        await db.commit()

    await inter.send(f'Carta {nomecarta} aggiunta con successo!')

@bot.slash_command()
@commands.is_owner()
async def prendi(inter: disnake.AppCmdInter):
    await inter.response.defer()
    async with aiosqlite.connect('cards.db') as db:

        cursor = await db.execute('SELECT name, photo, rarity FROM cards WHERE channel_id = ? ORDER BY RANDOM() LIMIT 1',
                                  (inter.channel.id,))
        card = await cursor.fetchone()

    if not card:
        await inter.send('Non ci sono carte nel database.')
        return

    name, photo, rarity = card
    embed = disnake.Embed(title=name, description=f'Rarità: {rarity}')
    embed.set_image(url=photo)

    await inter.edit_original_response(embed=embed)

@bot.slash_command()
@commands.has_permissions(manage_guild=True)
async def elimina(inter, nomecarta: str):
    card = await get_card_by_name(nomecarta)
    if not card:
        await inter.send(f'La carta "{nomecarta}" non è presente nel database.')
        return

    async with aiosqlite.connect('cards.db') as db:
        await db.execute('DELETE FROM cards WHERE name = ?', (nomecarta,))
        await db.commit()

    await inter.send(f'Carta "{nomecarta}" eliminata dal database.')
@bot.listen("on_guild_join")
async def ioesco(guild: disnake.Guild):
    if guild.id not in [1124444466502185020]:
        await guild.leave()
@tasks.loop(minutes=45.0)
async def spawn_cards():
    print("spawn")
    await setup_database()
    await setup_card_collection_table()
    channel_id = await get_channel_id()
    if not channel_id:
        print('Server non setuppato.  F')
        return


    channel = bot.get_channel(channel_id)
    
    async with aiosqlite.connect('cards.db') as db:
        cursor = await db.execute('SELECT rarity FROM cards WHERE channel_id = ? ORDER BY RANDOM() LIMIT 1',
                                  (channel_id,))
        selected_rarity = await cursor.fetchone()

        if not selected_rarity or selected_rarity[0] not in RARITIES:
            return

        selected_rarity = selected_rarity[0]
        rarity_probability = RARITIES[selected_rarity]
        randsss = random.random()
        print(randsss)
        # Check if the card should be spawned based on probability
        if randsss < rarity_probability:
            cursor = await db.execute('SELECT name, photo FROM cards WHERE rarity = ? AND channel_id = ? ORDER BY RANDOM() LIMIT 1',
                                      (selected_rarity, channel_id))
            card = await cursor.fetchone()

            if card:
                name, photo = card
                embed = disnake.Embed(title=name, description=f'Rarità: {selected_rarity}')
                embed.set_image(url=photo)
                print(photo)
                photo : str = photo.split("attachments/")[1]
                await channel.send(embed=embed, components=disnake.ui.Button(style=disnake.enums.ButtonStyle.blurple, label="Claim", disabled=False, custom_id=f"📃-{name}-{photo}"))
async def decode_button_id(x:str):
 if x.split("-") :
    x = x.split("-")
    baseid = x[0]
    cardname = x[1]
    cardurl = "https://cdn.discordapp.com/attachments/" + x[2]
    return [baseid, cardname, cardurl]
async def setup_card_collection_table():
    async with aiosqlite.connect('cards.db') as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS user_cards (
                            user_id INTEGER,
                            card_name TEXT,
                            card_url TEXT)''')
        await db.commit()
@bot.listen()
async def on_button_click(inter: disnake.MessageInteraction):
    if inter.component.custom_id.startswith("📃-"):
        _, card_name, card_url = await decode_button_id(inter.component.custom_id)

        user_id = inter.author.id

        # Add the claimed card's details to the user's card collection
        async with aiosqlite.connect('cards.db') as db:
            await db.execute('INSERT INTO user_cards (user_id, card_name, card_url) VALUES (?, ?, ?)',
                             (user_id, card_name, card_url))
            await db.commit()

        # Respond to the button click
        original_msg = inter.message

        # Check if the original message is still available before editing
        try:
            await original_msg.edit(content="Claimed by {}".format(inter.author.mention),
                                    components=disnake.ui.Button(style=inter.component.style,
                                                                 label=inter.component.label,
                                                                 disabled=True,
                                                                 custom_id=inter.component.custom_id),
                                    embed=original_msg.embeds[0])
            await inter.send("Claimed! ", ephemeral=True)
        except disnake.errors.InteractionNotResponded:
            # If the original response hasn't been sent yet, send it instead of editing
            await inter.send(content="Claimed by {}".format(inter.author.mention),
                             components=disnake.ui.Button(style=inter.component.style,
                                                          label=inter.component.label,
                                                          disabled=True,
                                                          custom_id=inter.component.custom_id),
                             embed=original_msg.embeds[0])
            await inter.send("Claimed! ", ephemeral=True)
async def get_user_cards(user_id):
    async with aiosqlite.connect('cards.db') as db:
        cursor = await db.execute('SELECT card_name, card_url FROM user_cards WHERE user_id = ?', (user_id,))
        cards = await cursor.fetchall()

    return cards
@bot.slash_command()
async def mycards(inter, user: disnake.Member = commands.Param(default=None)):
    if user is None:
        user_id = inter.author.id
    else:
        user_id = user.id

    cards = await get_user_cards(user_id)

    if not cards:
        await inter.send("Non hai carte")
        return

    card_list = []
    for i, (card_name, card_url) in enumerate(cards, start=1):
        card_list.append(f"**Carta #{i}**\nNome: {card_name}\nURL: {card_url}\n")

    if len(card_list) == 0:
        await inter.send("Le mie carte")
        return

    # Create an embed with all the cards and their images
    embed = disnake.Embed(title="Le Mie carte", description=f"Total Cards: {len(card_list)}\n")
    for i, card_info in enumerate(cards, start=1):
        card_name, card_url = card_info
        embed.add_field(name=f"Card #{i}", value=f"Name: {card_name}\nURL: {card_url}\n", inline=False)

    await inter.send(embed=embed)

async def delete_user_cards(user_id):
    async with aiosqlite.connect('cards.db') as db:
        await db.execute('DELETE FROM user_cards WHERE user_id = ?', (user_id,))
        await db.commit()
@bot.slash_command()
@commands.has_permissions(manage_roles=True, manage_nicknames=True, manage_emojis=True, manage_messages=True)
async def reset_my_cards(inter, user:disnake.Member=commands.Param(default="self")):
    if user == "self":
        
        user_id = inter.author.id
    else:
        user_id = user.id
    await delete_user_cards(user_id)
    await inter.send("Tutte le tue carte sono state tolte")
@bot.slash_command()
async def show_all_cards(inter):
    async with aiosqlite.connect('cards.db') as db:
        cursor = await db.execute('SELECT name, photo, rarity FROM cards')
        all_cards = await cursor.fetchall()

    if not all_cards:
        await inter.send('No cards found in the database.')
        return

    # Create an embed to display the cards
    embed = disnake.Embed(title='All Available Cards', color=disnake.Color.blurple())

    for card in all_cards:
        name, photo, rarity = card
        embed.add_field(name=f'Card: {name}', value=f'Rarity: {rarity}', inline=False)
        embed.set_image(url=photo)

    await inter.send(embed=embed)
bot.run('token_here')
