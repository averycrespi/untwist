from argparse import ArgumentParser
import json
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

from robber_baron import find_element


BOARD_SIZES = (4, 5)


def parse_args():
    """Parse command-line arguments."""
    parser = ArgumentParser(description="Play Wordtwist")
    parser.add_argument(
        "-s",
        "--board-size",
        type=int,
        default=4,
        choices=BOARD_SIZES,
        help="Board size; default 4",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    driver = webdriver.Chrome()

    new_game_url = f"https://wordtwist.puzzlebaron.com/init{args.board_size}.php"
    print(f"Loading new game URL: {new_game_url} ...")
    driver.get(new_game_url)
    board_url = find_element(driver, "div#newgameboard a").get_attribute("href")
    board_uid = board_url.split("u=")[-1]
    print(f"Extracted board UID: {board_uid}")

    # We need load the board URL _before_ requesting the board data,
    # otherwise WordTwist will complain that the game has already been completed
    print(f"Loading board URL: {board_url} ...")
    driver.get(board_url)
    data_url = f"https://wordtwist.puzzlebaron.com/boarddata.php?uid={board_uid}"
    print(f"Requesting board data from: {data_url} ...")
    board_data = json.loads(requests.get(data_url).text)
    print(f"Parsed board data: {json.dumps(board_data)}")

    print("Starting game and entering words ...")
    find_element(driver, "a#start").click()
    words = list(board_data["wordList"].keys())
    word_input = find_element(driver, "input#word")
    for word in words:
        word_input.send_keys(word)
        word_input.send_keys(Keys.RETURN)
        time.sleep(0.1)

    print("Submitting game ...")
    find_element(driver, "a#submit").click()
    find_element(driver, "div.TB_modal > div.alert a.yes").click()

    input("Press enter to quit: ")
    driver.quit()
