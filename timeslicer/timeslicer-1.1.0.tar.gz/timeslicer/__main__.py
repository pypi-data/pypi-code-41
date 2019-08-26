from timeslicer import timeslice

print("Timeslice:")
direc = input("Enter directory path to photos: ")
output = input("Enter path for output timeslicer (eg. directory_name/photo.jpg): ")
s = int(input("Enter skip value (how many photos to skip over when selecting slices): "))
q = int(input("Enter output quality (1 - 100): "))

print("")
print("Creating timeslicer...")
timeslice(direc, output_path=output, skip=s, qual=q)
print("Finished.")