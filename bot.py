import discord
from discord.ext import commands
import requests
from discord import Colour
import random
import json
from math import ceil
from bs4 import BeautifulSoup

client = commands.Bot(command_prefix = '~')

@client.event
async def on_ready():
    print("Bot is ready")

with open("config.json") as file:
    configuration = json.load(file)
    credentials = configuration['credentials']

    username = credentials['username']
    password = credentials['password']

    TOKEN = configuration['token']


def fetch_memes():
    data = requests.get('https://api.imgflip.com/get_memes').json()['data']['memes']
    #images = [{'name':image['name'],'url':image['url'],'id':image['id']} for image in data]
    return data

def generate_meme(meme_id, caption_text):
    URL = 'https://api.imgflip.com/caption_image'

    params = {
        'username':username,
        'password':password,
        'template_id':meme_id,
    }

    for i in range(len(caption_text)):
        params["boxes[{}][text]".format(i)]=caption_text[i]

    response = requests.request('POST',URL,params=params).json()

    if response['success'] == True:
        return response['data']
    else:
        return None

discord_colours = [ Colour.blue,
                    Colour.blurple,
                    Colour.gold,
                    Colour.green,
                    Colour.greyple,
                    Colour.light_grey,
                    Colour.magenta,
                    Colour.orange,
                    Colour.purple,
                    Colour.red,
                    Colour.teal]
prev_colour = random.choice(discord_colours)

def random_colour():
    global prev_colour
    while True:
        colour = random.choice(discord_colours)
        if colour!=prev_colour:
            prev_colour = colour
            return colour

@client.command()
async def templates(ctx):
    memes = fetch_memes()
    memes_len = len(memes)

    pages = []
    meme_list = ""

    for i in range(memes_len):
        meme_list+=(str(i+1)+"-"+memes[i]['name']+"\n")
        if (i+1)%25==0 or (i+1)==memes_len:
            page_colour = random_colour()
            page = discord.Embed(title="List of available templates", colour = page_colour())
            page.add_field(name="Page {}/{}".format((i+1)//25, ceil(memes_len/25)), value=meme_list)
            pages.append(page)

            meme_list = ""

    pages_len = len(pages)

    message = await ctx.send(embed = pages[0])

    number_emojis = ['1️⃣','2️⃣','3️⃣','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣','🔟']
    valid_numbers = []
    await message.add_reaction('◀')
    await message.add_reaction('▶')
    for i in range(pages_len):
        await message.add_reaction(number_emojis[i])
        valid_numbers.append(number_emojis[i])

    def check(reaction, user):
        return user == ctx.author

    i = 0
    reaction = None

    while True:
        if str(reaction) == '◀':
            if i > 0:
                i -= 1
                await message.edit(embed = pages[i])
        elif str(reaction) == '▶':
            if i < pages_len-1:
                i += 1
                await message.edit(embed = pages[i])
        elif str(reaction) in valid_numbers:
            i = valid_numbers.index(str(reaction))
            await message.edit(embed=pages[i])

        try:
            reaction, user = await client.wait_for('reaction_add', timeout = 60.0, check = check)
            await message.remove_reaction(reaction, user)
        except:
            break

    await message.clear_reactions()

@client.command()
async def memeinfo(ctx, meme_id:int):
    colour = random_colour()
    if meme_id>100 or meme_id<0:
        embed = discord.Embed(title="Invalid Meme ID", 
            description="Please select a valid template\nUse `~templates` to get the list of templates\nUse `~memehelp` to know more",
            colour=colour())
        await ctx.send(embed=embed)
        return None

    memes = fetch_memes()
    meme = memes[meme_id-1]

    caption_text = []
    for i in range(meme['box_count']):
        caption_text.append("text{}".format(i))

    
    embed = discord.Embed(title=meme['name'], colour=colour())

    usage_text = "`~makememe {}".format(meme_id)
    for i in caption_text:
        usage_text+=" \"{}\"".format(i)
    usage_text+="`"
    embed.add_field(name='Usage', value=usage_text, inline=False)

    embed.add_field(name="Example",
        value="[Click here for sample memes](https://imgflip.com/meme/{})\nUse `~examplememe {}` to display the top example".format(meme['id'],meme_id),
        inline=False)

    new_meme = generate_meme(meme['id'], caption_text)
    embed.set_image(url=new_meme['url'])
    await ctx.send( embed=embed)

def add_to_fav(user, creator, meme, new_meme, caption_text):
    with open("favourite.json", "r") as file:
        data = json.load(file)
        if str(user.id) in data:
            data[str(user.id)].append({"creator":creator, "id":meme['id'], "name":meme['name'], "caption_text":caption_text, "url":new_meme["url"]})
        else:
            data[str(user.id)] = [{"creator":creator,"id":meme['id'], "name":meme['name'], "caption_text":caption_text, "url":new_meme["url"]}]
            
    with open("favourite.json", "w") as file:
        json.dump(data, file)

@client.command()
async def makememe(ctx, meme_id:int, *caption_text):
    colour = random_colour()
    if meme_id>100 or meme_id<0:
        embed = discord.Embed(title="Invalid Meme ID", 
            description="Please select a valid template\nUse `~templates` to get the list of templates\nUse `~memehelp` to know more",
            colour=colour())
        await ctx.send(embed=embed)
        return None

    memes = fetch_memes()
    meme = memes[meme_id-1]
    caption_text = list(caption_text)
    for i in range(len(caption_text)):
        if caption_text[i] == "":
            caption_text[i] = " "
            
    #print(caption_text)
    if len(caption_text)!=meme['box_count']:
        embed = discord.Embed(title="Wrong number of captions", 
            description="""Please enter the exact number of captions required in the template
            This template requires {} captions, found {}
            Use `~memeinfo {}` to know more about this template""".format(meme['box_count'], len(caption_text),meme_id),
            colour=colour())
        await ctx.send(embed=embed)
        return None

    new_meme = generate_meme(meme['id'], caption_text)
    #print(new_meme)
    with open("history.json", "r") as file:
        data = json.load(file)
        user = ctx.author
        if str(user.id) in data:
            data[str(user.id)].append({"id":meme['id'], "name":meme['name'], "caption_text":caption_text, "url":new_meme["url"]})
        else:
            data[str(user.id)] = [{"id":meme['id'], "name":meme['name'], "caption_text":caption_text, "url":new_meme["url"]}]
            
    with open("history.json", "w") as file:
        json.dump(data, file)

    embed = discord.Embed(title=meme['name'], colour=colour())
    embed.set_image(url=new_meme['url'])

    message = await ctx.send(embed=embed)

    def check(reaction, user):
        return user != message.author

    await message.add_reaction('⭐')

    reaction = None

    while True:
        if str(reaction) == '⭐':
            add_to_fav(user, ctx.author.id, meme, new_meme, caption_text)
        try:
            reaction, user = await client.wait_for('reaction_add', timeout = 300.0, check=check)
        except:
            break

@client.command(aliases=['mymeme'])
async def mymemes(ctx, meme_id:int=None):
    colour = random_colour()
    user = ctx.author

    with open("history.json") as file:
        data = json.load(file)
    if str(user.id) in data:
        memes = data[str(user.id)]
    else:
        embed = discord.Embed(title="You haven't made any memes yet",
            description="Use `~makememe` to create memes\nUse `~memehelp` to know more",
            colour=colour())
        await ctx.send(embed=embed)
        return None
    memes_len = len(memes)

    if meme_id:
        if meme_id>0 and meme_id<=memes_len:
            meme = memes[meme_id-1]
            embed = discord.Embed(title=meme['name'],
            description="Hey <@{}>! Here's your meme".format(user.id),
            colour=colour())
            embed.set_image(url=meme['url'])
            message = await ctx.send(embed=embed)

            def reaction_check(reaction, reaction_user):
                return reaction_user != message.author

            await message.add_reaction('⭐')

            reaction = None
            reaction_user = None

            while True:
                if str(reaction) == '⭐':
                    add_to_fav(reaction_user, user.id, meme, meme, meme['caption_text'])
                try:
                    reaction, reaction_user = await client.wait_for('reaction_add', timeout = 300.0, check=reaction_check)
                except:
                    break
        else:
            embed = discord.Embed(title="Invalid Meme ID", 
            description="Please select a valid meme\nUse `~mymemes` to get the list of your creations\nUse `~memehelp` to know more",
            colour=colour())
            await ctx.send(embed=embed)
        return None

    pages_len = ceil(memes_len/10)
    meme_list = ""
    pages = []
    for i in range(memes_len):
        meme_list+=("{} - [{}]({})\n".format(i+1, memes[i]['name'], memes[i]['url']))
        if (i+1)%10==0 or (i+1)==memes_len:
            page_colour = random_colour()
            page = discord.Embed(title="List of your memes",
            description="Ayo <@{}>! Here are your memes".format(user.id),
            colour = page_colour())
            page.add_field(name="Page {}/{}".format(ceil((i+1)/10), pages_len), value=meme_list)
            pages.append(page)

            meme_list = ""

    message = await ctx.send(embed = pages[0])

    await message.add_reaction('⏮')
    await message.add_reaction('◀')
    await message.add_reaction('▶')
    await message.add_reaction('⏭')

    def check(reaction, user):
        return user == ctx.author

    i = 0
    reaction = None

    while True:
        if str(reaction) == '⏮':
            i = 0
            await message.edit(embed = pages[i])
        elif str(reaction) == '◀':
            if i > 0:
                i -= 1
                await message.edit(embed = pages[i])
        elif str(reaction) == '▶':
            if i < pages_len-1:
                i += 1
                await message.edit(embed = pages[i])
        elif str(reaction) == '⏭':
            i = pages_len-1
            await message.edit(embed = pages[i])
        
        try:
            reaction, user = await client.wait_for('reaction_add', timeout = 30.0, check = check)
            await message.remove_reaction(reaction, user)
        except:
            break

    await message.clear_reactions()

@client.command(aliases=['showmeme'])
async def showmemes(ctx, user:discord.User=None, meme_id:int=None):
    colour = random_colour()

    if user==None:
        user = ctx.author

    with open("history.json") as file:
        data = json.load(file)
    if str(user.id) in data:
        memes = data[str(user.id)]
    else:
        if user==ctx.author:
            title = "You never created a meme"
            description = "Use `~makememe` to create memes"
        else:
            title = "This user never created a meme"
            description = "Teach <@{}> to make some!".format(user.id)
        embed = discord.Embed(title=title,
            description=description,
            colour=colour())
        await ctx.send(embed=embed)
        return None
    memes_len = len(memes)

    if meme_id:
        if meme_id>0 and meme_id<=memes_len:
            meme = memes[meme_id-1]
            embed = discord.Embed(title=meme['name'],
            description="Kudos to <@{}> for creating this meme".format(user.id),
            colour=colour())
            embed.set_image(url=meme['url'])
            message = await ctx.send(embed=embed)

            def reaction_check(reaction, reaction_user):
                return reaction_user != message.author

            await message.add_reaction('⭐')

            reaction = None
            reaction_user = None
            while True:
                if str(reaction) == '⭐':
                    add_to_fav(reaction_user, user.id, meme, meme, meme['caption_text'])
                try:
                    reaction, reaction_user = await client.wait_for('reaction_add', timeout = 300.0, check=reaction_check)
                except:
                    break
        else:
            embed = discord.Embed(title="Invalid Meme ID", 
            description="Please select a valid meme\nUse `~memehelp` to know more",
            colour=colour())
            await ctx.send(embed=embed)
        return None

    pages_len = ceil(memes_len/10)
    meme_list = ""
    pages = []
    for i in range(memes_len):
        meme_list+=("{} - [{}]({})\n".format(i+1, memes[i]['name'], memes[i]['url']))
        if (i+1)%10==0 or (i+1)==memes_len:
            page_colour = random_colour()
            page = discord.Embed(title="List of memes",
            description="Here are the memes by <@{}>".format(user.id),
            colour = page_colour())
            page.add_field(name="Page {}/{}".format(ceil((i+1)/10), pages_len), value=meme_list)
            pages.append(page)

            meme_list = ""

    message = await ctx.send(embed = pages[0])

    await message.add_reaction('⏮')
    await message.add_reaction('◀')
    await message.add_reaction('▶')
    await message.add_reaction('⏭')

    def check(reaction, user):
        return user == ctx.author

    i = 0
    reaction = None

    while True:
        if str(reaction) == '⏮':
            i = 0
            await message.edit(embed = pages[i])
        elif str(reaction) == '◀':
            if i > 0:
                i -= 1
                await message.edit(embed = pages[i])
        elif str(reaction) == '▶':
            if i < pages_len-1:
                i += 1
                await message.edit(embed = pages[i])
        elif str(reaction) == '⏭':
            i = pages_len-1
            await message.edit(embed = pages[i])
        
        try:
            reaction, user = await client.wait_for('reaction_add', timeout = 30.0, check = check)
            await message.remove_reaction(reaction, user)
        except:
            break

    await message.clear_reactions()

@client.command(aliases=['myfavmeme'])
async def myfavmemes(ctx, meme_id:int=None):
    colour = random_colour()
    user = ctx.author

    with open("favourite.json") as file:
        data = json.load(file)
    if str(user.id) in data:
        memes = data[str(user.id)]
    else:
        embed = discord.Embed(title="You haven't saved any memes yet",
            description="Use `~myfavmemes` to see your saved memes\nUse `~memehelp` to know more",
            colour=colour())
        await ctx.send(embed=embed)
        return None
    memes_len = len(memes)

    if meme_id:
        if meme_id>0 and meme_id<=memes_len:
            meme = memes[meme_id-1]
            embed = discord.Embed(title=meme['name'],
            description="Kudos to <@{}> for creating this meme".format(meme['creator']),
            colour=colour())
            embed.set_image(url=meme['url'])
            message = await ctx.send(embed=embed)

            def reaction_check(reaction, reaction_user):
                return reaction_user != message.author and reaction_user!=user

            await message.add_reaction('⭐')

            reaction = None
            reaction_user = None
            while True:
                if str(reaction) == '⭐':
                    add_to_fav(reaction_user, meme['creator'], meme, meme, meme['caption_text'])
                try:
                    reaction, reaction_user = await client.wait_for('reaction_add', timeout = 300.0, check=reaction_check)
                except:
                    break
        else:
            embed = discord.Embed(title="Invalid Meme ID", 
            description="Please select a valid meme\nUse `~myfavmemes` to get the list of your saved memes",
            colour=colour())
            await ctx.send(embed=embed)
        return None

    pages_len = ceil(memes_len/10)
    meme_list = ""
    pages = []
    for i in range(memes_len):
        creator = await client.fetch_user(memes[i]['creator'])
        meme_list+=("{} - [{}]({}) - [{}]\n".format(i+1, memes[i]['name'], memes[i]['url'], creator))
        if (i+1)%10==0 or (i+1)==memes_len:
            page_colour = random_colour()
            page = discord.Embed(title="List of your saved memes",
            description="Ayo <@{}>! Here are your saved memes".format(user.id),
            colour = page_colour())
            page.add_field(name="Page {}/{}".format(ceil((i+1)/10), pages_len), value=meme_list)
            pages.append(page)

            meme_list = ""

    message = await ctx.send(embed = pages[0])

    await message.add_reaction('⏮')
    await message.add_reaction('◀')
    await message.add_reaction('▶')
    await message.add_reaction('⏭')

    def check(reaction, user):
        return user == ctx.author

    i = 0
    reaction = None

    while True:
        if str(reaction) == '⏮':
            i = 0
            await message.edit(embed = pages[i])
        elif str(reaction) == '◀':
            if i > 0:
                i -= 1
                await message.edit(embed = pages[i])
        elif str(reaction) == '▶':
            if i < pages_len-1:
                i += 1
                await message.edit(embed = pages[i])
        elif str(reaction) == '⏭':
            i = pages_len-1
            await message.edit(embed = pages[i])
        
        try:
            reaction, user = await client.wait_for('reaction_add', timeout = 30.0, check = check)
            await message.remove_reaction(reaction, user)
        except:
            break

    await message.clear_reactions()

@client.command(aliases = ['favmeme'])
async def favmemes(ctx, user:discord.User, meme_id:int = None):
    colour = random_colour()

    with open("favourite.json") as file:
        data = json.load(file)
    if str(user.id) in data:
        memes = data[str(user.id)]
    else:
        embed = discord.Embed(title="This user never saved a meme",
            description="Tell <@{}> to use ⭐".format(user.id),
            colour=colour())
        await ctx.send(embed=embed)
        return None
    memes_len = len(memes)

    if meme_id:
        if meme_id>0 and meme_id<=memes_len:
            meme = memes[meme_id-1]
            embed = discord.Embed(title=meme['name'],
            description="Kudos to <@{}> for creating this meme".format(meme['creator']),
            colour=colour())
            embed.set_image(url=meme['url'])
            message = await ctx.send(embed=embed)

            def reaction_check(reaction, reaction_user):
                return reaction_user != message.author and reaction_user!=user

            await message.add_reaction('⭐')

            reaction = None
            reaction_user = None
            while True:
                if str(reaction) == '⭐':
                    add_to_fav(reaction_user, meme['creator'], meme, meme, meme['caption_text'])
                try:
                    reaction, reaction_user = await client.wait_for('reaction_add', timeout = 300.0, check=reaction_check)
                except:
                    break

        else:
            embed = discord.Embed(title="Invalid Meme ID", 
            description="Please select a valid meme\nUse `~favmemes @user` to get the list of their memes",
            colour=colour())
            await ctx.send(embed=embed)
        return None

    pages_len = ceil(memes_len/10)
    meme_list = ""
    pages = []
    for i in range(memes_len):
        creator = await client.fetch_user(memes[i]['creator'])
        meme_list+=("{} - [{}]({}) - [{}]\n".format(i+1, memes[i]['name'], memes[i]['url'], creator))
        if (i+1)%10==0 or (i+1)==memes_len:
            page_colour = random_colour()
            page = discord.Embed(title="List of memes",
            description="Here are the memes saved by <@{}>".format(user.id),
            colour = page_colour())
            page.add_field(name="Page {}/{}".format(ceil((i+1)/10), pages_len), value=meme_list)
            pages.append(page)

            meme_list = ""

    message = await ctx.send(embed = pages[0])

    await message.add_reaction('⏮')
    await message.add_reaction('◀')
    await message.add_reaction('▶')
    await message.add_reaction('⏭')

    def check(reaction, user):
        return user == ctx.author

    i = 0
    reaction = None

    while True:
        if str(reaction) == '⏮':
            i = 0
            await message.edit(embed = pages[i])
        elif str(reaction) == '◀':
            if i > 0:
                i -= 1
                await message.edit(embed = pages[i])
        elif str(reaction) == '▶':
            if i < pages_len-1:
                i += 1
                await message.edit(embed = pages[i])
        elif str(reaction) == '⏭':
            i = pages_len-1
            await message.edit(embed = pages[i])
        
        try:
            reaction, user = await client.wait_for('reaction_add', timeout = 30.0, check = check)
            await message.remove_reaction(reaction, user)
        except:
            break

    await message.clear_reactions()

@client.command(aliases=['memeexample'])
async def examplememe(ctx, meme_id:int):
    colour = random_colour()
    if meme_id>100 or meme_id<0:
        embed = discord.Embed(title="Invalid Meme ID", 
            description="Please select a valid template\nUse `~templates` to get the list of templates",
            colour=colour())
        await ctx.send(embed=embed)
        return None

    memes = fetch_memes()
    meme = memes[meme_id-1]

    r = requests.get("https://imgflip.com/meme/{}".format(meme['id']))
    memepage_data = BeautifulSoup(r.text, 'html.parser')
    top_example = "https:" + memepage_data.select(".meme-link img")[1]['src']

    embed = discord.Embed(title=meme['name']+" Example", colour=colour())
    embed.set_image(url=top_example)
    await ctx.send(embed=embed)

@client.command()
async def memehelp(ctx):
    colour = random_colour()
    embed = discord.Embed(title="MemeMaker Help", description="A simple bot for creating memes with discord!",colour=colour())
    embed.set_thumbnail(url="https://i1.sndcdn.com/avatars-000108040698-2z3kzo-t500x500.jpg")
    embed.add_field(name="~meme", value="Display a random meme", inline=False)
    embed.add_field(name="~templates", value="Display the list of 100 templates (25 on each page). Use the arrows/number emojis to navigate between pages.", inline=False)
    embed.add_field(name="~memeinfo id", value="Display the usage of the meme corresponding to `id` in the template list.", inline=False)
    embed.add_field(name="~examplememe id", value="Display the top meme example corresponding to `id`.\nAlias = memeexample", inline=False)
    embed.add_field(name="~makememe id \"text0\" \"text1\"", value="This will generate the meme with captions provided. Use \"\" to leave a caption blank. A user can save the meme by cliking on the ⭐ reaction.")
    embed.add_field(name="~mymemes", value="Display the list of memes you've created.\nUse `~mymemes id` to show a meme.\nAlias = mymeme", inline=False)
    embed.add_field(name="~showmemes @user", value="Display the memes created by @user.\nUse `~showmemes @user id` to show a particular meme.\nUse `~showmemes` to display your memes.\nAlias = showmeme", inline=False)
    embed.add_field(name="~myfavmemes", value="Display the list of memes you've saved.\nUse `~myfavmemes id` to show a meme.\nAlias = myfavmeme", inline=False)
    embed.add_field(name="~favmemes @user", value="Display the memes saved by @user.\nUse `~favmemes @user id` to show a particular meme.\nAlias = favmeme", inline=False)

    await ctx.send(embed=embed)

client.run(TOKEN)

