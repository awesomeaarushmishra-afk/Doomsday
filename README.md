# DOOMSDAY

A retro first-person shooter built in Python with Pygame — raycasted walls, real enemies with pathfinding, interactive doors and elevators, a level progression system, and a full options menu with rebindable controls.

Forked from [Umang-Lodaya/Doom-PyGame](https://github.com/Umang-Lodaya/Doom-PyGame), which provided the original raycasting renderer, wall/sprite projection, and base NPC pathfinding. Everything under **Features** below was built on top of that foundation.

## Features

### Core Gameplay
- Raycasted 3D engine with textured walls, animated sprites, and a shotgun with hit detection
- Enemies (Soldier, Caco Demon, Cyber Demon) with BFS pathfinding and line-of-sight targeting
- Lives & health system with a heartbar HUD and a proper game-over flow
- **Level progression** — clearing a level's enemies advances you through a sequence of map layouts (rotated/mirrored variants of a base map), with enemy count scaling per level

### Main Menu & Options (v0.2)
- Full title screen with New Game / Options / Quit
- **Options menu**: adjustable mouse sensitivity, music volume, and FOV (60–110°) via sliders
- **Rebindable controls**: forward/backward/strafe, interact, cheat menu, and minimap toggle can all be reassigned to any key
- Settings persist across sessions in `user_settings.json`

### Interactive World (v0.2)
- **Doors** — walk up and press **E** to open/close; auto-closes after a delay
- **Elevators** — walkable floor tiles that transport you between points on the map
- **Minimap** — press **Tab** to toggle a top-down overlay showing walls, doors (color-coded open/closed), and elevators, with your position and facing direction

### Extras
- Custom bitmap font renderer (`doom_font.py`) using individual letter textures instead of a system font
- In-game music player: playlist scanning, next-track, volume control, shuffle/repeat, with a "Now Playing" HUD
- Cheat console (press **C**): `IDDQD` (godmode), `IDKFA` (all weapons/ammo), `GM` (noclip), `MAXHEALTH`, `KILLALL`, `MURDERER` (NPC friendly fire), `I'M DONE` (unlocks a secret developer room), `HELP`
- Hidden developer room easter egg — a browsable image gallery unlocked via the cheat console
- Resizable window with a fixed internal render resolution, scaled cleanly to any window size
- Packaged as a standalone Windows executable via PyInstaller

## Requirements

- Python 3.x
- Pygame (`pip install pygame`)

## Getting Started

### Run from source
```bash
git clone https://github.com/awesomeaarushmishra-afk/Doomsday.git
cd Doomsday
pip install -r requirements.txt
python main.py
```

### Or download the executable
Check the [Releases](../../releases) page for a standalone Windows build — no Python installation required.

## Controls

| Action | Key |
|---|---|
| Move | `W` `A` `S` `D` *(rebindable)* |
| Look | Mouse |
| Shoot | Left Mouse Button |
| Interact (doors/elevators) | `E` *(rebindable)* |
| Toggle Minimap | `Tab` *(rebindable)* |
| Open Cheat Console | `C` *(rebindable)* |
| Music: Next Track | `Right Arrow` |
| Music: Volume Up/Down | `Up` / `Down Arrow` |
| Music: Pause/Resume | `Ctrl + Space` |
| Quit | `Esc` |

All keybinds can be changed in **Options → Rebind Keys**.

## Building the Executable

This project uses PyInstaller with a prepared spec file:

```bash
pip install pyinstaller
pyinstaller doomsday.spec
```

The built executable will appear in the `dist/` folder. Asset paths are resolved via `utils.py`'s `resource_path()` helper, so the game works identically whether run from source or as a frozen executable.

## Credits

- Original raycasting engine and base game: [Umang-Lodaya/Doom-PyGame](https://github.com/Umang-Lodaya/Doom-PyGame)
- All features listed above under "Features": this fork

## Contributing

Found a bug or have a suggestion? Feel free to open an issue.
