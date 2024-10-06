import tkinter as tk
from tkinter import messagebox, ttk
import random
import threading
import time
from queue import Queue

class SimuladorMemoria(tk.Tk):
    def __init__(self, tamano_memoria, tamano_pagina):
        super().__init__()
        self.title("Simulador de Gestión de Procesos y Memoria")
        self.geometry("1000x600")
        self.resizable(False, False)
        
        # Parámetros de memoria
        self.tamano_memoria = tamano_memoria
        self.tamano_pagina = tamano_pagina
        self.memoria_total = tamano_memoria
        self.memoria_usada = 0
        self.paginas_totales = tamano_memoria // tamano_pagina
        self.memoria = [None] * self.paginas_totales

        # Variables de exclusión mutua
        self.lock = threading.Lock()

        # Colas de procesos
        self.cola_nuevos = Queue()
        self.cola_listos = Queue()
        self.cola_bloqueados = Queue()

        # Scheduler flag
        self.proceso_ejecutando = False

        # Crear la interfaz gráfica
        self.opcion_memoria = tk.StringVar(value="Paginacion")
        
        # Frame principal
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas para la memoria
        memoria_frame = ttk.LabelFrame(main_frame, text="Memoria")
        memoria_frame.grid(row=0, column=0, rowspan=4, padx=10, pady=10, sticky="n")
        
        self.canvas = tk.Canvas(memoria_frame, width=300, height=500, bg="white")
        self.canvas.pack(padx=10, pady=10)
        
        # Opciones de gestión de memoria
        opciones_frame = ttk.LabelFrame(main_frame, text="Opciones de Gestión de Memoria")
        opciones_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nw")
        
        ttk.Label(opciones_frame, text="Modo de Gestión de Memoria:").grid(row=0, column=0, sticky="w", pady=5)
        
        self.rbtn_paginacion = ttk.Radiobutton(opciones_frame, text="Paginación", variable=self.opcion_memoria, value="Paginacion")
        self.rbtn_paginacion.grid(row=1, column=0, sticky="w", pady=2)
        
        self.rbtn_compactacion = ttk.Radiobutton(opciones_frame, text="Compactación", variable=self.opcion_memoria, value="Compactacion")
        self.rbtn_compactacion.grid(row=2, column=0, sticky="w", pady=2)
        
        # Botones de control
        controles_frame = ttk.LabelFrame(main_frame, text="Controles")
        controles_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nw")
        
        self.btn_iniciar = ttk.Button(controles_frame, text="Iniciar Simulación", command=self.iniciar_simulacion)
        self.btn_iniciar.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        self.btn_reiniciar = ttk.Button(controles_frame, text="Reiniciar Simulación", command=self.reiniciar_simulacion)
        self.btn_reiniciar.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        
        self.btn_agregar_proceso = ttk.Button(controles_frame, text="Agregar Proceso Aleatorio", command=self.agregar_proceso_manual)
        self.btn_agregar_proceso.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        
        # Información de memoria y proceso actual
        info_frame = ttk.LabelFrame(main_frame, text="Información")
        info_frame.grid(row=2, column=1, padx=10, pady=10, sticky="nw")
        
        self.label_memoria_usada = ttk.Label(info_frame, text=f"Memoria Usada: {self.memoria_usada}/{self.memoria_total} MB")
        self.label_memoria_usada.grid(row=0, column=0, sticky="w", pady=2)
        
        self.label_proceso_actual = ttk.Label(info_frame, text="Proceso en ejecución: Ninguno")
        self.label_proceso_actual.grid(row=1, column=0, sticky="w", pady=2)
        
        # Secciones de procesos
        procesos_frame = ttk.LabelFrame(main_frame, text="Procesos")
        procesos_frame.grid(row=3, column=1, padx=10, pady=10, sticky="nw")
        
        # Nuevos
        nuevos_frame = ttk.Frame(procesos_frame)
        nuevos_frame.grid(row=0, column=0, padx=5, pady=5, sticky="n")
        ttk.Label(nuevos_frame, text="Nuevos").pack()
        self.listbox_nuevos = tk.Listbox(nuevos_frame, width=30, height=8)
        self.listbox_nuevos.pack()
        
        # Listos
        listos_frame = ttk.Frame(procesos_frame)
        listos_frame.grid(row=0, column=1, padx=5, pady=5, sticky="n")
        ttk.Label(listos_frame, text="Listos").pack()
        self.listbox_listos = tk.Listbox(listos_frame, width=30, height=8)
        self.listbox_listos.pack()
        
        # Ejecutando
        ejecutando_frame = ttk.Frame(procesos_frame)
        ejecutando_frame.grid(row=1, column=0, padx=5, pady=5, sticky="n")
        ttk.Label(ejecutando_frame, text="Ejecutando").pack()
        self.listbox_ejecutando = tk.Listbox(ejecutando_frame, width=30, height=8)
        self.listbox_ejecutando.pack()
        
        # Bloqueados
        bloqueados_frame = ttk.Frame(procesos_frame)
        bloqueados_frame.grid(row=1, column=1, padx=5, pady=5, sticky="n")
        ttk.Label(bloqueados_frame, text="Bloqueados").pack()
        self.listbox_bloqueados = tk.Listbox(bloqueados_frame, width=30, height=8)
        self.listbox_bloqueados.pack()
        
        # Mostrar la memoria en el canvas
        self.dibujar_memoria()

        # Lista de procesos activos
        self.procesos = []
        self.generacion_automatica = False

    def dibujar_memoria(self):
        self.canvas.delete("all")
        for i in range(self.paginas_totales):
            y0 = i * 15
            y1 = (i + 1) * 15
            if self.memoria[i] is None:
                color = "white"
                texto = "Vacío"
            else:
                color = "lightblue"
                texto = f"P:{self.memoria[i]}"
            self.canvas.create_rectangle(10, y0, 290, y1, fill=color, outline="black")
            self.canvas.create_text(150, y0 + 7.5, text=texto, font=("Arial", 8))
        
        # Actualizar el label de memoria usada
        self.label_memoria_usada.config(text=f"Memoria Usada: {self.memoria_usada}/{self.memoria_total} MB")

    def iniciar_simulacion(self):
        if not self.generacion_automatica:
            self.generacion_automatica = True
            modo_gestion = self.opcion_memoria.get()

            if modo_gestion == "Paginacion":
                threading.Thread(target=self.generar_procesos_automaticos, daemon=True).start()
            elif modo_gestion == "Compactacion":
                threading.Thread(target=self.generar_procesos_automaticos_compactacion, daemon=True).start()
            messagebox.showinfo("Simulador", "Simulación iniciada.")
        else:
            messagebox.showwarning("Simulador", "La simulación ya está en ejecución.")

    def generar_procesos_automaticos(self):
        while self.generacion_automatica:
            self.crear_proceso()
            time.sleep(3)  # Generar proceso cada 3 segundos

    def generar_procesos_automaticos_compactacion(self):
        while self.generacion_automatica:
            self.crear_proceso()
            time.sleep(3)

    def crear_proceso(self):
        id_proceso = f"P{random.randint(1000, 9999)}"
        espacio_proceso = random.randint(50, 250)
        proceso = {"id": id_proceso, "espacio": espacio_proceso, "estado": "Nuevo"}
        
        with self.lock:
            self.cola_nuevos.put(proceso)
        
        # Actualizar la interfaz gráfica desde el hilo principal
        self.after(0, self.actualizar_listboxes)
        
        # Intentar asignar procesos de la cola nuevos a listos
        self.asignar_procesos()

    def agregar_proceso_manual(self):
        self.crear_proceso()

    def asignar_procesos(self):
        with self.lock:
            while not self.cola_nuevos.empty():
                proceso = self.cola_nuevos.get()
                modo_gestion = self.opcion_memoria.get()
                if modo_gestion == "Paginacion":
                    asignado = self.asignar_proceso_paginado(proceso)
                elif modo_gestion == "Compactacion":
                    asignado = self.asignar_proceso_compactacion(proceso)
                
                if asignado:
                    self.cola_listos.put(proceso)
                    proceso["estado"] = "Listo"
                    # Actualizar la GUI en el hilo principal
                    self.after(0, lambda p=proceso: self.listbox_listos.insert(tk.END, f"{p['id']} ({p['espacio']} MB)"))
                else:
                    self.cola_nuevos.put(proceso)
                    # Actualizar la GUI en el hilo principal
                    self.after(0, lambda p=proceso: self.listbox_nuevos.insert(tk.END, f"{p['id']} ({p['espacio']} MB)"))
        
        self.after(0, self.actualizar_listboxes)
        self.schedule_execution()

    def asignar_proceso_paginado(self, proceso):
        paginas_necesarias = (proceso["espacio"] + self.tamano_pagina - 1) // self.tamano_pagina
        paginas_disponibles = [i for i, pagina in enumerate(self.memoria) if pagina is None]

        if len(paginas_disponibles) >= paginas_necesarias:
            for i in range(paginas_necesarias):
                self.memoria[paginas_disponibles[i]] = proceso["id"]
            self.memoria_usada += proceso["espacio"]
            self.procesos.append(proceso)
            
            # Actualizar la GUI en el hilo principal
            self.after(0, self.dibujar_memoria)
            
            return True
        else:
            return False

    def asignar_proceso_compactacion(self, proceso):
        self.compactar_memoria()
        return self.asignar_proceso_paginado(proceso)

    def compactar_memoria(self):
        nueva_memoria = [pagina for pagina in self.memoria if pagina is not None]
        self.memoria = nueva_memoria + [None] * (self.paginas_totales - len(nueva_memoria))
        self.after(0, self.dibujar_memoria)

    def schedule_execution(self):
        # Scheduler para ejecutar procesos si no hay ninguno ejecutando
        with self.lock:
            if not self.proceso_ejecutando and not self.cola_listos.empty():
                proceso = self.cola_listos.get()
                self.proceso_ejecutando = True
                proceso["estado"] = "Ejecutando"
                self.procesos = [p for p in self.procesos if p["id"] != proceso["id"]]
                self.procesos.append(proceso)  # Actualizar el estado en la lista de procesos
                
                # Actualizar la GUI en el hilo principal
                self.after(0, lambda p=proceso: self.move_to_ejecutando(p))
                
                # Iniciar la ejecución del proceso
                threading.Thread(target=self.ejecutar_proceso, args=(proceso,), daemon=True).start()

    def move_to_ejecutando(self, proceso):
        # Remover de Listos
        self.remove_proceso_de_listbox(self.listbox_listos, proceso)
        # Agregar a Ejecutando
        self.listbox_ejecutando.insert(tk.END, f"{proceso['id']} ({proceso['espacio']} MB)")
        self.label_proceso_actual.config(text=f"Proceso en ejecución: {proceso['id']}")

    def ejecutar_proceso(self, proceso):
        # Simular tiempo de ejecución
        tiempo_ejecucion = random.randint(2, 5)
        time.sleep(tiempo_ejecucion)
        
        # Finalizar la ejecución del proceso
        self.after(0, lambda p=proceso: self.finalizar_ejecucion(p))

    def finalizar_ejecucion(self, proceso):
        with self.lock:
            # Liberar memoria después de la ejecución
            paginas_liberadas = 0
            for i in range(self.paginas_totales):
                if self.memoria[i] == proceso["id"]:
                    self.memoria[i] = None
                    paginas_liberadas += 1

            self.memoria_usada -= proceso["espacio"]
            self.procesos = [p for p in self.procesos if p["id"] != proceso["id"]]
            self.dibujar_memoria()

            # Remover de Ejecutando
            self.remove_proceso_de_listbox(self.listbox_ejecutando, proceso)

            self.label_proceso_actual.config(text="Proceso en ejecución: Ninguno")
            self.proceso_ejecutando = False

            # Intentar asignar nuevos procesos
            self.schedule_execution()

    def remove_proceso_de_listbox(self, listbox, proceso):
        # Remover la representación del proceso de un listbox específico
        for idx in range(listbox.size()):
            item = listbox.get(idx)
            if item.startswith(proceso["id"]):
                listbox.delete(idx)
                break

    def actualizar_listboxes(self):
        # Limpiar todas las listboxes
        self.listbox_nuevos.delete(0, tk.END)
        self.listbox_listos.delete(0, tk.END)
        self.listbox_ejecutando.delete(0, tk.END)
        self.listbox_bloqueados.delete(0, tk.END)
        
        # Actualizar listbox de nuevos
        nuevos = list(self.cola_nuevos.queue)
        for proceso in nuevos:
            self.listbox_nuevos.insert(tk.END, f"{proceso['id']} ({proceso['espacio']} MB)")
        
        # Actualizar listbox de listos
        listos = list(self.cola_listos.queue)
        for proceso in listos:
            self.listbox_listos.insert(tk.END, f"{proceso['id']} ({proceso['espacio']} MB)")
        
        # Actualizar listbox de ejecutando
        ejecutando = [p for p in self.procesos if p["estado"] == "Ejecutando"]
        for proceso in ejecutando:
            self.listbox_ejecutando.insert(tk.END, f"{proceso['id']} ({proceso['espacio']} MB)")
        
        # Actualizar listbox de bloqueados
        bloqueados = [p for p in self.procesos if p["estado"] == "Bloqueado"]
        for proceso in bloqueados:
            self.listbox_bloqueados.insert(tk.END, f"{proceso['id']} ({proceso['espacio']} MB)")

    def reiniciar_simulacion(self):
        self.generacion_automatica = False
        self.memoria = [None] * self.paginas_totales
        self.memoria_usada = 0
        self.procesos = []
        self.proceso_ejecutando = False
        with self.lock:
            while not self.cola_nuevos.empty():
                self.cola_nuevos.get()
            while not self.cola_listos.empty():
                self.cola_listos.get()
            while not self.cola_bloqueados.empty():
                self.cola_bloqueados.get()
        
        self.dibujar_memoria()
        self.label_proceso_actual.config(text="Proceso en ejecución: Ninguno")
        self.after(0, self.actualizar_listboxes)
        messagebox.showinfo("Simulador", "Simulación reiniciada correctamente.")

if __name__ == "__main__":
    app = SimuladorMemoria(1000, 50)  # Memoria de 1000 MB con páginas de 50 MB
    app.mainloop()
