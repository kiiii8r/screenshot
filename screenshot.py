import io
from time import sleep
from typing import List, Tuple, Optional
from PIL import Image
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def get_full_screenshot_image(driver, reverse=False, driverss_contains_scrollbar=None):
    # type: (selenium.webdriver.remote.webdriver.WebDriver, bool, Optional[bool]) -> Image.Image
    """
    スクリーンショットを撮影し、ピロウズインスタンスを取得する。
    :param reverse: 画像合成時に下方向から貼り付けます。デフォルトはFalse。
    :param driverss_contains_scrollbar: WebDriverで撮影したスクリーンショットに水平スクロールバーが含まれている場合にTrueに設定します。デフォルトは自動で決定されます。
    """
    if driverss_contains_scrollbar is None:
        driverss_contains_scrollbar = isinstance(driver, webdriver.Chrome)
    # Scroll to the bottom of the page once
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(0.5)
    scroll_height, document_client_width, document_client_height, inner_width, inner_height = driver.execute_script("return [document.body.scrollHeight, document.documentElement.clientWidth, document.documentElement.clientHeight, window.innerWidth, window.innerHeight]")
    streams_to_be_closed = []   # type: List[io.BytesIO]

    # 固定ヘッダー削除
    topnav = driver.find_elements_by_class_name("top-header")
    coupon = driver.find_elements_by_class_name("sugoi-badge")
    gotop = driver.find_elements_by_class_name("go-top")

    if topnav:
      driver.execute_script("arguments[0].setAttribute('style', 'position: absolute; top: 0px;')", topnav[0]) 

    if coupon:
      driver.execute_script("arguments[0].setAttribute('style', 'position: absolute; top: 0px;')", coupon[0]) 

    if gotop:
      driver.execute_script("arguments[0].setAttribute('style', 'position: absolute; top: 0px;')", gotop[0]) 

    images = [] # type: List[Tuple[Image.Image, int]]
    try:
        # open
        for y_coord in range(0, scroll_height, document_client_height):
            driver.execute_script("window.scrollTo(0, arguments[0]);", y_coord)

            # スクショまでの待機時間
            sleep(0.3)
            stream = io.BytesIO(driver.get_screenshot_as_png())

            #ファンプレイヤーが出たら非表示
            funplayer = driver.find_elements_by_class_name("fpw-view")

            if funplayer:
              driver.execute_script("arguments[0].setAttribute('style', 'position: absolute; top: 0px;')", funplayer[1]) 

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
# options.add_argument('--headless')
driver = webdriver.Chrome(executable_path='/Users/kii/lang/python/chromedriver',options=options)

# url.csvの読み込み
df = pd.read_csv('url.csv')
urls = []
for idx in range(len(df['URL'])):
  urls.append(df['URL'][idx])
  
for url in urls:
    driver.get(url)
    sleep (3)

    img = get_full_screenshot_image(driver) 
       
    img_name = url.lstrip("https://" "http://" ).replace("/","_").replace("?", "_") + ".png"
    img.save(img_name)    