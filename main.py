import tkinter as tk
from gui.main_window import VentanaPrincipal
from core.app import AppController
from core.config import VENTANA_TITULO, VENTANA_DIMENSIONES

def main():
    """Función principal de la aplicación"""
    # Crear ventana raíz
    root = tk.Tk()
    root.title(VENTANA_TITULO)
    root.geometry(VENTANA_DIMENSIONES)
    root.resizable(True, True)
    
    # Crear ventana principal (sin controller aún)
    ventana = VentanaPrincipal(root, None)
    
    # Crear controlador
    controller = AppController(ventana)
    
    # Inyectar controlador en la ventana
    ventana.set_controller(controller)
    
    # Iniciar la aplicación
    root.mainloop()

if __name__ == "__main__":
    main()