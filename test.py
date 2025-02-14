class APP():
    def __init__(self):
        super().__init__()
        self.index = 0

    def anjay(self):
        self.index += 1
    
    def output(self):
        print(self.index)

main = APP()
main.anjay()
main.anjay()
main.output()