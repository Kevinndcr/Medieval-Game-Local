# Medieval Fighting Game - Multiplayer Edition

A 2D medieval-themed fighting game with local and network multiplayer support.

## Features

- Epic medieval-themed combat with swords and shields
- Beautiful coliseum background
- Exciting gameplay mechanics including clashing swords and battle minigames
- Network multiplayer support for playing with friends on the same network
- Special effects including blood, hit effects, and swing effects

## How to Play

### Controls

**Player 1 (Host):**
- Movement: W, A, S, D
- Attack: Spacebar
- Guard: G

**Player 2 (Client):**
- Movement: W, A, S, D
- Attack: Spacebar
- Guard: G

### Multiplayer Instructions

1. **To Host a Game:**
   - Launch the game
   - Click "Host Game"
   - Share your IP address (displayed on screen) with your friend
   - Wait for your friend to connect
   - Once connected, the game will start automatically

2. **To Join a Game:**
   - Launch the game
   - Click "Join Game"
   - Enter the IP address of the host
   - Click "Connect" or press Enter
   - Once connected, the game will start automatically

**Note:** Both players must be on the same network for multiplayer to work.

## Requirements

- Python 3.6+
- Pygame 2.5.2+
- Both computers must be on the same network for multiplayer

## Installation

1. Make sure you have Python installed
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the game:
   ```
   python main.py
   ```

## Troubleshooting

- If you're having connection issues, ensure both computers are on the same network
- Check that your firewall is not blocking the game (port 5555)
- Verify that the IP address is entered correctly when joining a game
