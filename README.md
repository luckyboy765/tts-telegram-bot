# Crossword (TTS) Telegram Bot

A group game bot that plays Indonesian crossword puzzles (*Teka-Teki Silang*)
inside a Telegram chat. Every game builds a **new random board** from the word
bank, and the board image is redrawn after each correct answer.

Built with **Python, Pyrogram, Pillow and SQLite**.

## Features

- **Board generator**: places words so they cross each other, different every game
- **3 difficulty modes**: Easy (6 words), Normal (9), Hard (13), each with its own word bank
- **Rendered board image** (Pillow): letters fill in as players answer, the latest
  word is highlighted
- **Forgiving answer parser**: `3. gula`, `3.gula`, `3 gula` and `3gula` all work;
  one number can be both Across and Down, both are checked
- **Scoring**: longer words give more points (10 × letters)
- **Leaderboards**: all-time and weekly, plus personal stats
- Auto-ends idle games and reveals the answers

## Commands

| Command | Action |
|---|---|
| `/new` | Start a game and pick a mode |
| `/stop` | End the game and reveal all answers |
| `/peringkat` | Leaderboard (`/peringkat mingguan` for weekly) |
| `/stats` | Personal stats |
| `/soal` | Size of the word bank |
| `/help` | How to play |

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env      # fill API_ID, API_HASH, BOT_TOKEN
python main.py
```

`API_ID` and `API_HASH` come from https://my.telegram.org, `BOT_TOKEN` from @BotFather.

## Adding words

Add a line to the `WORDS` list in `words.py`:

```python
("JAWABAN", "clue text", "easy"),   # level: easy | normal | hard
```

Answers must be one word, letters A–Z only, so they can cross on the board.

## Project structure

```
main.py        Pyrogram bot, commands and answer handling
generator.py   crossword layout algorithm
renderer.py    board image drawing (Pillow)
game.py        game state, answer parser, scoring
words.py       word bank
build_bank.py  builds the per-level word files in data/
stats.py       scores and leaderboards (SQLite)
```
