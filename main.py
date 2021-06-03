import discord
import os
import datetime
from discord.ext import commands
from discord.utils import get
from keep_alive import keep_alive
from access_json import *
from set_up_field import *
import requests
import shutil
from PIL import Image

client = commands.Bot(command_prefix = "f!")

@client.event
async def on_ready():
  print("Ready!")

# HELP
@client.command(name = "h")
async def help(ctx, *specs):
  if len(specs) == 0:
    em = discord.Embed(title = "General Help", description = "f!h <type> for more indepth help.")
    em.add_field(name = "f!h t", value = "Tournament related commands")

    await ctx.send(embed = em)
    return
  
  if specs[0].lower() == "t":
    em = discord.Embed(title = "Tournament Commands", description = "Tournament related commands.")

    em.add_field(name = "Organizational Commands", value = "For tournament organizers", inline = False)
    em.add_field(name = "f!tn <ID CODE> <NAME>", value = "NEW TOURNAMENT\nCreate a new tournament with an access code of <ID CODE> (unique) and called <NAME>")
    em.add_field(name = "f!td <ID CODE> <DATE>", value = "SET DATE\nSet the date for the tournament")
    em.add_field(name = "f!md <ID CODE> <MAX # DECKS", value = "SET MAX # DECK\nSet the maximum number of decks a player can submit")
    em.add_field(name = "f!w <ID CODE> <URL>", value = "SET WEBSITE\nSets the website for the tournament related to the <ID CODE>")
    em.add_field(name = "f!tc <ID CODE>", value = "CLOSE TOURNAMENT\nSwitches tournament status to CLOSED")
    em.add_field(name = "f!to <ID CODE>", value = "REOPEN TOURNAMENT\nSwitches tournament status to OPEN")
    em.add_field(name = "f!tr <ID CODE>", value = "REMOVE TOURNAMENT\nDeletes the tournament with <ID CODE>")

    em.add_field(name = "Participant Commands", value = "For tournament participants", inline = False)
    em.add_field(name = "f!ta [o, c]", value = "VIEW TOURNAMENTS\nf!ta to show all tournaments\nf!ta o to show all open tournaments\nf!ta c to show all closed tournaments")
    em.add_field(name = "f!ts <ID CODE> [Deck #]", value = "SUBMIT DECK\nAdd deck to tournament with id <ID CODE> at place [DECK #], or if [] left blank, the first closest space")
    em.add_field(name = "f!tdcl <ID CODE> [DECK #]", value = "CLEAR DECK\nf!tdcl to clear all decks\nf!tdcl [DECK #] to remove the [DECK #]th deck on the list")
    em.add_field(name = "f!tdl <ID CODE> <@PERSON>", value = "VIEW DECKLIST\nView the given person's decklist for the tournament")

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

  await save_t_codes(codes)
  em = discord.Embed(title = "Success", description = "{} has been created under code: {}".format(codes[code]["name"], code))
  await ctx.send(embed = em)

@client.command(name = "td")
async def set_tournament_date(ctx, code, *d):
  code = code.upper()
  d = " ".join(d)

  codes = await get_t_codes()
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
  if await check_c(ctx, codes, code):
    return
  
  codes[code]["web"] = w
  await save_t_codes(codes)

  em = discord.Embed(title = "Success", description = "{} website set to {}".format(code, w))
  await ctx.send(embed = em)

@client.command(name = "tc")
async def close_tournament(ctx, code):
  code = code.upper()
  codes = await get_t_codes()
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
        em = await set_up_t_full(codes, c, em)

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
        em = await set_up_t_full(codes, c, em)

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
    if x.isdigit():
      urls[int(x)-1] = ""
      success.append(x)

  decks[code][str(ctx.author.id)] = "$http".join(urls)
  await save_decks(decks)

  em = discord.Embed(title = "Success", description = "Deck(s) {} has been cleared".format(", ".join(success)))
  await ctx.send(embed = em)  
    
@client.command(name = "tdl")
async def display_decks(ctx, code, member : discord.Member):
  code = code.upper()
  codes = await get_t_codes()

  if await check_c(ctx, codes, code):
    return
  
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

  #for url in urls:
  #i += 1
  #if url == "":
    #continue
  #em = discord.Embed(title = "Deck {}".format(str(i)))
  #em.set_image(url = "http" + url)
  #await ctx.send(embed = em)
  
  imgs = []

  for url in urls:
    i += 1
    if url == "":
      continue
    r = requests.get("http" + url, stream = True)
    imageName = "img" + str(i) + ".jpg"

    with open(imageName, 'wb') as f:
      shutil.copyfileobj(r.raw, f)

    imgs.append(Image.open("img" + str(i) + ".jpg"))
  
  widths, heights = zip(*(i.size for i in imgs))

  total_width = sum(widths)
  max_height = max(heights)

  new_im = Image.new('RGB', (total_width, max_height))
  x_offset = 0
  for im in imgs:
    new_im.paste(im, (x_offset,0))
    x_offset += im.size[0]
  new_im.save('decks.jpg')

  f = discord.File("decks.jpg")
  em = discord.Embed(title = "{}'s Decks".format(member.name))
  em.set_image(url="attachment://decks.jpg")
  await ctx.send(embed = em, file = f)


keep_alive()
client.run(os.environ['TOKEN'])