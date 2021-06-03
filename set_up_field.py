import discord

async def set_up_t_full(codes, c, em):
  em.add_field(name = c, value = "Name: {}\nStatus: {}\nDate: {}\nMax Decks: {}\nWebsite: {}".format(codes[c]["name"], codes[c]["status"], codes[c]["date"], codes[c]["decks"], codes[c]['web']))
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