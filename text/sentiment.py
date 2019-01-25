import random


def analyse_sentiment(text):
    output = random.choices(population=[-1,0,1], weights=[.1, .7, .2], k=1)[0]
    return output


class SentimentCounter:
    def __init__(self):
        self.counter = {"pos": 0,
                        "neg": 0,
                        "neu": 0
                        }

        self.counter_popular = {"pos": 0,
                            "neg": 0,
                            "neu": 0
                            }
    
    def choose_counter(self, is_popular):
        if is_popular:
            return self.counter_popular
        return self.counter

    def update(self, value, is_popular):
        counter = self.choose_counter(is_popular)
        if value == 0:
            counter["neu"]+=1
        elif value == 1:
            counter["pos"]+=1
        elif value == -1:
            counter["neg"]+=1
        else:
            raise ValueError("Invalid sentiment value, must be one of [-1, 0, 1]")
