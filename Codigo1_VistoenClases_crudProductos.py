import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox
import mysql.connector

class ProductDB:
    def __init__(self, host, user, password, port, database):
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            port=port,
            database=database
        )
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS datosdb (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(255),
                precio DECIMAL(10, 2),
                stock INT
            )
        """)
        self.conn.commit()

    def execute_query(self, query, params=None):
        try:
            self.cursor.execute(query, params)
            if query.strip().upper().startswith("SELECT"):
                result = self.cursor.fetchall()
                return result
            self.conn.commit()
        except mysql.connector.Error as e:
            messagebox.showerror("Error de base de datos", str(e))
        return []

    def fetch_all_products(self):
        return self.execute_query("SELECT * FROM datosdb")
    
class ProductCRUDApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestión de Productos")
        self.db = ProductDB(
            host="127.0.0.1",
            user="root",
            password="Papajorge302*",
            port="3306",
            database="adso"
        )

        self.create_widgets()
        self.load_products()

    def create_widgets(self):
        self.create_treeview()
        self.create_input_fields()
        self.create_buttons()

    def create_treeview(self):
        self.tree = ttk.Treeview(self.root, columns=("ID", "Nombre", "Precio", "Stock"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("Precio", text="Precio")
        self.tree.heading("Stock", text="Stock")
        self.tree.pack(padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def create_input_fields(self):
        fields = [("Nombre del Producto:", 10), ("Precio/h:", 10), ("Stock:", 10)]
        self.entries = {}
        for label_text, width in fields:
            label = ttk.Label(self.root, text=label_text)
            label.pack(pady=(0, 5), padx=10, anchor="w")

            entry = ttk.Entry(self.root, width=width)
            entry.pack(pady=(0, 10), padx=10, fill="x")
            self.entries[label_text] = entry

    def create_buttons(self):
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=10)

        buttons = [("Agregar", self.add_product), ("Eliminar", self.remove_product),
                   ("Actualizar", self.update_product), ("Buscar", self.search_product),
                   ("Mostrar Todo", self.show_all_products)]

        for text, command in buttons:
            button = ttk.Button(btn_frame, text=text, command=command)
            button.grid(row=0, column=buttons.index((text, command)), padx=5)

    def load_products(self):
        self.clear_table()
        for row in self.db.fetch_all_products():
            self.tree.insert("", "end", values=row)

    def add_product(self):
        values = [entry.get() for entry in self.entries.values()]
        if all(values):
            query = "INSERT INTO datosdb (nombre, precio, stock) VALUES (%s, %s, %s)"
            self.db.execute_query(query, tuple(values))  # Convertir valores a una tupla
            messagebox.showinfo("Éxito", "Producto agregado con éxito")
            self.load_products()
            self.clear_input_fields()
        else:
            messagebox.showerror("Error", "Por favor, complete todos los campos")

    def remove_product(self):
        selected_item = self.tree.selection()
        if selected_item:
            product_id = self.tree.item(selected_item, "values")[0]
            self.db.execute_query("DELETE FROM datosdb WHERE id=%s", (product_id,))
            messagebox.showinfo("Éxito", "Producto eliminado con éxito")
            self.load_products()

    def update_product(self):
        selected_item = self.tree.selection()
        if selected_item:
            product_id = self.tree.item(selected_item, "values")[0]
            values = [entry.get() for entry in self.entries.values()]
            query = "UPDATE datosdb SET nombre=%s, precio=%s, stock=%s WHERE id=%s"
            params = tuple(values + [product_id])  # Convertir a tupla
            self.db.execute_query(query, params)
            messagebox.showinfo("Éxito", "Producto actualizado con éxito")
            self.load_products()
            self.clear_input_fields()

    def search_product(self):
        search_term = self.entries["Nombre del Producto:"].get()
        if search_term:
            self.clear_table()
            query = "SELECT * FROM datosdb WHERE nombre LIKE %s"
            param = ('%' + search_term + '%',)
            result = self.db.execute_query(query, param)
            if result:
                for row in result:
                    self.tree.insert("", "end", values=row)
            else:
                messagebox.showinfo("No encontrado", "No se encontraron productos que coincidan con el término de búsqueda")
        else:
            messagebox.showerror("Error", "Por favor, ingrese un término de búsqueda")


    def show_all_products(self):
        self.load_products()

    def on_tree_select(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            values = self.tree.item(selected_item, "values")
            if values:
                for entry, value in zip(self.entries.values(), values[1:]):
                    entry.delete(0, tk.END)
                    entry.insert(0, value)

    def clear_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def clear_input_fields(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = ProductCRUDApp(root)
    root.mainloop()
