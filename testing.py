import tkinter as tk
window = tk.Tk()
window.title("my first gui with tkinter")
window.geometry("400x300")
label = tk.Label(window,text="hello guys")
label.pack()
def greet():
    print("hello hello haha")
button = tk.Button(window,text="my first button",command=greet)
button.pack()
window.mainloop()