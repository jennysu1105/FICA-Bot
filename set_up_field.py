import discord

async def set_up_t_full(client, codes, c, em):
  admins = codes[c]["admins"].split("$")
  a_names = []
  for a in admins:
    user = await client.fetch_user(int(a))
    if user != None:
      a_names.append(user.name)
  
  em.add_field(name = c, value = "Name: {}\nStatus: {}\nDate: {}\nMax Decks: {}\nWebsite: {}\nOrganizers: {}".format(codes[c]["name"], codes[c]["status"], codes[c]["date"], codes[c]["decks"], codes[c]['web'], ", ".join(a_names)))
  return em

async def check_c(ctx, codes, c):
  if c not in codes:
    em = discord.Embed(title = "Unsuccessful", description = "{} does not exist!".format(c))
    await ctx.send(embed = em)
    return True
  return False

async def check_closed_c(ctx, codes, c, str):
  if codes[c]["status"] == "CLOSED":
    em = discord.Embed(title = "Successful", description = "{} is closed! {}".format(c, str))
    await ctx.send(embed = em)
    return True
  return False

async def check_admin(ctx, codes, c):
  admins = codes[c]["admins"].split("$")
  if str(ctx.author.id) in admins:
    return True
  
  em = discord.Embed(title = "Unsuccessful", description = "{} is not an organizer for {}".format(ctx.author.name, c))
  await ctx.send(embed = em)
  return False
