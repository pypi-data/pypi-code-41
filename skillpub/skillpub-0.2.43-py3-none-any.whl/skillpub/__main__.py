try:
    from skillpub.manager import main as skillpub_main
except:
    print("I cant't start on your OS and Python version. Check my requirements on www.skillpub.org")

main = skillpub_main

if __name__ == '__main__':
    main()