import pygame
import sys
from network import Network
from main import Player, Background, Button, ClashBattle, draw_game_over, draw_round_over
from assets.sound_manager import SoundManager

# Initialize Pygame
pygame.init()

# Set up the display
width = 1000
height = 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Sword Clash - Network Game")

# Initialize game components
background = Background()
sound_manager = SoundManager()

def main(host='localhost'):
    # Network setup
    network = Network(host)
    if not network.connect():
        print("Could not connect to server!")
        return

    # Game state
    clock = pygame.time.Clock()
    running = True
    game_state = PLAYING = 0
    GAME_OVER = 1
    ROUND_OVER = 2

    # Create local player (position will be updated by server)
    player1 = Player(100, 300, "Player 1", pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d, 
                    pygame.K_SPACE, pygame.K_g)
    player2 = Player(700, 300, "Player 2", pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, 
                    pygame.K_RIGHT, pygame.K_RETURN, pygame.K_n)

    clash_battle = None

    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and (game_state == GAME_OVER or game_state == ROUND_OVER):
                    game_state = PLAYING

        # Update local player
        keys = pygame.key.get_pressed()
        player1.update(keys, player2)

        # Send local player state and get game state from server
        player_data = {
            'x': player1.x,
            'y': player1.y,
            'attacking': player1.is_attacking,
            'health': player1.health
        }
        game_state_data = network.send(player_data)

        if game_state_data:
            # Update other player's state
            player2.x = game_state_data['player2']['x']
            player2.y = game_state_data['player2']['y']
            player2.is_attacking = game_state_data['player2']['attacking']
            player2.health = game_state_data['player2']['health']

            # Handle clash battle state
            if game_state_data['clash_battle'] and not clash_battle:
                clash_battle = ClashBattle(player1, player2)
            elif not game_state_data['clash_battle']:
                clash_battle = None

        # Draw everything
        background.draw(screen)
        player1.draw(screen)
        player2.draw(screen)

        if clash_battle:
            clash_battle.update(keys)
            clash_battle.draw(screen)

        # Draw UI
        if game_state == GAME_OVER:
            winner = "Player 1" if player2.health <= 0 else "Player 2"
            draw_game_over(screen, winner)
        elif game_state == ROUND_OVER:
            winner = "Player 1" if player2.health <= 0 else "Player 2"
            draw_round_over(screen, winner)

        pygame.display.flip()
        clock.tick(60)

    network.close()
    pygame.quit()

if __name__ == "__main__":
    # Get server IP from command line argument or use default
    host = sys.argv[1] if len(sys.argv) > 1 else 'localhost'
    main(host)
