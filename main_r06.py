import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk


def load_image():
    file_path = filedialog.askopenfilename(
        filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.bmp")]
    )
    if file_path:
        global base_image, base_image_display, img_tk
        base_image = Image.open(file_path).convert("RGBA")  # Ensure we use RGBA for transparency
        base_image.thumbnail((400, 400))  # Resizing for display
        base_image_display = base_image.copy()  # Copy for dynamic overlay
        img_tk = ImageTk.PhotoImage(base_image_display)
        image_label.config(image=img_tk)
        image_label.image = img_tk
        root.update()


def load_watermark():
    file_path = filedialog.askopenfilename(
        filetypes=[("PNG files", "*.png")]
    )
    if file_path:
        global watermark_image, watermark_resized
        watermark_image = Image.open(file_path).convert("RGBA")  # Load PNG with transparency
        apply_watermark()


def apply_watermark():
    if base_image and watermark_image:
        # Adjust watermark size and opacity dynamically
        update_watermark()


def update_watermark():
    global base_image_display, watermark_image, watermark_resized, img_tk, watermark_pos
    base_image_display = base_image.copy()

    # Resize the watermark dynamically based on the slider
    size_percentage = watermark_size_slider.get() / 100.0
    watermark_resized = watermark_image.resize(
        (int(watermark_image.width * size_percentage), int(watermark_image.height * size_percentage)),
        Image.Resampling.LANCZOS
    )

    # Adjust watermark opacity
    opacity = int(opacity_slider.get() * 2.55)  # Convert to 0-255 range
    watermark_with_opacity = watermark_resized.copy()
    alpha = watermark_with_opacity.split()[3]  # Get the alpha channel
    alpha = alpha.point(lambda p: p * (opacity / 255))  # Apply opacity
    watermark_with_opacity.putalpha(alpha)

    if grid_mode.get():
        # Grid mode - spread multiple copies of the watermark across the image, but spaced out every 3rd watermark
        spacing_x = watermark_with_opacity.width * 3  # Every 3rd width
        spacing_y = watermark_with_opacity.height * 3  # Every 3rd height
        for x in range(0, base_image.width, spacing_x):
            for y in range(0, base_image.height, spacing_y):
                base_image_display.paste(watermark_with_opacity, (x, y), watermark_with_opacity)
    else:
        # Single watermark mode - Place one watermark at the current position
        watermark_pos = (
            max(0, min(watermark_pos[0], base_image.width - watermark_with_opacity.width)),
            max(0, min(watermark_pos[1], base_image.height - watermark_with_opacity.height))
        )
        base_image_display.paste(watermark_with_opacity, watermark_pos, watermark_with_opacity)

    # Update the display
    img_tk = ImageTk.PhotoImage(base_image_display)
    image_label.config(image=img_tk)
    image_label.image = img_tk
    root.update()


def start_drag(event):
    # When mouse is clicked, start drag
    global drag_data
    drag_data["start_x"] = event.x
    drag_data["start_y"] = event.y
    drag_data["start_pos_x"] = watermark_pos[0]
    drag_data["start_pos_y"] = watermark_pos[1]


def on_drag(event):
    # When the mouse is moved with button held down, calculate position offset
    global watermark_pos
    delta_x = event.x - drag_data["start_x"]
    delta_y = event.y - drag_data["start_y"]

    # Calculate new watermark position relative to the mouse drag
    new_x = drag_data["start_pos_x"] + delta_x
    new_y = drag_data["start_pos_y"] + delta_y

    # Ensure the new position stays within the image boundaries
    new_x = max(0, min(new_x, base_image.width - watermark_resized.width))
    new_y = max(0, min(new_y, base_image.height - watermark_resized.height))

    # Update the watermark position and refresh the image
    watermark_pos = (new_x, new_y)
    update_watermark()


# Initialize the tkinter window
root = tk.Tk()
root.title("Dynamic Watermarking Program")

# Set the initial size of the window (width x height)
root.geometry("600x700")

# Label to display the image
image_label = tk.Label(root)
image_label.pack()

# Button to load the image
load_button = tk.Button(root, text="Load Image", command=load_image)
load_button.pack(pady=10)

# Button to load the watermark
watermark_button = tk.Button(root, text="Load Watermark", command=load_watermark)
watermark_button.pack(pady=10)

# Opacity slider
opacity_slider = tk.Scale(root, from_=0, to=100, orient="horizontal", label="Opacity")
opacity_slider.pack(pady=10)
opacity_slider.set(100)  # Set default opacity to 100%
opacity_slider.bind("<Motion>", lambda event: update_watermark())

# Watermark size slider (from 10% to 200% of the original size)
watermark_size_slider = tk.Scale(root, from_=10, to=200, orient="horizontal", label="Watermark Size (%)")
watermark_size_slider.pack(pady=10)
watermark_size_slider.set(100)  # Default size is 100% (original size)
watermark_size_slider.bind("<Motion>", lambda event: update_watermark())

# Checkbox for grid mode
grid_mode = tk.BooleanVar()  # Variable to track the checkbox state
grid_checkbox = tk.Checkbutton(root, text="Grid Mode", variable=grid_mode, command=update_watermark)
grid_checkbox.pack(pady=10)

# Variables to hold images
base_image = None
base_image_display = None
watermark_image = None
watermark_resized = None
img_tk = None

# Variables to hold drag data and watermark position
drag_data = {"start_x": 0, "start_y": 0, "start_pos_x": 0, "start_pos_y": 0}
watermark_pos = (0, 0)  # Initial watermark position at the top-left corner

# Binding the dragging events to the image label
image_label.bind("<Button-1>", start_drag)
image_label.bind("<B1-Motion>", on_drag)

# Start the main loop
root.mainloop()
