import customtkinter as ctk

# Mengatur tema dan tampilan
ctk.set_appearance_mode("Dark")  # "Light" atau "Dark"
ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue", dll.

# Membuat jendela utama
root = ctk.CTk()

# Mengatur judul dan ukuran jendela
root.title("CustomTkinter App")
root.geometry("400x300")

# Membuat label
label = ctk.CTkLabel(root, text="Hello, CustomTkinter!", font=("Arial", 20))
label.pack(pady=20)

# Fungsi untuk menambahkan tombol baru
def button_click():
    label.config(text="Button Clicked!")
    # Membuat tombol baru setelah tombol pertama diklik
    new_button = ctk.CTkButton(root, text="New Button", command=button_click)
    new_button.pack(pady=10)

# Membuat tombol pertama
button = ctk.CTkButton(root, text="Click Me", command=button_click)
button.pack(pady=10)

# Menjalankan aplikasi
root.mainloop()
