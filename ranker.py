import math
import random
import sys
import time
import numpy as np

class competitor:
    def __init__(self, name, rating=1200, played = 0, won = 0, lost = 0):
        self.name = name
        self.rating = rating
        self.played = played
        self.won = won
        self.lost = lost

# A totally over the top method for finding a specific competitor
def levenshtein_ratio(s1, s2):
    rows = len(s1) + 1
    cols = len(s2) + 1
    dist = np.zeros((rows,cols))

    for i in range(rows):
        for j in range(cols):
            dist[i][0] = i
            dist[0][j] = j
    
    for c in range(1,cols):
        for r in range(1,rows):
            if s1[r-1] == s2[c-1]:
                cost = 0
            else: 
                cost = 2
            dist[r][c] = min(dist[r-1][c] + 1, dist[r][c-1] + 1, dist[r-1][c-1] + cost)

    ratio = ((len(s1)+len(s2)) - dist[rows-1][cols-1]) / (len(s1)+len(s2))

    return ratio

def read_data(filename):
    competitors = []
    with open(filename) as f:
        for line in f:
            dat = line.split(',')
            if len(dat) == 5:
                name = dat[0]
                rating = float(dat[1])
                played = int(dat[2])
                won = int(dat[3])
                lost = int(dat[4])
                if not (played == won + lost):
                    raise Exception("Error in input data, played should equal won + lost")    
            elif len(dat) == 4:
                name = dat[0]
                rating = float(dat[1])
                played = int(dat[2])
                won = int(dat[3])
                if not (played == won):
                    raise Exception("Error in input data, played should equal won + lost")  
            elif len(dat) == 3:
                name = dat[0]
                rating = float(dat[1])
                played = int(dat[2])
            elif len(dat) == 2:
                name = dat[0]
                rating = float(dat[1])
            elif len(dat) == 1:
                name = dat[0]
                rating = 1200
            else:
                raise Exception("Error in input data formatting")

            # Create new competitor object
            competitors.append(competitor(name, rating))
    
    return competitors

def write_data(competitors, filename):
    with open(filename, "w") as f:
        for c in competitors:
            f.write(f"{c.name.rstrip()}, {c.rating}, {c.played}, {c.won}, {c.lost}\n")


def get_pairings(competitors):
    '''
    if mode == "roundrobin":
        for pair

        sorted_played = competitors.sort(key=lambda x: x.played, reverse=True)
    '''
    a = random.randint(0,len(competitors)-1)
    b = random.randint(0,len(competitors)-1)

    return [competitors[a], competitors[b]]

def update_after_pairing(comp_a, comp_b, result):
    comp_a.played += 1
    comp_b.played += 1

    e_a = 1/(1+10**((comp_b.rating - comp_a.rating)/400))
    e_b = 1/(1+10**((comp_a.rating - comp_b.rating)/400))

    # Using USCF K-factor
    k_a = 800/comp_a.played
    k_b = 800/comp_b.played

    if result == 1:
        comp_a.won += 1
        comp_b.lost += 1
        comp_a.rating += k_a*(1 - e_a)
        comp_b.rating += k_b*(-e_b)
    if result == 2:
        comp_a.lost += 1
        comp_b.won += 1
        comp_a.rating += k_a*(-e_a)
        comp_b.rating += k_b*(1 - e_b)        

if __name__ == "__main__":
    cont = True

    competitors = read_data("competitors.txt")
    print(f"Read data ({len(competitors)} competitors) successfully.\n")

    while cont:
        print("1: View leaderboard")
        print("2: View specific competitor")
        print("3: Evaluate new pairings")
        print("4: Reset ratings")
        print("5: Exit")

        in1 = input()

        if in1 == "1":
            sorted_comps = sorted(competitors, key=lambda x: x.rating, reverse=True)
            print("\nLeaderboard")
            print("-----------------------")
            print("{:<18} | {:<6}".format("Name", "Rating"))
            print("-----------------------")
            for i in range(10):
                print("{:<18} | {:<6}".format(sorted_comps[i].name.rstrip(), str(sorted_comps[i].rating).split(".")[0]))
            print("{:<18} | {:<6}\n".format("...", "..."))
        elif in1 == "2":
            print("Enter competitor name: ")
            in2 = input()
            sorted_comps = sorted(competitors, key=lambda x: levenshtein_ratio(in2, x.name.rstrip()), reverse=True)
            if levenshtein_ratio(in2, sorted_comps[0].name.rstrip()) == 1:
                print(f"{sorted_comps[i].name.rstrip()}, {sorted_comps[i].rating}, {sorted_comps[i].played}, {sorted_comps[i].won}, {sorted_comps[i].lost}\n")            
            else:
                print("Did you mean:")
                for i in range(3):
                    print(f"{i+1}: {sorted_comps[i].name.rstrip()}")
                in3 = input()
                while in3 not in ["1","2","3"]:
                    print("Choose an option from 1 to 3...")
                    in3 = input()
                in3 = int(in3) - 1
                print(f"{sorted_comps[in3].name.rstrip()}, {sorted_comps[in3].rating}, {sorted_comps[in3].played}, {sorted_comps[in3].won}, {sorted_comps[in3].lost}\n")    

        elif in1 == "3":
            while True:
                pairing = get_pairings(competitors)
                print("PAIRING: " + pairing[0].name.rstrip() + " (" + str(pairing[0].rating).split(".")[0] + ") vs " + pairing[1].name.rstrip() + " (" + str(pairing[1].rating).split(".")[0] + ")")
                result = input()
                while result not in ["0","1","2"]:
                    print("Invalid result: enter 1 for a win for the first competitor, 2 for a win for the second competitor, or 0 to return")
                    result = input()
                if result == "0":
                    break
                elif result == "1" or result == "2":
                    update_after_pairing(pairing[0], pairing[1],int(result))
        elif in1 == "4":
            print("Are you sure? y/n")
            in2 = input()
            while in2 not in ["y", "Y", "n", "N"]:
                print("Yes (y) or no (n) answer required:")
                in2 = input()
            if in2 == "y" or in2 == "Y":
                for comp in competitors:
                    comp.rating = 1200
                    comp.played = 0
                    comp.won = 0
                    comp.lost = 0
        elif in1 == "5":
            write_data(competitors, "competitors.txt")
            print("Rating data has been saved. Exiting...")
            time.sleep(1)
            sys.exit()



