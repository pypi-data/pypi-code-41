from smockrawl.smockrawl import Smockeo

def main():
    print("smockrawl - Smockeo crawler - CLI example")
    username = input("Smockeo username: ")
    password = input("Smockeo password: ")
    detectorId = input("Smockeo detector ID: ")
    smo = Smockeo(username, password, detectorId)
    smo.authenticate()
    smo.poll()
    smo.print_status()

if __name__ == "__main__":
    main()