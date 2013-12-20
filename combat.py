class Character:
    def __init__(self, name):
        self.name = name
        self.hp = 20
        self.mana = 30
        self.magic = 5
        self.defense = 5
        self.speed = 1

        self.effects = {}

    def __repr__(self):
        return self.name

    def apply_effect(effect):
        if effect.type in self.effects and self.effect[effect.type].value > effect.value:
            print("Stronger effect for %s already exists on %s" % (effect.type, self.name))

        self.effects[effect.type] = effect
        effect.apply(self)

class Encounter:
    def __init__(self, participants):
        self.participants = participants
        for i in self.participants:
            i.atb = 0

    def tick(self):
        for i in self.participants:
            i.atb += i.speed

            if i.atb >= 10:
                self.do_turn(i)
                i.atb -= 10

    def do_turn(self, ch):
        print("%s's turn!" % (ch,))

        # Tick any active effects
        for fxtype, fx in ch.effects.items():
            fx.tick(ch)
            fx.duration -= 1

        # Remove any completed effects
        for fx in [i for i in ch.effects.values() if i.duration <= 0]:
            del ch.effects[fx.type]

        # Display options
        option = 0
        while option < 1:
            print("Options:")
            print("\t1. Attack")
 
            inp = input("Enter option: ")
            try:
                option = int(inp)
            except ValueError:
                option = 0
            if option not in (1,):
                option = 0
                print("Invalid option")
   
        if option == 1:
            targets = self.participants[:]
            targets.remove(ch)

            target = None
            while target is None:
                print("Attacking, pick a target:")
                for idx, i in enumerate(targets):
                    print("\t", idx, i)
                
                tidx = input("Target: ")
                try:
                    tidx = int(tidx)
                except ValueError:
                    tidx = -1
                if 0 < tidx < len(targets) - 1:
                    print("Invalid target")
                else:
                    target = targets[tidx]

            print("Attacking", target)
        print()

if __name__ == '__main__':
    participants = [
            Character("Foo"),
            Character("Bar"),
        ]

    e = Encounter(participants)
    while e.participants:
        e.tick()

    print("Encounter done!")
