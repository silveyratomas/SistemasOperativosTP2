import tkinter as tk
import subprocess

# Funciones para ejecutar los archivos
def ejecutar_compactacion():
    subprocess.run(["python", "compactacion.py"])

def ejecutar_paginacion():
    subprocess.run(["python", "paginacion.py"])

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("TP2 Sistemas Operativos")
ventana.geometry("400x300")

# Crear el título principal
titulo_label = tk.Label(ventana, text="TP2 Sistemas Operativos", font=("Helvetica", 16, "bold"))
titulo_label.pack(pady=10)

# Crear subtítulo con los nombres
autores_label = tk.Label(ventana, text="Autores: Silveyra Tomás, Waniukiewicz Nicolas, Stupniki Hernan", font=("Helvetica", 12))
autores_label.pack(pady=5)

# Crear botones
boton_compactacion = tk.Button(ventana, text="Compactación", command=ejecutar_compactacion, width=20, height=2, bg="lightblue")
boton_compactacion.pack(pady=10)

boton_paginacion = tk.Button(ventana, text="Paginación", command=ejecutar_paginacion, width=20, height=2, bg="lightgreen")
boton_paginacion.pack(pady=10)

# Iniciar el bucle de la ventana
ventana.mainloop()
