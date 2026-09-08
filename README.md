# DOOMSDAY

A retro first-person shooter built in Python with Pygame. It combines the fast-paced action of classic 90s FPS games with a set of custom-built quality-of-life and gameplay features on top of a raycasting engine base.

Forked from [Umang-Lodaya/Doom-PyGame](https://github.com/Umang-Lodaya/Doom-PyGame), which provided the original raycasting renderer, wall/sprite projection, and base NPC pathfinding. Everything listed below under **Features I Added** was built on top of that foundation.

## Features I Added

- **Main Menu** — a full title screen with New Game / Options / Quit, arrow-key navigation, custom background and title art, and an animated selector arrow.
- **Custom Bitmap Font Renderer** (`doom_font.py`) — renders text using individual letter textures instead of a system font, with automatic fallback glyphs and color tinting.
- **Music Player** (`music_player.py`) — scans a `music/` folder, supports next-track, shuffle, repeat, volume control, and play/pause, with a live "Now Playing" HUD in-game.
- **Lives & Game Over System** — the player now has multiple lives, a heartbar HUD, and a proper game-over screen with a timed return to the main menu instead of freezing the game.
- **Win State** — clearing all enemies triggers a win screen with an automatic return to the main menu.
- **Cheat Console** — press `C` in-game to open a Doom-style command console. Supports:
  - `IDDQD` — Godmode
  - `IDKFA` — All weapons & ammo
  - `GM` — Noclip
  - `MAXHEALTH` — Full heal
  - `KILLALL` — Instantly clears all enemies
  - `MURDERER` — Toggles NPC friendly fire (enemies turn on each other)
  - `I'M DONE` — Unlocks a secret developer room
  - `HELP` — Lists all cheats
- **Developer Room Easter Egg** (`developer_room.py`) — a hidden image gallery unlocked via the cheat console, browsable with the arrow keys.
- **NPC Infighting** — enemies can now target and attack each other (not just the player) when friendly fire is toggled on, using a generalized line-of-sight targeting system.
- **Resizable Window** — gameplay renders internally at a fixed resolution and scales cleanly to any window size, instead of being locked to one fixed resolution.

## Requirements

- Python 3.x
- Pygame (`pip install pygame`)

## Getting Started

```bash
git clone https://github.com/awesomeaarushmishra-afk/Doomsday.git
cd Doomsday
pip install -r requirements.txt
python main.py
```

## Controls

| Action | Key |
|---|---|
| Move | `W` `A` `S` `D` |
| Look | Mouse |
| Shoot | Left Mouse Button |
| Open Cheat Console | `C` |
| Music: Next Track | `Right Arrow` |
| Music: Volume Up/Down | `Up` / `Down Arrow` |
| Music: Pause/Resume | `Ctrl + Space` |
| Quit | `Esc` |

## Credits

- Original raycasting engine and base game: [Umang-Lodaya/Doom-PyGame](https://github.com/Umang-Lodaya/Doom-PyGame)
- All features listed above under "Features I Added": this fork

## Contributing

Found a bug or have a suggestion? Feel free to open an issue.
