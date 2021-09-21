import os

TEMP_DIR = "./data/temp"
if not os.path.isdir(TEMP_DIR):
    os.makedirs(TEMP_DIR)

JSON_DIR = "./data/json/"
if not os.path.isdir(JSON_DIR):
    os.makedirs(JSON_DIR)

DATA_DIR = "./data"
if not os.path.isdir(DATA_DIR):
    os.makedirs(DATA_DIR)

HEADER = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
    "cookie": "cookie: Hm_lvt_7d06c05f2674b5f5fffa6500f4e9da89=1631376039; tgw_l7_route=44a8ecb0130e9cd4b0b2316b71c7a866; PHPSESSID=5ebelmq7p4mbtm9pn71bsvl6j6; Hm_lpvt_7d06c05f2674b5f5fffa6500f4e9da89=1631376664",
}

SAVE_TEMP = True

TOUR_ID = {
    '103': ['2019LPL春季赛', 20190114],
    '104': ['2019LCK春季赛', 20190116],
    '105': ['2019LCS春季赛', 20190126],
    '106': ['2019LEC春季赛', 20190118],
    
    '120': ['2019LPL夏季赛', 20190601],
    '122': ['2019LCS夏季赛', 20190601],
    '123': ['2019LCK夏季赛', 20190605],
    '126': ['2019LEC夏季赛', 20190607],
    
    '152': ['2020LPL春季赛', 20200113],
    '153': ['2020LCK春季赛', 20200205],
    '157': ['2020LCS春季赛', 20200126],
    '158': ['2020LEC春季赛', 20200124],
    
    '170': ['2020LCS夏季赛', 20200612],
    '171': ['2020LEC夏季赛', 20200612],
    '172': ['2020LPL夏季赛', 20200605],
    '173': ['2020LCK夏季赛', 20200617],
    '177': ['S10LPL资格赛', 20200828],
    '179': ['S10LCK资格赛', 20200907],
    
    '189': ['2021LCS春季赛', 20210205],
    '190': ['2021LEC春季赛', 20210122],
    '191': ['2021LPL春季赛', 20210109],
    '192': ['2021LCK春季赛', 20210113],
    
    '200': ['2021LPL夏季赛', 20210607],
    '201': ['2021LCK夏季赛', 20210609],
    '202': ['2021LCS夏季赛', 20210605],
    '203': ['2021LEC夏季赛', 20210611],
    '208': ['S11LPL资格赛', 20210903],
    '209': ['S11LCK资格赛', 20210831]
}
