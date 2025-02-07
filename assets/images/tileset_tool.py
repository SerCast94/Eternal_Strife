import os
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from PIL import Image, ImageDraw, ImageFont, ImageTk

class TileSetTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Generador de Tiles Numerados")

        self.image = None
        self.processed_image = None
        self.image_path = None
        self.tile_size = None

        self.canvas = tk.Canvas(root, width=800, height=600, bg="lightgray")
        self.canvas.pack(padx=10, pady=10, side=tk.LEFT, expand=True, fill=tk.BOTH)

        self.controls_frame = tk.Frame(root)
        self.controls_frame.pack(padx=10, pady=10, side=tk.RIGHT, fill=tk.Y)

        self.load_button = tk.Button(self.controls_frame, text="Cargar Imagen", command=self.load_image)
        self.load_button.pack(pady=10)

        self.tile_size_button = tk.Button(self.controls_frame, text="Indicar Tamaño del Tile", command=self.set_tile_size)
        self.tile_size_button.pack(pady=10)

        self.export_button = tk.Button(self.controls_frame, text="Exportar Imagen", command=self.export_image)
        self.export_button.pack(pady=10)

        self.resolution_label = tk.Label(self.controls_frame, text="Resolución: N/A")
        self.resolution_label.pack(pady=10)

    def load_image(self):
        initial_dir = os.path.dirname(__file__)
        self.image_path = filedialog.askopenfilename(initialdir=initial_dir, filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
        if self.image_path:
            self.image = Image.open(self.image_path)
            self.display_image(self.image)
            self.resolution_label.config(text=f"Resolución: {self.image.width}x{self.image.height}")

    def display_image(self, image):
        self.canvas.delete("all")
        self.canvas.image = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.canvas.image)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

    def set_tile_size(self):
        if self.image:
            self.tile_size = simpledialog.askinteger("Tamaño del tile", "Introduce el tamaño de cada tile (en píxeles):")
            if self.tile_size:
                self.processed_image = self.image.copy()
                self.process_image(self.processed_image, self.tile_size)
                self.display_image(self.processed_image)
        else:
            messagebox.showwarning("Advertencia", "Primero carga una imagen.")

    def export_image(self):
        if self.processed_image:
            output_folder = "output_tiles"
            os.makedirs(output_folder, exist_ok=True)
            original_name = os.path.splitext(os.path.basename(self.image_path))[0]
            output_path = os.path.join(output_folder, f"{original_name}_numerado.png")
            self.processed_image.save(output_path)
            messagebox.showinfo("Proceso completado", f"La imagen con los tiles numerados ha sido generada correctamente como {output_path}.")
        else:
            messagebox.showwarning("Advertencia", "Primero carga una imagen y establece el tamaño del tile.")

    def process_image(self, image, tile_size):
        image_width, image_height = image.size

        # Calcular el número de tiles en cada dirección
        tiles_x = image_width // tile_size
        tiles_y = image_height // tile_size

        # Escalar la imagen antes de escribir los números
        scaled_image = image.resize((image_width * 4, image_height * 4), Image.NEAREST).convert("RGBA")
        draw = ImageDraw.Draw(scaled_image)

        # Crear una fuente para numerar los tiles
        font_size = max(10, (tile_size * 4) // 3)
        font = ImageFont.truetype("arial.ttf", font_size)

        # Dibujar las líneas horizontales
        for y in range(tiles_y + 1):
            draw.line([(0, y * tile_size * 4), (image_width * 4, y * tile_size * 4)], fill=(255, 0, 0, 128))

        # Dibujar las líneas verticales
        for x in range(tiles_x + 1):
            draw.line([(x * tile_size * 4, 0), (x * tile_size * 4, image_height * 4)], fill=(255, 0, 0, 128))

        # Numerar los tiles
        for y in range(tiles_y):
            for x in range(tiles_x):
                tile_index = y * tiles_x + x
                draw.text((x * tile_size * 4 + 20, y * tile_size * 4 + 20), str(tile_index), font=font, fill="white")

        self.processed_image = scaled_image

def main():
    root = tk.Tk()
    app = TileSetTool(root)
    root.mainloop()

if __name__ == "__main__":
    main()