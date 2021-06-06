# Meme Maker Discord Bot

## Setup

### Downloading bot
`$ git clone https://github.com/aryamaanthakur/meme-maker-discord-bot.git`

`$ cd meme-maker-discord-bot`

`$ pip3 install -r requirements.txt`

### Setting up credentials

Create an account on [**imgflip**](https://imgflip.com).

Open `config.json` and change the username and password to the account you just made.

Change the **TOKEN** to that of your bot. (See the bottom if you're doing this for the first time)

### Running the bot
Run bot.py (`python3 bot.py`)


## Usage

### `~memehelp`
Display the list of commands and their usage.

### `~templates`
Display the list of 100 templates (25 on each page). Use the arrows/number emojis to navigate between pages.

### `~memeinfo id`
Display the usage of the meme corresponding to `id` in the template list.

### `~examplememe id`
Display the top meme example corresponding to `id`.  
Alias = `memeexample`

### `~makememe id "text0" "text1"`
This will generate the meme with captions provided. Use "" to leave a caption blank. A user can save the meme by cliking on the ⭐ reaction.

### `~mymemes`
Display the list of memes you've created.  
Use `~mymemes id` to show a meme.  
Alias = `mymeme`

### `~showmemes @user`
Display the memes created by @user.  
Use `~showmemes @user id` to show a particular meme.  
Use `~showmemes` to display your memes.  
Alias = `showmeme`

### `~myfavmemes`
Display the list of memes you've saved.  
Use `~myfavmemes id` to show a meme.  
Alias = `myfavmeme`

### `~favmemes @user`
Display the memes saved by @user.  
Use `~favmemes @user id` to show a particular meme.  
Alias = `favmeme`

## Creating a discord bot (For those who are unfamiliar)
Goto [https://discord.com/developers/applications](https://discord.com/developers/applications) and create a new application

In the **Bot** section click on **Add Bot**

Copy the **TOKEN** and paste it in your `config.json` file.

### Add bot to your server
In the OAuth2 section check **bot** in scopes and check `Administrator` in bot permissions.

Click on the copy button below scope options.

This link will be used to invite bot in your server.
