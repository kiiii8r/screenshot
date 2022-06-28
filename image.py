import io
from time import sleep
from typing import List, Tuple, Optional
from PIL import Image

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def get_full_screenshot_image(driver, reverse=False, driverss_contains_scrollbar=None):
    # type: (selenium.webdriver.remote.webdriver.WebDriver, bool, Optional[bool]) -> Image.Image
    """
    take full screenshot and get its Pillow instance
    :param driver: Selenium WebDriver
    :param reverse: Paste from bottom direction when combining images. The default is False.
    :param driverss_contains_scrollbar: Set to True if the screenshot taken by WebDriver contains a horizontal scroll bar. Default is determined automatically.
    """
    if driverss_contains_scrollbar is None:
        driverss_contains_scrollbar = isinstance(driver, webdriver.Chrome)
    # Scroll to the bottom of the page once
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(0.5)
    scroll_height, document_client_width, document_client_height, inner_width, inner_height = driver.execute_script("return [document.body.scrollHeight, document.documentElement.clientWidth, document.documentElement.clientHeight, window.innerWidth, window.innerHeight]")
    streams_to_be_closed = []   # type: List[io.BytesIO]
    images = [] # type: List[Tuple[Image.Image, int]]
    try:
        # open
        for y_coord in range(0, scroll_height, document_client_height):
            driver.execute_script("window.scrollTo(0, arguments[0]);", y_coord)
            stream = io.BytesIO(driver.get_screenshot_as_png())
            streams_to_be_closed.append(stream)
            img = Image.open(stream)
            images.append((img, min(y_coord, scroll_height - inner_height)))  # Image, y_coord
        # load
        scale = float(img.size[0]) / (inner_width if driverss_contains_scrollbar else document_client_width)
        img_dst = Image.new(mode='RGBA', size=(int(document_client_width * scale), int(scroll_height * scale)))
        for img, y_coord in (reversed(images) if reverse else images):
            img_dst.paste(img, (0, int(y_coord * scale)))
        return img_dst
    finally:
        # close
        for stream in streams_to_be_closed:
            stream.close()
        for img, y_coord in images:
            img.close()

options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(executable_path='/Users/○○○○/Desktop/WebDriver/chromedriver',options=options)

urls = [
        "https://carmo-kun.jp/lp/35/",
        "https://carmo-kun.jp/lp/36/"
        ]

for url in urls:
    driver.get(url)
    sleep (3)

    img = get_full_screenshot_image(driver) 
       
    img_name = "/Users/○○○○○/Desktop/WebDriver/image_" +  url.lstrip("https://" "http://" ).replace("/","_").replace("?", "_") + ".png"
    img.save(img_name)    