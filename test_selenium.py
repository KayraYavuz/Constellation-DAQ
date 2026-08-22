from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)
driver.get("http://localhost:5050")
time.sleep(2)

logs = driver.get_log("browser")
for log in logs:
    print("PAGE LOAD LOG:", log)

driver.execute_script("openPanel('dfp_panel', 'TDAQ System', 'DFP Panel & Network', 'dfp_panel', true);")
time.sleep(1)

logs = driver.get_log("browser")
for log in logs:
    print("AFTER CLICK LOG:", log)

print("Active panels:", driver.execute_script("return Object.keys(activePanels);"))
driver.quit()
