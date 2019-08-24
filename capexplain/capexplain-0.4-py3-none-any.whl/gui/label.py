import Tkinter as tk


def DarkenLabel():
    label.config(bg="gray")

root = tk.Tk()
app = tk.Frame(root)
app.pack()

label = tk.Label(app, bg="green", pady=5, font=(None, 1), height=5, width=20)
# checkbox = tk.Checkbutton(app, bg="white", command=DarkenLabel)
label.grid(row=0, column=0, sticky="ew")
# checkbox.grid(row=0, column=0, sticky="w")
root.mainloop()