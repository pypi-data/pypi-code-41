from timeslicer import timeslice

print("Timeslice:")
direc = input("Enter directory path to photos: ")
output = input("Enter path for output timeslicer (eg. directory_name/photo.jpg): ")
s = int(input("Enter skip value (how many photos to skip over when selecting slices): "))

r = str(input("Reverse (y/n)?"))
while r.lower() not in ['y', 'n']:
    r = input("Reverse (y/n)?")

rev = True
if r == 'n':
    rev = False

rand = str(input("Randomize (y/n)?"))
while rand.lower() not in ['y', 'n']:
    rand = input("Randomize (y/n)?")

randomize = True
if rand == 'n':
    randomize = False

q = int(input("Enter output quality (1 - 100): "))


print("")
print("Creating timeslice...")
timeslice(direc, output_path=output, skip=s, reverse=rev, randomize=randomize, qual=q)
print("Finished.")