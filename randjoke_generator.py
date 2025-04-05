import random
import json

def get_randomjoke():
    with open('random_jokes.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
        random_joke = random.choice(data)
        return random_joke