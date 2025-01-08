# Hold Your Gun Steady

**Hold Your Gun Steady** is a reflex training game developed in Python using the Pygame library. In this game, you will test your accuracy and reaction time by shooting colorful balls that spawn at random positions. As you progress, the difficulty will increase, and you will have to be quick and precise to score points and avoid penalties.

## Features

- **Multiple Difficulty Levels**: Choose between Easy, Normal, or Hard difficulty settings, each with different spawn rates, ball speeds, and score multipliers.
- **Real-Time Gameplay**: Balls appear and shrink over time, and the player must click on them to explode them and earn points.
- **Combo System**: Score multipliers for consecutive hits, encouraging players to chain combos.
- **Sound Effects**: Realistic sound effects for both hitting and missing balls.
- **Highscore Tracking**: Keep track of your highest scores locally and see your progress over time.
- **Pause & Resume**: Pause the game at any time and resume without losing your current progress.
- **Game Records**: After each session, your game performance (score, accuracy, combo, etc.) will be saved to a text file for future reference.

## Installation

### Requirements

- Python 3.x
- Pygame 2.x

To install the required libraries, run:

```bash
pip install pygame
```

### Clone the Repository

You can clone this repository to your local machine using Git:

```bash
git clone https://github.com/CNMengHan/HoldyourGunsteady.git
cd HoldyourGunsteady
```

## Running the Game

Once you have installed the required dependencies and cloned the repository, you can run the game by executing the following command in your terminal:

```bash
python game.py
```

This will launch the game window where you can play the game.

## Controls

- **Mouse Click**: Shoot at the balls that appear on the screen. If you hit a ball, it will explode, and you will gain points. If you miss, your score will decrease.
- **Esc**: Pause or resume the game.
- **Q**: Quit to the main menu during the game or pause screen.

## Difficulty Levels

- **Easy**: Slow ball speed, longer ball spawn interval, lower score multiplier.
- **Normal**: Moderate ball speed and spawn interval, average score multiplier.
- **Hard**: Fast ball speed, short spawn interval, high score multiplier.

## Game Over and Scoring

At the end of the game, your score, highest combo, and accuracy are displayed. Scores are saved automatically to a file (`game_records.txt`), and the highest score is tracked in a JSON file (`highscore.json`).

### Scoring System

- Balls spawn with random point values (1-3 points).
- Points are multiplied based on the selected difficulty level.
- Missing a ball or failing to click before it disappears results in a score penalty.
- Combo streaks increase your score multiplier for consecutive hits.

## High Scores

Your highest score is saved in a file called `highscore.json`, and you can see it in the main menu. Every game session's performance is saved in `game_records.txt` for your review.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Credits

- Developed by [CNMengHan](https://github.com/CNMengHan).
- Powered by [Pygame](https://www.pygame.org/).
