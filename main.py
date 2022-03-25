import discord
import os
import requests
import json
import asyncio
import random

#token and verification
token = os.environ['TOKEN']
client = discord.Client()

#bot startup
@client.event
async def on_ready():
  print('Logged In as {0.user}'.format(client))
  
  #set activity status
  activity = discord.Game(name="MT Help", type=3)
  await client.change_presence(status=discord.Status.idle, activity=activity)

#listens to messages sent by users
@client.event
async def on_message(message):
  
  #ignored if sent by self
  if message.author == client.user:
    return
    
  msg = message.content

  #opens list of users who have set up points
  with open("users.json","r") as file:
    users = json.load(file)
    user = message.author
    user_id = str(user.id)
    
    if msg == "MT Points":

      #adds points to existing user
      if user_id in users:
        with open("users.json","w") as file:
          users[user_id]["Points"] += 10
          json.dump(users, file, sort_keys=True, indent=4, ensure_ascii=False)
          await message.channel.send('10 Points Awarded !')

      #create record and then add points to new user
      else:
        with open("users.json","w") as file:
          users = {}
          users[user_id] = {}
          users[user_id]["Points"] = 0
          json.dump(users, file, sort_keys=True, indent=4, ensure_ascii=False)
          await message.channel.send('New adventurer detected ! \nWelcome ! Your points are now being tracked')
          await message.channel.send('10 Points Awarded !')

    #clear all points
    if msg == "MT Points Clear":
      with open("users.json","w") as file:
          users[user_id]["Points"] = 0
          json.dump(users, file, sort_keys=True, indent=4, ensure_ascii=False)
          await message.channel.send('All points cleared')

		

  #trivia game mode
  async def trivia_mode():
    bot_message = ''
    reactions = ["🇦", "🇧", "🇨", "🇩", "🇪"]

    #question bank
    questions = {
      'At what age was Rudeus hit by a truck during his previous life ?': 'C', 
      'Ruijerd Superdia is also known as... ?': ['C','E'],
      'Ghyslaine is part of the ___ race.': 'B' }

    #choices correspond to questions.keys()
    choices = [
              ["A. 22","B. 28","C. 34","D. 41"],
              ["A. Demonic Reaper","B. The Evil Supard","C. Dead End","D. Protector of Children", "E. Guard Dog Ruijerd"],
              ["A. Demon","B. Beastfolk","C. Marewolf","D. Forestor"]
              ]

    #responses correspond to choices
    responses = [
              ["Come on bro, did he look that young ?","Close, but not quite","That's right, you got it !","If he was that old, he might've died from a heart attack instead."],
              ["Terrifying, but not right.","Although most people believe he's evil, nobody calls him this.","Correct ! He's known as 'Dead End' because those who meet him have their fates cut short (i.e reach a dead end in thier lives) , or so the rumour goes.","A more accurate name out of all the choices, but sadly, very few people regard him as such.", "Also correct ! He's known as Guard Dog Ruijerd of Dead End during his time partying up with Rudeus and Eris. "],
              ["A demon huh ? Although its true that Ghylaine's race often intermingles closely with the Demon race, she isn't a half-breed. Better luck next round !","Right ! Did you guess that based on her tail and fluffy ears ?","Sorry to say, there is no such race in Mushoku Tensei's world","What even is a 'Forestor' ? Someone who lives in a forest ? I sure don't know."]
              ]
    
    random_number = random.randint(0, len(questions)-1)

    question_keys = list(questions.keys())
    question = question_keys[random_number]
    choice = choices[random_number]
    response = responses[random_number]
    choices_message = '\n'.join(choice)
    correct_answer = questions.get(question)

    #send question as an embed
    embedded = discord.Embed(title = f"{question}\n{choices_message}")
    bot_message = await message.channel.send(embed = embedded)
    for i in range (len(choice)):
        await bot_message.add_reaction(reactions[i])


    #answered = False
      
    #Check and return reaction user and all available reactions
    def check(reaction, user):
        reacts = ["🇦", "🇧", "🇨", "🇩", "🇪"]
        if user == client.user:
          return
        else:
          return user == message.author and str(reaction.emoji) in reacts
        

    try:
      reaction, user = await client.wait_for('reaction_add', timeout=20.0, check=check)
    
      #Stop round if time limit exceeded
    except asyncio.TimeoutError:
      await message.channel.send('Timeout, try to react faster next time')

    #carry on if reaction given
    else:   
          channel = message.channel
      
          if reaction.emoji == "🇦":
              flag = check_answer(correct_answer, 'A')
              await create_embed_response(flag, response[0], channel)
            
          elif reaction.emoji == "🇧":
              flag = check_answer(correct_answer, 'B')
              await create_embed_response(flag, response[1], channel)
            
          elif reaction.emoji == "🇨":
              flag = check_answer(correct_answer, 'C')
              await create_embed_response(flag, response[2], channel)
            
          elif reaction.emoji == "🇩":
              flag = check_answer(correct_answer, 'D')
              await create_embed_response(flag, response[3], channel)
            
          elif reaction.emoji == "🇪":
              flag = check_answer(correct_answer, 'E')
              await create_embed_response(flag, response[4], channel)
            
          else:
              await message.channel.send('What kind of answer is that ?')

          if flag == True :
            async def add_points(user):
              with open("users.json","r") as file:
                users = json.load(file)
                
                user_id = str(user.id)
                
              #adds points to existing user
              if user_id in users:
                with open("users.json","w") as file:
                  users[user_id]["Points"] += 10
                  json.dump(users, file, sort_keys=True, indent=4, ensure_ascii=False)
                  await message.channel.send('10 Points Awarded !')
                  
              #create record and then add points to new user
              else:
                with open("users.json","w") as file:
                  users = {}
                  users[user_id] = {}
                  users[user_id]["Points"] = 10
                  json.dump(users, file, sort_keys=True, indent=4, ensure_ascii=False)
                  await message.channel.send('New adventurer detected ! \nWelcome {}! Your points are now being tracked'.format(user.mention))
                  await message.channel.send('10 Points Awarded !')           
            await add_points(user)
        


  if message.content.startswith("MT Trivia"):
    await trivia_mode()

  if message.content.startswith("MT Help"):
    channel = message.channel
    await display_embed(channel)

#Function to display help menu (written in notepad, indents may cause issues)
async def display_embed(channel):
	embed = discord.Embed(
		title = 'Available Commands',
		description = 'Ver 0.1 - Trivia mode and point system ',
		colour = discord.Colour.orange()
	)

	embed.set_footer(text='In development v0.1')
	embed.set_image(url='https://media.discordapp.net/attachments/905934829659496458/920654143721467944/Mushoku_Tensei_Isekai_Ittara_Honki_Dasu_Logo_Japones.png')
	file = discord.File("thumbnail2.png")
	embed.set_thumbnail(url="attachment://thumbnail2.png")
	embed.set_author(name = 'MushokuBot Help', icon_url='https://cdn.discordapp.com/attachments/905934829659496458/920656680830791740/286158_-_Copy.jpg')
	embed.add_field(name=':scroll: MT Trivia', value = 'Start a round of Mushoku Tensei trivia !', inline = True)
	embed.add_field(name=':diamond_shape_with_a_dot_inside: MT Points', value = 'View your current MT points', inline = True)
	embed.add_field(name=':grey_question: MT Help', value = 'View all available commands', inline = False)
	
	await channel.send(file = file, embed=embed)

#Fuction to check if given response is the right answer
def check_answer(correct_answer, response):
  if response == correct_answer:
    return True

  elif isinstance(correct_answer, list) and (response in correct_answer):
    return True
          
  else:
    return False   

async def create_embed_response(correct_answer, response, channel):
  embedded = discord.Embed(title = f"{correct_answer}! {response}\n")
  await channel.send(embed = embedded)
  return
        
client.run(token)

# The following line is optional: it removes the reaction added by the user 
        #await reply.remove_reaction(reaction, user) 
                  
#@client.event
#async def on_reaction_add(reaction, user):
  #await reaction.message.channel.send(f"{user} reacted with {reaction.emoji}")
