import discord

async def general_help():
  em = discord.Embed(title = "General Help", description = "f!h <type> for more indepth help.")
  em.add_field(name = "f!h t", value = "Tournament related commands")
  return em

async def tournament_help():
  em = discord.Embed(title = "Tournament Commands", description = "Tournament related commands.")

  em.add_field(name = "Organizational Commands", value = "For tournament organizers", inline = False)
  em.add_field(name = "f!tn <ID CODE> <NAME>", value = "NEW TOURNAMENT\nCreate a new tournament with an access code of <ID CODE> (unique) and called <NAME>")
  em.add_field(name = "f!tdf <OLD CODE> <NEW CODE>", value = "DUPLICATE FORMAT\nTakes the format as <OLD CODE> and creates a new tournament with the same name, admin, max # deck fields to <NEW CODE>")
  em.add_field(name = "f!td <ID CODE> <DATE>", value = "SET DATE\nSet the date for the tournament")
  em.add_field(name = "f!md <ID CODE> <MAX # DECKS>", value = "SET MAX # DECK\nSet the maximum number of decks a player can submit")
  em.add_field(name = "f!w <ID CODE> <URL>", value = "SET WEBSITE\nSets the website for the tournament related to the <ID CODE>")
  em.add_field(name = "f!torgs <ID CODE> <@MEMBERS>", value = "ADD NEW ADMINS\nAdd the given users as admins")
  em.add_field(name = "f!tro <ID CODE> <@MEMBERS>", value = "REMOVE ADMINS\nRemoves members from the admin role of the tournament")
  em.add_field(name = "f!tc <ID CODE>", value = "CLOSE TOURNAMENT\nSwitches tournament status to CLOSED")
  em.add_field(name = "f!to <ID CODE>", value = "REOPEN TOURNAMENT\nSwitches tournament status to OPEN")
  em.add_field(name = "f!tr <ID CODE>", value = "REMOVE TOURNAMENT\nDeletes the tournament with <ID CODE>")

  em.add_field(name = "Participant Commands", value = "For tournament participants", inline = False)
  em.add_field(name = "f!ta [o, c]", value = "VIEW TOURNAMENTS\nf!ta to show all tournaments\nf!ta o to show all open tournaments\nf!ta c to show all closed tournaments")
  em.add_field(name = "f!ts <ID CODE> [DECK #]", value = "SUBMIT DECK\nAdd deck to tournament with id <ID CODE> at place [DECK #], or if [] left blank, the first closest space\nREMINDER: You must reprint this to submit another deck!")
  em.add_field(name = "f!tcd <FROM CODE> <TO CODES>", value = "DUPLICATE DECKS\nCopies the deck list of <FROM CODE> and duplicated them to <TO CODES>")
  em.add_field(name = "f!tdcl <ID CODE> [DECK #s]", value = "CLEAR DECK\nf!tdcl to clear all decks\nf!tdcl [DECK #] to remove the [DECK #s]th deck on the list")
  em.add_field(name = "f!tdl <ID CODE> [@PERSON]", value = "VIEW DECKLIST\nf!dl <ID CODE> to view your submitted decklists\nf!tdl <ID CODE> [@PERSON] to view the given person's decklist for the tournament")
  
  return em