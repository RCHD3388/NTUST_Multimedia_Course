# ui/app.py

"""
Simple interface for Part 2 experiments.

The interface only runs the manual renderer
and displays the generated pixel-array images.
"""

import tkinter as tk
from tkinter import messagebox

from PIL import Image, ImageTk

from experiments.part2 import (
    run_part2_point2,
    run_part2_point3,
)


DISPLAY_SIZE = 330


class Part2App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Multimedia Homework - Part 2")
        self.root.geometry("1700x950")

        # Keep references to displayed images.
        self.photo_images = []

        self.build_interface()

    def build_interface(self) -> None:
        """
        Build the application controls.
        """
        title = tk.Label(
            self.root,
            text="Part 2 - Inside and Outside",
            font=("Arial", 16, "bold"),
        )
        title.pack(pady=(15, 10))

        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=5)

        star_button = tk.Button(
            button_frame,
            text="Point 2 - Five-Pointed Star",
            width=26,
            command=self.show_star_result,
        )
        star_button.pack(
            side=tk.LEFT,
            padx=5,
        )

        circle_button = tk.Button(
            button_frame,
            text="Point 3 - Path Direction",
            width=26,
            command=self.show_circle_results,
        )
        circle_button.pack(
            side=tk.LEFT,
            padx=5,
        )

        self.info_label = tk.Label(
            self.root,
            text="Choose an experiment.",
            font=("Arial", 11),
            justify=tk.LEFT,
        )
        self.info_label.pack(pady=10)

        self.result_frame = tk.Frame(self.root)
        self.result_frame.pack(
            fill=tk.BOTH,
            expand=True,
            padx=15,
            pady=10,
        )

    def clear_results(self) -> None:
        """
        Clear the current result display.
        """
        for widget in self.result_frame.winfo_children():
            widget.destroy()

        self.photo_images.clear()

    def load_display_image(
        self,
        filename: str,
    ) -> ImageTk.PhotoImage:
        """
        Load the rendered PNG without resizing or resampling.
        """
        image = Image.open(filename).convert("RGB")
        photo = ImageTk.PhotoImage(image)

        self.photo_images.append(photo)

        return photo

    def add_image_panel(
        self,
        parent: tk.Widget,
        title: str,
        filename: str,
    ) -> None:
        """
        Add one generated image to the interface.
        """
        panel = tk.Frame(parent)

        label = tk.Label(
            panel,
            text=title,
            font=("Arial", 11, "bold"),
        )
        label.pack(pady=(0, 5))

        photo = self.load_display_image(filename)

        image_label = tk.Label(
            panel,
            image=photo,
        )
        image_label.pack()

        panel.pack(
            side=tk.LEFT,
            expand=True,
            padx=10,
        )

    def show_star_result(self) -> None:
        """
        Run and show Part 2 Point 2.
        """
        try:
            result = run_part2_point2()

            self.clear_results()

            self.info_label.config(
                text=(
                    "Five-pointed self-intersecting star\n"
                    f"Center winding number: "
                    f"{result['center_winding']}"
                )
            )

            self.add_image_panel(
                self.result_frame,
                "Filled Star",
                result["filled_image"],
            )

        except Exception as error:
            messagebox.showerror(
                "Rendering Error",
                str(error),
            )

    def show_circle_results(self) -> None:
        """
        Run and show Part 2 Point 3.
        """
        try:
            result = run_part2_point3()

            self.clear_results()

            self.info_label.config(
                text=(
                    "Inner points unchanged: "
                    f"{result['points_unchanged']}\n"
                    "Same direction center winding: "
                    f"{result['same_direction_winding']}\n"
                    "Reversed inner direction center winding: "
                    f"{result['opposite_direction_winding']}"
                )
            )

            self.add_image_panel(
                self.result_frame,
                "Same Direction",
                result["same_direction_image"],
            )

            self.add_image_panel(
                self.result_frame,
                "Inner Direction Reversed",
                result["opposite_direction_image"],
            )

        except Exception as error:
            messagebox.showerror(
                "Rendering Error",
                str(error),
            )


def run_app() -> None:
    """
    Start the graphical interface.
    """
    root = tk.Tk()
    Part2App(root)
    root.mainloop()