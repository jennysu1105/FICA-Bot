import json

async def get_t_codes():
  with open("t_codes.json", 'r') as f:
    return json.load(f)

async def save_t_codes(t_codes):
  with open("t_codes.json", "w") as f:
    json.dump(t_codes, f)

async def open_t_code(code):
  codes = await get_t_codes()
  if code in codes:
    return False
  
  else:
    codes[code] = {}
    codes[code]["date"] = "TBD"
    codes[code]["decks"] = "TBD"
    codes[code]["web"] = "NA"

  await save_t_codes(codes)

  return True

async def get_decks():
  with open("decks.json", 'r') as f:
    return json.load(f)

async def save_decks(decks):
  with open("decks.json", "w") as f:
    json.dump(decks, f)

async def open_code_decks(code):
  decks = await get_decks()
  if code in decks:
    return False
  
  else:
    decks[code] = {}

  await save_decks(decks)

  return True

async def open_user_decks(code, user):
  decks = await get_decks()

  if str(user.id) in decks[code]:
    return False
  
  else:
    decks[code][str(user.id)] = "$http"
  
  await save_decks(decks)

  return True