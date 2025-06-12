import logging
from memory.controller import ProgressController
from ui.menu import MenuUI
from ui.playing_level import PlayingLevelUI
from resources.image_handler import load_images_for_level

def on_level_complete(level: int):
    """Callback called when a level is completed."""
    logging.info(f"Level {level} completed!")
    controller.complete_level(level)
    controller.unlock_next_level(level + 1)

    app.refresh_menu()

def start_level(level: int) -> None:
    logging.info(f"Level {level} selected! Starting the level...")

    images = load_images_for_level(level)
    if len(images) < 3:
        logging.error(f"Not enough images to start level {level}")
        return

    correct_order = [0, 1, 2]

    playing_window = PlayingLevelUI(app, level, images, correct_order, on_level_complete)
    playing_window.grab_set()

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    try:
        controller = ProgressController()
        app = MenuUI(controller, start_level)

        def refresh_menu():
            for btn in app.level_buttons:
                btn.destroy()
            app.level_buttons.clear()
            app.create_widgets()

        app.refresh_menu = refresh_menu

        app.mainloop()
    except Exception as e:
        logging.error(f"An error occurred: {e}")