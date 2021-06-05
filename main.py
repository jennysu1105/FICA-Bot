import discord
import os
import datetime
from discord.ext import commands
from keep_alive import keep_alive
from access_json import *
from set_up_field import *
import requests
import shutil
from help import *
from PIL import Image

client = commands.Bot(command_prefix = "f!")

@client.event
async def on_ready():
  await client.change_presence(activity=discord.Game(name="prototype... f!h to get help"))
  print("Ready!")

# HELP
@client.command(name = "h")
async def help(ctx, *specs):
  if len(specs) == 0:
    em = await general_help()
  
  if specs[0].lower() == "t":
    em = await tournament_help()

  await ctx.send(embed = em)
  return

# TOURNAMENT INFORMATION RELATED COMMANDS
  # ADMIN COMMANDS
@client.command(name = "tn")
async def create_tournament(ctx, code, *name):
  code = code.upper()
  codes = await get_t_codes()
  if code in codes:
    em = discord.Embed(title = "Unsuccessful", description = "{} already exists".format(code))
    await ctx.send(embed = em)
    return
  
  await open_t_code(code)
  await open_code_decks(code)
  codes = await get_t_codes()

  codes[code]["name"] = " ".join(name)
  codes[code]["status"] = "OPEN"
  codes[code]["admins"] = str(ctx.author.id)

  await save_t_codes(codes)
  em = discord.Embed(title = "Success", description = "{} has been created under code: {}".format(codes[code]["name"], code))
  await ctx.send(embed = em)

@client.command(name = "tdf", pass_context = True)
async def duplicate_format(ctx, old, new):
  old = old.upper()
  new = new.upper()
  codes = await get_t_codes()

  if not await check_admin(ctx, codes, old):
    return

  if new in codes:
    em = discord.Embed(title = "Unsuccessful", description = "{} already exists".format(new))
    await ctx.send(embed = em)
    return
  
  await open_t_code(new)
  await open_code_decks(new)

  codes = await get_t_codes()

  codes[new]["name"] = codes[old]["name"]
  codes[new]["status"] = "OPEN"
  codes[new]["admins"] = codes[old]["admins"]
  codes[new]["decks"] = codes[old]["decks"]

  await save_t_codes(codes)
  em = discord.Embed(title = "Success", description = "{}'s format has been duplicated to {}".format(old, new))
  await ctx.send(embed = em)

@client.command(name = "td", pass_context = True)
async def set_tournament_date(ctx, code, *d):
  code = code.upper()
  d = " ".join(d)

  codes = await get_t_codes()

  if not await check_admin(ctx, codes, code):
    return

  if await check_c(ctx, codes, code):
    return

  codes[code]["date"] = d
  await save_t_codes(codes)

  em = discord.Embed(title = "Success", description = "{} set to {}".format(code, d))
  await ctx.send(embed = em)

@client.command(name = "tmd")
async def set_max_decks(ctx, code, d):
  code = code.upper()
  codes = await get_t_codes()

  if not await check_admin(ctx, codes, code):
    return

  if await check_c(ctx, codes, code):
    return

  if not d.isdigit():
    em = discord.Embed(title = "Unsuccessful", description = "<Max Deck> must be an integer")
    await ctx.send(embed = em)
    return

  codes[code]["decks"] = d
  await save_t_codes(codes)

  em = discord.Embed(title = "Success", description = "{} max deck submit set to {}".format(code, d))
  await ctx.send(embed = em)

@client.command(name = "tw")
async def set_website(ctx, code, w):
  code = code.upper()
  codes = await get_t_codes()

  if not await check_admin(ctx, codes, code):
    return

  if await check_c(ctx, codes, code):
    return
  
  codes[code]["web"] = w
  await save_t_codes(codes)

  em = discord.Embed(title = "Success", description = "{} website set to {}".format(code, w))
  await ctx.send(embed = em)

@client.command(name = "torgs")
async def add_organizers(ctx, code, *members : discord.Member):
  code = code.upper()
  codes = await get_t_codes()

  if not await check_admin(ctx, codes, code):
    return

  if await check_c(ctx, codes, code):
    return

  admins = codes[code]["admins"].split("$")
  success = []
  for m in members:
    if str(m.id) not in admins:
      admins.append(str(m.id))
      success.append(m.name)
  
  codes[code]["admins"] = "$".join(admins)
  await save_t_codes(codes)

  if success == []:
    em = discord.Embed(title = "Success", description = "All are already admins")
  else:
    em = discord.Embed(title = "Success", description = "{} are now organizers of {}".format(", ".join(success), code))
  await ctx.send(embed = em)

@client.command(name = "tro")
async def remove_organizers(ctx, code, *members : discord.Member):
  code = code.upper()
  codes = await get_t_codes()

  if await check_c(ctx, codes, code):
    return

  admins = codes[code]["admins"].split("$")
  for m in members:
    admins.remove(str(m.id))

  codes[code]["admins"] = "$".join(admins)
  await save_t_codes(codes)

  em = discord.Embed(title = "Success", description = "{} are not organizers of {} anymore".format(", ".join(list(map(lambda x: x.name, members))), code))
  await ctx.send(embed = em)

@client.command(name = "tc")
async def close_tournament(ctx, code):
  code = code.upper()
  codes = await get_t_codes()

  if not await check_admin(ctx, codes, code):
    return

  if await check_c(ctx, codes, code):
    return
  
  codes[code]["status"] = "CLOSED"
  await save_t_codes(codes)
  em = discord.Embed(title = "Successful", description = "{} is now closed!".format(code))
  await ctx.send(embed = em)

@client.command(name = "to")
async def open_tournament(ctx, code):
  code = code.upper()
  codes = await get_t_codes()

  if not await check_admin(ctx, codes, code):
    return

  if await check_c(ctx, codes, code):
    return

  codes[code]["status"] = "OPEN"
  await save_t_codes(codes)

  em = discord.Embed(title = "Successful", description = "{} is now open!".format(code))
  await ctx.send(embed = em)
  
@client.command(name = "tcl", pass_context=True)
@commands.has_permissions(administrator=True)
async def clear_tournaments(ctx):
  await save_t_codes({})
  await save_decks({})
  em = discord.Embed(title = "Clear Successful")
  await ctx.send(embed = em)

@client.command(name = "tr")
async def remove_tournament(ctx, code):
  code = code.upper()
  codes = await get_t_codes()
  decks = await get_decks()

  if not await check_admin(ctx, codes, code):
    return
    
  if await check_c(ctx, codes, code):
    return
  
  del codes[code]
  del decks[code]

  await save_t_codes(codes)
  await save_decks(decks)
  em = discord.Embed(title = "Successful", description = "{} has been removed.".format(code))
  await ctx.send(embed = em)

  # PUBLIC COMMANDS
@client.command(name = "ta")
async def view_tournament(ctx, f = ""):
  f = f.lower()
  codes = await get_t_codes()
  em = discord.Embed(title = "All Tournaments")

  if not f == "c":
    if f == "o":
      em = discord.Embed(title = "Open Tournaments", description = "List of all open tournaments")

    if f == "":
      em.add_field(name = "Opened Tournaments",value = "List of all open tournaments", inline = False)

    for c in codes:
      if codes[c]["status"] == "OPEN":
        em = await set_up_t_full(client, codes, c, em)

    if f == "o":
      await ctx.send(embed = em)
      return
  
  if not f == "o":
    if f == "c":
      em = discord.Embed(title = "Closed Tournaments", description = "List of allpast tournaments")

    if f == "":
      em.add_field(name = "Closed Tournaments", value = "List of all past tournaments", inline = False)

    for c in codes:
      if codes[c]["status"] == "CLOSED":
        em = await set_up_t_full(client, codes, c, em)

    if f == "c":
      await ctx.send(embed = em)
      return
  
  if f == "":
    await ctx.send(embed = em)

# MEMBER SPECIFIC COMMANDS
  # DECK COMMANDS
@client.command(name = "ts")
async def submit_deck(ctx, code, n = "-1"):
  code = code.upper()
  codes = await get_t_codes()

  if await check_c(ctx, codes, code):
    return

  if await check_closed_c(ctx, codes, code, "Cannot submit decks anymore!"):
    return

  if not ctx.message.attachments:
    em = discord.Embed(title = "Unsuccessful", description = "No Image Detected")
    await ctx.send(embed = em)
    return

  if not ctx.message.attachments[0].url.endswith(".png") and not ctx.message.attachments[0].url.endswith(".PNG") and not ctx.message.attachments[0].url.endswith(".jpeg") and not ctx.message.attachments[0].url.endswith(".JPEG") and not ctx.message.attachments[0].url.endswith(".JPG") and not ctx.message.attachments[0].url.endswith(".jpg"):
    em = discord.Embed(title = "Unsuccessful", description = "No Image Detected")
    await ctx.send(embed = em)
    return

  if not n.isdigit() and not n == "-1":
    em = discord.Embed(title = "Unsuccessful", description = "<Deck Number> must be an integer")
    await ctx.send(embed = em)
    return

  if not codes[code]["decks"] == "TBD" and not n == "-1":
    if int(n) < 1 and n > int(codes[code]["decks"]):
      em = discord.Embed(title = "Unsuccessful", description = "Attempt to submit deck {}, but maximum number of decks is {}".format(n, codes[code]["decks"]))
      await ctx.send(embed = em)
      return
  
  await open_user_decks(code, ctx.author)
  decks = await get_decks()

  urls = decks[code][str(ctx.author.id)].split("$http")
  sub = 0
  for url in urls:
    if url == "":
      continue
    sub += 1
  
  if n == "-1" and (int(codes[code]["decks"]) <= sub):
    em = discord.Embed(title = "Unsuccessful", description = "You have reached the maximum number of decks.")
    await ctx.send(embed = em)
    return

  if n == "-1":
    placed = False
    for x in range(len(urls)):
      if urls[x] == "":
        urls[x] = ctx.message.attachments[0].url[4:]
        placed = True
        n = x + 1
        break
    if not placed:
      urls.append(ctx.message.attachments[0].url[4:])
      n = len(urls)
  
  else:
    if int(n) > len(urls):
      for _ in range(int(n) - len(urls)):
        urls.append("")
    urls[int(n)-1] = ctx.message.attachments[0].url[4:]

  decks[code][str(ctx.author.id)] = "$http".join(urls)
  await save_decks(decks)

  em = discord.Embed(title = "Success", description = "Deck {} updated with attachment".format(n))
  urls = decks[code][str(ctx.author.id)].split("$http")
  em.set_image(url = "http" + urls[int(n)-1])
  await ctx.send(embed = em)

@client.command(name = "tdcl")
async def remove_deck(ctx, code, *n):
  success = []
  code = code.upper()
  codes = await get_t_codes()

  if await check_c(ctx, codes, code):
    return

  if await check_closed_c(ctx, codes, code, "Cannot submit decks anymore!"):
    return
  
  await open_user_decks(code, ctx.author)
  decks = await get_decks()

  if len(n) == 0:
    decks[code][str(ctx.author.id)] = {}
    em = discord.Embed(title = "Success", description = "Cleared all decks")
    await ctx.send(embed = em)
    return

  urls = decks[code][str(ctx.author.id)].split("$http")
  for x in n:
    if x.isdigit() and int(x) <= int(codes[code]["decks"]):
      urls[int(x)-1] = ""
      success.append(x)

  decks[code][str(ctx.author.id)] = "$http".join(urls)
  await save_decks(decks)

  em = discord.Embed(title = "Success", description = "Deck(s) {} has been cleared".format(", ".join(success)))
  await ctx.send(embed = em)  

@client.command(name = "tcd")
async def duplicate_deck(ctx, fro, *to):
  fro = fro.upper()
  to = list(map(lambda x:x.upper(), to))

  codes = await get_t_codes()

  if await check_c(ctx, codes, fro):
    return
  
  valid = []
  for c in to:
    if c not in codes:
      continue
    valid.append(c)

  await open_user_decks(fro, ctx.author)
  for c in valid:
    await open_user_decks(c, ctx.author)
  decks = await get_decks()

  for c in valid:
    l = decks[fro][str(ctx.author.id)].split("$http")
    l = list(filter(lambda a: a != "", l))
    if codes[c]["decks"] != "TBH":
      if len(l) > int(codes[c]["decks"]):
        l = l[:int(codes[c]["decks"])]
    decks[c][str(ctx.author.id)] = "$http".join(l)

  await save_decks(decks)
  em = discord.Embed(title = "Success", description = "Decklist of {} had been copied to {}".format(fro, ", ".join(valid)))
  await ctx.send(embed = em)

@client.command(name = "tdl")
async def display_decks(ctx, code, *member : discord.Member):
  code = code.upper()
  codes = await get_t_codes()

  if await check_c(ctx, codes, code):
    return
  
  if len(member) == 0:
    member = ctx.author
  else:
    member = member[0]

  decks = await get_decks()
  if str(member.id) not in decks[code]:
    em = discord.Embed(title = "Unsuccessful", description = "{} has not submitted any decks yet".format(member.name))
    await ctx.send(embed = em)
    return
  

  urls = decks[code][str(member.id)].split("$http")
  if urls == [""]*len(urls):
    em = discord.Embed(title = "Unsuccessful", description = "{} has not submitted any decks yet".format(member.name))
    await ctx.send(embed = em)
    return
    
  i = 0
  imgs = []

  for url in urls:
    i += 1
    if url == "":
      continue
    r = requests.get("http" + url, stream = True)
    imageName = "res/img" + str(i) + ".jpg"

    with open(imageName, 'wb') as f:
      shutil.copyfileobj(r.raw, f)

    imgs.append(Image.open("res/img" + str(i) + ".jpg"))
  
  widths, heights = zip(*(i.size for i in imgs))

  total_width = sum(widths)
  max_height = max(heights)

  new_im = Image.new('RGB', (total_width, max_height))
  x_offset = 0
  for im in imgs:
    new_im.paste(im, (x_offset,0))
    x_offset += im.size[0]
  new_im.save('res/decks.jpg')

  f = discord.File("res/decks.jpg")
  em = discord.Embed(title = "{}'s Decks".format(member.name))
  em.set_image(url="attachment://res/decks.jpg")
  await ctx.send(embed = em, file = f)

keep_alive()
client.run(os.environ['TOKEN'])