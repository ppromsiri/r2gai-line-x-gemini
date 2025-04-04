import gspread

# First you need access to the Google API. Based on the route you
# chose in Step 1, call either service_account(), oauth() or api_key().
gc = gspread.service_account(filename="sa.json")
sh = gc.open_by_key("1WYLQd84Sbkz-VXOHiJ7B2r7kA2PTqDPi6fgucKQO2aE")
sh.sheet1.append_row(["Hello", "World!"])