import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import mysql.connector
from datetime import datetime

class TaekwondoUserManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestión de Datos - Sistema de Movilidad")
        self.root.geometry("900x700")
        
        # Configuración de la base de datos
        self.db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': '',
            'database': 'bd_movilidad'
        }
        
        # Variables para los campos
        self.id_var = tk.StringVar()
        self.nombre_var = tk.StringVar()
        self.correo_var = tk.StringVar()
        self.contrasena_var = tk.StringVar()

        # Variables para las otras tablas
        self.movilidad_id_var = tk.StringVar()
        self.fuerza_id_var = tk.StringVar()
        self.estadisticas_id_var = tk.StringVar()
        
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Sección de formulario de usuario
        self.form_frame_user = ttk.LabelFrame(main_frame, text="Datos del Usuario", padding="10")
        self.form_frame_user.grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # Campos del formulario
        ttk.Label(self.form_frame_user, text="ID Usuario:").grid(row=0, column=0, padx=5, pady=5)
        ttk.Entry(self.form_frame_user, textvariable=self.id_var, state='readonly').grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(self.form_frame_user, text="Nombre:").grid(row=1, column=0, padx=5, pady=5)
        ttk.Entry(self.form_frame_user, textvariable=self.nombre_var).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(self.form_frame_user, text="Correo:").grid(row=2, column=0, padx=5, pady=5)
        ttk.Entry(self.form_frame_user, textvariable=self.correo_var).grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(self.form_frame_user, text="Contraseña:").grid(row=3, column=0, padx=5, pady=5)
        ttk.Entry(self.form_frame_user, textvariable=self.contrasena_var, show="*").grid(row=3, column=1, padx=5, pady=5)
        
        # Botones de acción de usuario
        button_frame_user = ttk.Frame(self.form_frame_user)
        button_frame_user.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame_user, text="Nuevo Usuario", command=self.new_user).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame_user, text="Guardar Usuario", command=self.save_user).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame_user, text="Eliminar Usuario", command=self.delete_user).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame_user, text="Limpiar Usuario", command=self.clear_user_form).grid(row=0, column=3, padx=5)

        # Tabla de usuarios
        table_frame_user = ttk.LabelFrame(main_frame, text="Lista de Usuarios", padding="10")
        table_frame_user.grid(row=1, column=0, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar la tabla
        columns = ('ID', 'Nombre', 'Correo', 'Fecha Registro')
        self.tree_user = ttk.Treeview(table_frame_user, columns=columns, show='headings')
        
        for col in columns:
            self.tree_user.heading(col, text=col)
            self.tree_user.column(col, width=150)
        
        # Scrollbars
        yscrollbar_user = ttk.Scrollbar(table_frame_user, orient=tk.VERTICAL, command=self.tree_user.yview)
        xscrollbar_user = ttk.Scrollbar(table_frame_user, orient=tk.HORIZONTAL, command=self.tree_user.xview)
        self.tree_user.configure(yscrollcommand=yscrollbar_user.set, xscrollcommand=xscrollbar_user.set)
        
        self.tree_user.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        yscrollbar_user.grid(row=0, column=1, sticky=(tk.N, tk.S))
        xscrollbar_user.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        self.tree_user.bind('<<TreeviewSelect>>', self.on_select_user)
        
        # Configurar expansión
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        table_frame_user.columnconfigure(0, weight=1)
        table_frame_user.rowconfigure(0, weight=1)

    def db_connect(self):
        """Establece conexión con la base de datos"""
        try:
            return mysql.connector.connect(**self.db_config)
        except mysql.connector.Error as err:
            messagebox.showerror("Error de Conexión", f"No se pudo conectar a la base de datos: {err}")
            return None

    def load_data(self):
        """Carga los datos de usuario en la tabla"""
        for item in self.tree_user.get_children():
            self.tree_user.delete(item)
            
        conn = self.db_connect()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM Usuario ORDER BY id_usuario")
                
                for user in cursor.fetchall():
                    fecha = user[4].strftime('%Y-%m-%d %H:%M:%S') if user[4] else ''
                    self.tree_user.insert('', tk.END, values=(user[0], user[1], user[2], fecha))
                    
            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"Error al cargar datos: {err}")
            finally:
                conn.close()

    def clear_user_form(self):
        """Limpia el formulario de usuario"""
        self.id_var.set('')
        self.nombre_var.set('')
        self.correo_var.set('')
        self.contrasena_var.set('')

    def new_user(self):
        """Prepara el formulario para un nuevo usuario"""
        self.clear_user_form()

    def save_user(self):
        """Guarda o actualiza un usuario"""
        nombre = self.nombre_var.get().strip()
        correo = self.correo_var.get().strip()
        contrasena = self.contrasena_var.get().strip()
        
        if not nombre or not correo or not contrasena:
            messagebox.showwarning("Datos Incompletos", "Por favor complete todos los campos")
            return
            
        conn = self.db_connect()
        if conn:
            try:
                cursor = conn.cursor()
                user_id = self.id_var.get()
                
                if user_id:  # Actualizar
                    cursor.execute("""
                        UPDATE Usuario 
                        SET nombre = %s, correo = %s, contrasena = %s 
                        WHERE id_usuario = %s
                    """, (nombre, correo, contrasena, user_id))
                    messagebox.showinfo("Éxito", "Usuario actualizado correctamente")
                else:  # Insertar nuevo
                    cursor.execute("""
                        INSERT INTO Usuario (nombre, correo, contrasena) 
                        VALUES (%s, %s, %s)
                    """, (nombre, correo, contrasena))
                    messagebox.showinfo("Éxito", "Usuario creado correctamente")
                
                conn.commit()
                self.load_data()
                self.clear_user_form()
                
            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"Error al guardar usuario: {err}")
            finally:
                conn.close()

    def delete_user(self):
        """Elimina un usuario"""
        user_id = self.id_var.get()
        if not user_id:
            messagebox.showwarning("Selección Requerida", "Por favor seleccione un usuario para eliminar")
            return
            
        if not messagebox.askyesno("Confirmar Eliminación", 
                                  "¿Está seguro de que desea eliminar este usuario?\n" +
                                  "Esta acción no se puede deshacer."):

            return
            
        conn = self.db_connect()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM Usuario WHERE id_usuario = %s", (user_id,))
                conn.commit()
                
                messagebox.showinfo("Éxito", "Usuario eliminado correctamente")
                self.load_data()
                self.clear_user_form()
                
            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"Error al eliminar usuario: {err}")
            finally:
                conn.close()

    def on_select_user(self, event):
        """Cuando se selecciona una fila en la tabla de usuarios"""
        item = self.tree_user.selection()
        if item:
            user_id, nombre, correo, _ = self.tree_user.item(item, "values")
            self.id_var.set(user_id)
            self.nombre_var.set(nombre)
            self.correo_var.set(correo)
            # Contraseña no se carga por seguridad
        

if __name__ == "__main__":
    root = tk.Tk()
    app = TaekwondoUserManager(root)
    root.mainloop()
