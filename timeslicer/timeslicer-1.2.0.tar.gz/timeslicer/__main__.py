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

q = int(input("Enter output quality (1 - 100): "))


print("")
print("Creating timeslice...")
timeslice(direc, output_path=output, skip=s, reverse=rev, qual=q)
print("Finished.")