# starts bubbles
import os


# Press the green button in the gutter to run the script.
# bubblesConfig = 'python bubbles.py -x 1000 -y 600 r -nba 20 -nbr 5'
bubblesConfig = 'python bubbles.py -x 1000 -y 600 d -file SCENE_01.csv'
# bubblesConfig = 'python bubbles.py r -nba 30 -nbr 5'
if __name__ == '__main__':
    os.system(bubblesConfig)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
