import tkinter as tk
import random
import threading
import time
from tkinter import ttk


# Configuración de la memoria
MEMORIA_TOTAL = 1000  # Memoria total disponible (en MB)
MEMORIA_USADA = 0  # Memoria actualmente en uso (en MB)
TAMANO_PAGINA = 10  # Tamaño de cada página en MB
NUMERO_PAGINAS = MEMORIA_TOTAL // TAMANO_PAGINA  # Cantidad total de páginas en memoria
paginas_memoria = [None] * NUMERO_PAGINAS  # Tabla de páginas para la memoria

# Lista de procesos en diferentes estados
procesos = []
procesos_nuevos = []
procesos_listos = []
procesos_bloqueados = []
procesos_terminados = []
recursos_semaforos = [threading.Semaphore(1), threading.Semaphore(1), threading.Semaphore(1)]  # Semáforos para los recursos R0, R1, R2
procesos_ocupando_recurso = [None, None, None]  # Lista para rastrear qué proceso tiene cada recurso
proceso_ejecucion = None

# Clase para representar un proceso
class Proceso:
    def __init__(self, id, memoria):
        self.id = id
        self.memoria = memoria
        self.estado = 'Nuevos'
        self.veces_bloqueado = 0
        self.recurso = random.randint(0, 2)  # Asigna aleatoriamente R0, R1 o R2
        self.paginas = []  # Páginas asignadas en la memoria principal
        self.tiene_recurso = False

    def __str__(self):
        return f"P{self.id}: ({self.memoria} MB) Recurso: R{self.recurso}"

# Función para mover un proceso de Listo a Ejecutando
def mover_a_ejecutando():
    global proceso_ejecucion
    while True:
        if not proceso_ejecucion and procesos_listos:
            proceso = procesos_listos.pop(0)
            proceso_ejecucion = proceso
            proceso.estado = 'Ejecutando'
            actualizar_interfaz()

            if not proceso.tiene_recurso:
                if recursos_semaforos[proceso.recurso].acquire(blocking=False):
                    proceso.tiene_recurso = True
                    procesos_ocupando_recurso[proceso.recurso] = proceso.id
                    actualizar_interfaz()
                    time.sleep(1)

            time.sleep(2)
            
            if proceso.veces_bloqueado < 3:
                proceso.veces_bloqueado += 1
                proceso.estado = 'Bloqueado'
                procesos_bloqueados.append(proceso)
            else:
                proceso.estado = 'Terminado'
                procesos_terminados.append(proceso)
                liberar_paginas(proceso)
                liberar_recurso(proceso)

            proceso_ejecucion = None
            actualizar_interfaz()

        time.sleep(2)

# Función para revisar procesos bloqueados
def revisar_procesos_bloqueados():
    while True:
        for proceso in procesos_bloqueados[:]:
            if proceso.tiene_recurso:
                time.sleep(3)
                proceso.estado = 'Listo'
                procesos_bloqueados.remove(proceso)
                procesos_listos.append(proceso)
                actualizar_interfaz()
            else:
                if recursos_semaforos[proceso.recurso].acquire(blocking=False):
                    proceso.tiene_recurso = True
                    procesos_ocupando_recurso[proceso.recurso] = proceso.id
                    proceso.estado = 'Listo'
                    procesos_bloqueados.remove(proceso)
                    procesos_listos.append(proceso)
                    actualizar_interfaz()

        time.sleep(2)

# Función para liberar el recurso asignado a un proceso
def liberar_recurso(proceso):
    if proceso.tiene_recurso:
        recursos_semaforos[proceso.recurso].release()
        procesos_ocupando_recurso[proceso.recurso] = None
        proceso.tiene_recurso = False
        actualizar_interfaz()

# Función para asignar páginas a un proceso
def asignar_paginas(proceso):
    global MEMORIA_USADA
    paginas_necesarias = (proceso.memoria + TAMANO_PAGINA - 1) // TAMANO_PAGINA

    if paginas_memoria.count(None) >= paginas_necesarias:
        for i in range(NUMERO_PAGINAS):
            if len(proceso.paginas) == paginas_necesarias:
                break
            if paginas_memoria[i] is None:
                paginas_memoria[i] = proceso.id
                proceso.paginas.append(i)
                MEMORIA_USADA += TAMANO_PAGINA

        return True
    else:
        return False

# Función para liberar las páginas asignadas a un proceso
def liberar_paginas(proceso):
    global MEMORIA_USADA
    for pagina in proceso.paginas:
        paginas_memoria[pagina] = None
        MEMORIA_USADA -= TAMANO_PAGINA
    proceso.paginas = []

# Función para agregar un proceso
def agregar_proceso(memoria_necesaria):
    proceso = Proceso(len(procesos) + 1, memoria_necesaria)
    procesos_nuevos.append(proceso)
    proceso.estado = 'Listos'
    procesos.append(proceso)
    actualizar_interfaz()

# Función para mover procesos de Nuevos a Listos
def nuevo_a_listo():
    while True:
        for proceso in procesos_nuevos[:]:
            if asignar_paginas(proceso):
                procesos_nuevos.remove(proceso)
                procesos_listos.append(proceso)
                proceso.estado = 'Listo'
                actualizar_interfaz()
        time.sleep(3)

# Función para agregar un proceso manualmente
def agregar_proceso_manual():
    try:
        memoria_necesaria = int(memoria_entry.get())
        if memoria_necesaria > 0:
            agregar_proceso(memoria_necesaria)
        else:
            tk.messagebox.showerror("Error", "La memoria debe ser un número positivo.")
    except ValueError:
        tk.messagebox.showerror("Error", "Ingrese un valor numérico válido para la memoria.")
    finally:
        memoria_entry.delete(0, tk.END)

# Función para agregar un proceso aleatorio
def agregar_proceso_aleatorio():
    memoria_necesaria = random.randint(50, 200)
    agregar_proceso(memoria_necesaria)

# Función para actualizar la interfaz gráfica
def actualizar_interfaz():
    memoria_label.config(text=f"Memoria Usada: {MEMORIA_USADA}/{MEMORIA_TOTAL} MB")
    ejecucion_label.config(text=f"Ejecutando: {proceso_ejecucion if proceso_ejecucion else 'Ninguno'}")

    # Limpiar y actualizar lista de procesos
    nuevos_listbox.delete(0, tk.END)
    for p in procesos_nuevos:
        nuevos_listbox.insert(tk.END, str(p))

    listos_listbox.delete(0, tk.END)
    for p in procesos_listos:
        listos_listbox.insert(tk.END, str(p))

    bloqueados_listbox.delete(0, tk.END)
    for p in procesos_bloqueados:
        bloqueados_listbox.insert(tk.END, str(p))

    terminados_listbox.delete(0, tk.END)
    for p in procesos_terminados:
        terminados_listbox.insert(tk.END, str(p))

    mensaje_error.config(text="")

    # Mostrar procesos en memoria
    mostrar_procesos_en_memoria()

    # Actualizar estado de los recursos
    actualizar_estado_recursos()

    #Actualizar tabla de paginacion
    actualizar_tabla_paginacion()


def actualizar_tabla_paginacion():
    # Limpiar la tabla antes de actualizarla
    for item in tabla_paginacion.get_children():
        tabla_paginacion.delete(item)
    
    # Añadir las filas con la información de la paginación
    for marco, proceso_id in enumerate(paginas_memoria):
        if proceso_id is not None:
            tabla_paginacion.insert("", "end", values=(marco, marco, proceso_id))


# Función para mostrar visualmente el uso de la memoria
# Función para mostrar visualmente el uso de la memoria
# Función para mostrar visualmente el uso de la memoria
# Función para mostrar visualmente el uso de la memoria
def mostrar_procesos_en_memoria():
    canvas.delete("all")  # Limpiar el canvas

    ancho_columna = 5  # Ancho de las columnas
    colores_procesos = ["lightblue", "lightgreen", "lightcoral", "lightyellow", "lightpink"]  # Lista de colores

    # Variables para mantener el seguimiento de los procesos ya dibujados
    procesos_dibujados = set()

    for i in range(NUMERO_PAGINAS):
        x0, y0 = (i * ancho_columna), 0  # Cada página se dibuja en la posición correspondiente
        x1, y1 = x0 + ancho_columna, 100  # Altura fija para las páginas

        if paginas_memoria[i]:
            # Obtener el color basado en el ID del proceso
            color = colores_procesos[paginas_memoria[i] % len(colores_procesos)]
            canvas.create_rectangle(x0, y0, x1, y1, fill=color)

    # Dibuja la línea fina debajo del rectángulo grande
    y_fino0 = 110
    y_fino1 = 115  # Ancho muy fino de 5 píxeles

    i = 0
    while i < NUMERO_PAGINAS:
        if paginas_memoria[i]:
            proceso_id = paginas_memoria[i]
            if proceso_id not in procesos_dibujados:
                procesos_dibujados.add(proceso_id)

                # Encuentra el rango de páginas ocupadas por el mismo proceso
                inicio = i
                while i < NUMERO_PAGINAS and paginas_memoria[i] == proceso_id:
                    i += 1
                fin = i

                # Dibujar el rectángulo para toda la sección del proceso
                x0, x1 = (inicio * ancho_columna), (fin * ancho_columna)
                color = colores_procesos[proceso_id % len(colores_procesos)]
                canvas.create_rectangle(x0, y_fino0, x1, y_fino1, fill=color, outline=color)  # Sin divisiones visibles

                # Dibujar el número del proceso centrado
                canvas.create_text((x0 + (x1 - x0) / 2, (y_fino0 + y_fino1) / 2), text=f"P{proceso_id}", anchor='center', font=("Arial", 8))

        else:
            i += 1  # Si no hay proceso en esa página, avanzar





# Función para actualizar el estado de los recursos
def actualizar_estado_recursos():
    for i, recurso in enumerate(["R0", "R1", "R2"]):
        estado = f"{recurso}: {'Libre' if procesos_ocupando_recurso[i] is None else f'Ocupado por P{procesos_ocupando_recurso[i]}' }"
        estado_recursos_label[i].config(text=estado)

# Configuración de la interfaz gráfica
root = tk.Tk()
root.title("Simulador de Gestión de Procesos y Memoria (PAGINACIÓN)")

# Frame principal
frame_principal = tk.Frame(root)
frame_principal.pack(padx=10, pady=10)

# Sección de memoria usada
memoria_label = tk.Label(frame_principal, text=f"Memoria Usada: {MEMORIA_USADA}/{MEMORIA_TOTAL} MB", font=("Arial", 14))
memoria_label.pack()

# Frame para el canvas de memoria
canvas_frame = tk.Frame(frame_principal)
canvas_frame.pack(pady=10)

canvas = tk.Canvas(canvas_frame, width=500, height=125, bg="white")
canvas.pack()

# Sección de ejecución
ejecucion_label = tk.Label(frame_principal, text=f"Ejecutando: Ninguno", font=("Arial", 14))
ejecucion_label.pack()

#//
# Frame para la entrada de memoria y botones
control_frame = tk.Frame(frame_principal)
control_frame.pack(pady=10)

memoria_entry = tk.Entry(control_frame)
memoria_entry.pack(side=tk.LEFT, padx=(0, 5))

agregar_btn = tk.Button(control_frame, text="Agregar Proceso", command=agregar_proceso_manual)
agregar_btn.pack(side=tk.LEFT, padx=(5, 0))

agregar_aleatorio_btn = tk.Button(control_frame, text="Agregar Proceso Aleatorio", command=agregar_proceso_aleatorio)
agregar_aleatorio_btn.pack(side=tk.LEFT, padx=(5, 0))
#//


# Listas de procesos
nuevos_frame = tk.Frame(frame_principal)
nuevos_frame.pack(side=tk.LEFT, padx=(10, 5))

listos_frame = tk.Frame(frame_principal)
listos_frame.pack(side=tk.LEFT, padx=(5, 5))

bloqueados_frame = tk.Frame(frame_principal)
bloqueados_frame.pack(side=tk.LEFT, padx=(5, 5))

terminados_frame = tk.Frame(frame_principal)
terminados_frame.pack(side=tk.LEFT, padx=(5, 10))

nuevos_label = tk.Label(nuevos_frame, text="Procesos Nuevos", font=("Arial", 12))
nuevos_label.pack()
nuevos_listbox = tk.Listbox(nuevos_frame, width=30, height=10)
nuevos_listbox.pack()

listos_label = tk.Label(listos_frame, text="Procesos Listos", font=("Arial", 12))
listos_label.pack()
listos_listbox = tk.Listbox(listos_frame, width=30, height=10)
listos_listbox.pack()

bloqueados_label = tk.Label(bloqueados_frame, text="Procesos Bloqueados", font=("Arial", 12))
bloqueados_label.pack()
bloqueados_listbox = tk.Listbox(bloqueados_frame, width=30, height=10)
bloqueados_listbox.pack()

terminados_label = tk.Label(terminados_frame, text="Procesos Terminados", font=("Arial", 12))
terminados_label.pack()
terminados_listbox = tk.Listbox(terminados_frame, width=30, height=10)
terminados_listbox.pack()

# Frame para los recursos
recursos_frame = tk.Frame(frame_principal)
recursos_frame.pack(pady=10)

estado_recursos_label = tk.Label(recursos_frame, text="Estado de Recursos", font=("Arial", 12))
estado_recursos_label.pack()

estado_recursos_label = []
for i in range(3):
    estado_label = tk.Label(recursos_frame, text=f"R{i}: Libre", font=("Arial", 12))
    estado_label.pack()
    estado_recursos_label.append(estado_label)

# Mensaje de error
mensaje_error = tk.Label(frame_principal, text="", fg="red", font=("Arial", 10))
mensaje_error.pack()

# Crear el Treeview para la tabla de paginación
tabla_paginacion = ttk.Treeview(root, columns=("Pagina", "Marco", "Proceso"), show="headings", height=10)
tabla_paginacion.heading("Pagina", text="Página")
tabla_paginacion.heading("Marco", text="Marco de Memoria")
tabla_paginacion.heading("Proceso", text="ID del Proceso")
tabla_paginacion.pack()


# Hilos para el manejo de procesos
threading.Thread(target=nuevo_a_listo, daemon=True).start()
threading.Thread(target=mover_a_ejecutando, daemon=True).start()
threading.Thread(target=revisar_procesos_bloqueados, daemon=True).start()

# Iniciar la interfaz gráfica
root.mainloop()
