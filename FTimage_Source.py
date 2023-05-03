import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import cv2
from skimage.color import rgb2gray
import numpy.ma as ma

import tkinter as tk
from tkinter import ttk
from tkinter import *
from PIL import ImageTk, Image
from tkinter import messagebox
from tkinter import filedialog

# To Do
# DONE change antialias to LANCZOS
# DONE test out custom mask
# DONE pack this into a executable binary. 
# SDK grasshopper integration Source Developer Kit. 
# mask transparency implementation


def create_mask(mask_type, i, shape, **kwargs):
    """
    Create a mask based on the given mask type and other parameters.

    Parameters:
    -----------
    mask_type : str
        The type of mask to create.
    i : float
        The scaling factor to apply to the mask. Unimplemented
    shape : tuple
        The shape of the image to be masked.
    **kwargs : dict
        Additional keyword arguments used to create the mask.

    Returns:
    --------
    numpy.ndarray
        The mask created based on the given parameters.
    """

    rows, cols = shape

    #Validate height. 
    if kwargs.get('height') is not None:
        if kwargs['height'] > rows:
            kwargs['height'] = rows
            print('Warning: height is larger than image height. Setting height to image height.')

    # Validate width
    if kwargs.get('width') is not None:
        if kwargs['width'] > cols:
            kwargs['width'] = cols
            print('Warning: width is larger than image width. Setting width to image width.')

    # Validate stripe width - not working. 
    #if kwargs.get('stripe_width') is not None:
     #   if kwargs['stripe_width'] > min(image.shape)//2:
      #      kwargs['stripe_width'] = min(image.shape)//2
       #     print('Warning: stripe width is too large. Setting stripe width to half the image dimension.')

    try:
        if mask_type == 'lowpass':
            mask = np.zeros(shape)
            rows, cols = shape
            left = (cols - kwargs['width']) // 2
            right = left + kwargs['width']
            top = (rows - kwargs['height']) // 2
            bottom = top + kwargs['height']
            mask[:top, :] = 1
            mask[bottom:, :] = 1
            mask[:, :left] = 1
            mask[:, right:] = 1
        elif mask_type == 'highpass':
            mask = np.ones(shape)
            rows, cols = shape
            left = (cols - kwargs['width']) // 2
            right = left + kwargs['width']
            top = (rows - kwargs['height']) // 2
            bottom = top + kwargs['height']
            mask[:top, :] = 0
            mask[bottom:, :] = 0
            mask[:, :left] = 0
            mask[:, right:] = 0
        elif mask_type == 'sine_ang':
            x = np.arange(shape[1])
            y = np.arange(shape[0])
            X, Y = np.meshgrid(x, y)
            mask = np.where(np.sin((X+Y) * 2 * np.pi / kwargs['stripe_width']) >= kwargs['threshold'], 1, 0)
        elif mask_type == 'sineX':
            x = np.arange(shape[1])
            y = np.arange(shape[0])
            X, Y = np.meshgrid(x, y)
            mask = np.where(np.sin(X * 2 * np.pi / kwargs['stripe_width']) >= kwargs['threshold'], 1, 0)
        elif mask_type == 'sineY':
            x = np.arange(shape[1])
            y = np.arange(shape[0])
            X, Y = np.meshgrid(x, y)
            mask = np.where(np.sin(Y * 2 * np.pi / kwargs['stripe_width']) >= kwargs['threshold'], 1, 0)
        elif mask_type == 'custom':
            with open(kwargs['file'], 'r') as f:
                mask_func_str = f.read()
                #print(mask_func_str)
            namespace = {"np": np}
            exec(mask_func_str, namespace)
            mask_func = namespace["custom"]
            mask = mask_func(shape)

        else:
            raise ValueError(f"Invalid mask type: {mask_type}")
    except KeyError as e:
        raise ValueError(f"Missing keyword argument for mask type {mask_type}: {e}")

    mask = mask * i
    return mask

def masker(image, i, mask_type='highpass', 
height=50, width=50, threshold=0.5, stripe_width=50, 
file=''):

    """
    Apply a mask to the given image in its Fourier space and display the results.

    Parameters:
    -----------
    image : numpy.ndarray
        The input image to be masked.
    i : float 
        The scaling factor to apply to the mask. Unimplemented.
    mask_type : str, optional
        The type of mask to use. Default is 'highpass'.
    height : int, optional
        The height of the masking rectangle. Default is 50.
    width : int, optional
        The width of the masking rectangle. Default is 50.
    threshold : float, optional
        The threshold value used to create the mask (if applicable). Default is 0.5.
    stripe_width : int, optional
        The width of the stripes used to create the mask (if applicable). Default is 50.

    Returns:
    --------
    None
    """
    
    try:
        f_size = 15
        fig, ax = plt.subplots(2,2,figsize=(15,15))
        cmap_var = matplotlib.cm.viridis #try viridis #try gray

        image_grey_fourier = np.fft.fftshift(np.fft.fft2(rgb2gray(image)))
        mask = create_mask(mask_type=mask_type, i=i, shape=image_grey_fourier.shape,
                           height=height, width=width,
                           threshold=threshold, stripe_width=stripe_width, 
                           file=file)

        Mray = ma.masked_array(image_grey_fourier, mask = mask)
        Mray_clean = ma.filled(Mray, fill_value=1)

        ax[0,0].imshow(np.log(abs(image_grey_fourier)), cmap=cmap_var)
        ax[0,0].set_title("Fourier", fontsize = f_size)


        ax[1,0].imshow(np.log(abs(Mray_clean)), cmap=cmap_var)
        ax[1,0].set_title('Masked Fourier', fontsize = f_size)

        ax[0,1].imshow(rgb2gray(image), cmap=cmap_var)
        ax[0,1].set_title('Greyscale Image', fontsize = f_size)

        ax[1,1].imshow(abs(np.fft.ifft2(Mray_clean)), cmap=cmap_var)
        ax[1,1].set_title('Transformed Greyscale Image', fontsize = f_size)

        fig.set_facecolor('lightslategray')
        plt.show()
    except Exception as e:
        messagebox.showerror("Error", str(e))


class Application(tk.Frame):

    """A GUI application that applies a variety of masks to images.

    This application allows the user to select an image file and apply various masks to the image. The application uses the tkinter and Pillow libraries to create a GUI and display images, and the cv2 library to read and manipulate image data.

    The main window of the application contains several widgets, including a "Open Image" button that allows the user to select an image file, drop-down menu and spinboxes for selecting the mask type and various mask parameters, and a "Run" button that applies the selected mask to the displayed image.

    The application also includes a custom theme that is imported using a .tcl file.

    Attributes:
        master (tk.Tk): The main window of the application.

    Methods:
        __init__(self, master=None): Initializes the Application object and creates the GUI widgets.
        open_image(self): Displays the file dialog and allows the user to select an image file.
        update_image(self): Loads and displays the selected image with the current mask applied.
        create_widgets(self): Creates the GUI widgets for selecting the mask type and parameters.
        run_masker(self): Applies the selected mask to the displayed image.

    """

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Masker")
        self.master.geometry('800x600')

        # Create a style
        style = ttk.Style(root)

        # Import the tcl file
        import os

        # Get the directory where the current script or module is located
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Construct the path to the theme file relative to the current directory
        theme_file = os.path.join(current_dir, "forest-dark.tcl")

        # Load the theme file
        root.tk.call("source", theme_file)

        #root.tk.call("source", r"C:\Users\lette\OneDrive\Documents\code\python\Forest-ttk-theme-master\forest-dark.tcl")
        #root.tk.call("source", r"forest-dark.tcl")


        # Set the theme with the theme_use method
        style.theme_use("forest-dark")

        self.pack()
        self.create_widgets()
    
    def open_image(self):
        # Display the file dialog and allow the user to select an image file
        file_path = filedialog.askopenfilename()

        # If the user selected an image file, update the displayed image
        if file_path:
            self.image_path = file_path
            self.update_image()

    def open_custom(self):
        # Display the file dialog and allow the user to select an image file
        file_path = filedialog.askopenfilename()

        # If the user selected an image file, update the displayed image
        if file_path:
            self.custom_path = file_path
    
        
    def update_image(self):
        # Load and display the image
        self.image = cv2.imread(self.image_path)
        #greyscale = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        img = Image.open(self.image_path)
        img = img.resize((300, 300), Image.Resampling.LANCZOS)
        self.img = ImageTk.PhotoImage(img)

        # Destroy the old panel (if it exists)
        if hasattr(self, 'panel'):
            self.panel.destroy()

        # Create a new panel for the updated image
        self.panel = ttk.Label(self.master, image=self.img)
        self.panel.image = self.img
        self.panel.pack()

    def create_widgets(self):

        # add button to open file
        open_button = ttk.Button(self.master, text="Open Image", command=self.open_image)
        open_button.pack()

        # add button to open custom file
        open_button = ttk.Button(self.master, text="Open Custom Mask", command=self.open_custom)
        open_button.pack()

        # Add a drop-down menu for the mask type
        lbl_mask_type = ttk.Label(self.master, text="Mask Type:")
        lbl_mask_type.pack()
        self.mask_type_var = StringVar(self.master)
        self.mask_type_var.set("highpass")
        mask_type_dropdown = ttk.OptionMenu(self.master, self.mask_type_var, "highpass", "highpass", "lowpass", "sine_ang", "sineX", "sineY", "custom")
        mask_type_dropdown.pack()

        # Add a spinbox for the mask height
        lbl_height = ttk.Label(self.master, text="Mask Height:")
        lbl_height.pack()
        self.height_var = IntVar(self.master)
        self.height_var.set(50)
        height_spinbox = ttk.Spinbox(self.master, from_=0, to=50, width=5, textvariable=self.height_var)
        height_spinbox.pack()

        # Add a spinbox for the mask width
        lbl_width = ttk.Label(self.master, text="Mask Width:")
        lbl_width.pack()
        self.width_var = IntVar(self.master)
        self.width_var.set(50)
        width_spinbox = ttk.Spinbox(self.master, from_=0, to=50, width=5, textvariable=self.width_var)
        width_spinbox.pack()

        # Add a spinbox for the threshold (used in the sine_ang, sineX, and sineY masks)
        lbl_threshold = ttk.Label(self.master, text="Threshold:")
        lbl_threshold.pack()
        self.threshold_var = DoubleVar(self.master)
        self.threshold_var.set(0.5)
        threshold_spinbox = ttk.Spinbox(self.master, from_=0.0, to=50, increment=0.1, width=5, textvariable=self.threshold_var)
        threshold_spinbox.pack()

        # Add a spinbox for the stripe width (used in the sine_ang, sineX, and sineY masks)
        lbl_stripe_width = ttk.Label(self.master, text="Stripe Width:")
        lbl_stripe_width.pack()
        self.stripe_width_var = IntVar(self.master)
        self.stripe_width_var.set(50)
        stripe_width_spinbox = ttk.Spinbox(self.master, from_=0, to=50, width=5, textvariable=self.stripe_width_var)
        stripe_width_spinbox.pack()
        
        # Add a "Run" button
        run_button = ttk.Button(self.master, text="Run", command=self.run_masker)
        run_button.pack()

    def run_masker(self):
        masker(image=self.image, i=1, mask_type=self.mask_type_var.get(), height=self.height_var.get(), width=self.width_var.get(),
           threshold=self.threshold_var.get(), stripe_width=self.stripe_width_var.get(), file=self.custom_path)


root = tk.Tk()
app = Application(master=root)
app.mainloop()


           
