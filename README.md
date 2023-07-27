# Cards Bot

This Python bot is designed to be used with Disnake, a __fork__ of the Discord.py library that supports Discord interactions (such as slash commands and buttons). The bot has the ability to manage a card collection, where users can interact with the bot to add, view, and claim cards.

**Note:** This bot is a work in progress and may contain bugs. Please keep this in mind when using it.

## Setup

To run the bot, you need to have Python and the Disnake library installed. Additionally, make sure you have set up a Discord bot and obtained its token.

1. Install Disnake: `pip install disnake`
2. Replace `'token_here'` with your actual Discord bot token in the last line of the code:
```python
bot.run('token_here')
```
3. Run the bot using python:
  ```
  python your_file_name.py
  ```
## Bot Features

### Slash Commands

- `/setup`: Set up the bot to receive cards in the current channel.

- `/vedirarita`: View the available rarities for cards.

- `/aggiungi`: Add a new card to the collection. Parameters: `nomecarta` (name of the card), `foto` (attachment with an image of the card), `rarita` (optional rarity of the card).

- `/prendi`: Randomly receive a card from the collection.

- `/elimina`: Delete a card from the collection. Parameters: `nomecarta` (name of the card).

- `/mycards`: View the cards you own or the cards owned by another user. Parameters: `user` (optional, specify a user to view their cards).

- `/reset_my_cards`: Reset the card collection for yourself or another user. Parameters: `user` (optional, specify a user to reset their collection).

- `/show_all_cards`: View all available cards in the collection.

### Button Interactions

The bot supports button interactions for claiming cards. When a card is spawned, users can click the "Claim" button to add the card to their collection.

## Database

The bot uses a SQLite database (`cards.db`) to store card information. The database has two tables:

1. `cards`: Stores the details of all available cards, including name, photo URL, rarity, and the channel where the card can be spawned.

2. `user_cards`: Stores the card details that users have claimed, including the user ID, card name, and card photo URL.

## Card Rarity

The cards have different rarities with associated probabilities:

- `Impossible`: 0.02
- `Leggendario`: 0.10
- `Ultra raro`: 0.20
- `Super raro`: 0.40
- `Raro`: 0.55
- `comune`: 0.80

## Known Issues

As mentioned earlier, this bot is still a work in progress, and there may be bugs or incomplete features. The developer is actively working on improving and completing the bot. If you encounter any issues or have suggestions, please feel free to report them to the bot developer.

---

Please remember that the code provided is a skeleton of a Discord bot with card collection features. You can further customize and expand the bot to suit your needs. Additionally, make sure to comply with Discord's API terms of service and guidelines while using the bot. Happy coding!
