import random
from time import sleep
from typing import Type

import pyautogui
import selenium
from selenium.webdriver import ActionChains
from selenium.webdriver.remote.webdriver import WebDriver

from core.geometry import Point, WebPoint
from loguru import logger
from selenium.webdriver.common.by import By

from core.instruction import Instruction
from core.strategy import Strategy


class Human:
    def __init__(self, strategy: Type[Strategy], instruction: Type[Instruction], pause_between_actions: float = 0.011):
        self.monitor_max_x, self.monitor_max_y = pyautogui.size()
        self.strategy = strategy
        self.pause_between_actions = pause_between_actions
        pyautogui.PAUSE = pause_between_actions
        self.instruction = instruction
        self.point_class = Point

    def follow_instruction(self):
        self.instruction.perform(human=self)

    def get_current_mouse_position(self):
        x, y = pyautogui.position()
        logger.debug(f"get current mouse position x:{x} y:{y}")
        return self.point_class(x, y)

    def consider_screen_limits(self, point):
        logger.debug("fix point by consider screen limits")
        if point.x > self.monitor_max_x:
            point.x = self.monitor_max_x
        if point.y > self.monitor_max_y:
            point.y = self.monitor_max_y
        if point.x < 0:
            point.x = 0
        if point.y < 0:
            point.y = 0

    def random_sleep(self):
        sleep_time = self.strategy.generate_sleep_time()
        logger.debug(f"random sleep: {sleep_time}")
        sleep(sleep_time)

    def random_click_sleep(self):
        sleep_time = self.strategy.generate_click_sleep_time()
        logger.debug(f"random click sleep: {sleep_time}")
        sleep(sleep_time)

    def click(self):
        logger.debug("click started")
        self.random_sleep()
        self.mouse_down()
        self.random_click_sleep()
        self.mouse_up()
        logger.debug("click finished")

    @staticmethod
    def mouse_down():
        logger.debug("mouseDown")
        pyautogui.mouseDown(button='left')

    def mouse_up(self):
        logger.debug("mouseUp")
        pyautogui.mouseUp(button='left')

    def random_wandering(self):
        logger.debug(f"random wandering started")
        again = random.choice((True, False))

        while again:
            current_position = self.get_current_mouse_position()
            offset_x = random.uniform(-random.randint(50, 600), random.randint(50, 600))
            offset_y = random.uniform(-random.randint(50, 600), random.randint(50, 600))
            destination = self.point_class(
                current_position.x + offset_x,
                current_position.y + offset_y,
            )
            self.random_sleep()
            self.move(from_=current_position, to_=destination)
            again = random.choice((True, False))

        logger.debug(f"random wandering finished")
        self.random_sleep()

    def move(self, from_, to_):
        logger.debug("Human: move")
        points = self.strategy.get_points(from_, to_)
        for point in points:
            logger.debug(f"point {point.x} {point.y} {point.duration}")
            self.consider_screen_limits(point)
            pyautogui.moveTo(point.x, point.y, point.duration)
        else:
            last = point
            return last

    def move_to_screen_center(self, offset_x: int = 0, offset_y: int = 0):
        screen_center = self.point_class(self.monitor_max_x / 2 + offset_x, self.monitor_max_y / 2 + offset_y)
        self.move(self.get_current_mouse_position(), screen_center)


class WebHuman(Human):
    def __init__(
        self,
        start_url: str,
        strategy: Type[Strategy],
        instruction: Type[Instruction],
        pause_between_actions: float = 0.011,
        driver: WebDriver = selenium.webdriver.Chrome,
        dpi: float = 1,
    ):
        super().__init__(
            strategy=strategy,
            instruction=instruction,
            pause_between_actions=pause_between_actions
        )
        options = selenium.webdriver.ChromeOptions()
        # --- Important for get truly global coordinates from xpath ---
        options.add_argument(f"--force-device-scale-factor={dpi}")
        self.driver = driver(options=options)
        self.driver.maximize_window()
        # ------------------------------------------------------
        self.nav_height = self.driver.execute_script('return window.outerHeight - window.innerHeight;')
        self.start_url = start_url
        self.point_class = WebPoint
        self.inner_height = self.driver.execute_script('return window.innerHeight;')

    def get_current_mouse_position(self):
        x, y = pyautogui.position()
        logger.debug(f"get current mouse position x:{x} y:{y}")
        return WebPoint(x, y)

    def get_element_center(self, xpath):
        element = self.driver.find_element(By.XPATH, xpath)
        logger.debug(f"nav height: {self.nav_height}")
        logger.debug(f"element location x: {element.location.get('x')} y: {element.location.get('y')}")
        x = float(element.location.get("x")) + float(element.size.get('width')) / 2
        y = (
            float(self.nav_height) +
            float(element.location.get("y")) +
            float(element.size.get('height')) / 2
        )
        logger.debug(f"get element center x: {x}, y: {y}")
        center = self.point_class(
            x=int(x),
            y=int(y),
            xpath=xpath,
        )
        self.consider_window_offsets(point=center)
        return center

    def consider_window_offsets(self, point):
        window_position = self.driver.get_window_position()
        x_offset = window_position['x']
        y_offset = window_position['y']
        logger.debug(f"window offsets: {x_offset}, {y_offset}")
        point.x += x_offset
        point.y += y_offset

    def get_scrolled_offset_y(self, bottom: bool = False) -> int:
        offset_y = self.driver.execute_script("return window.pageYOffset;")
        if bottom:
            return offset_y + self.inner_height
        return offset_y

    def scroll_to_element(self, xpath):
        element_center = self.get_element_center(xpath)
        offset_y = self.get_scrolled_offset_y(bottom=True)
        while element_center.y > offset_y:
            pyautogui.scroll(self.strategy.get_scrolling_amount())
            offset_y = self.get_scrolled_offset_y(bottom=True)
            self.random_click_sleep()

    def move(self, from_: WebPoint, to_: WebPoint, never_scroll: bool = False):
        logger.debug("WebHuman: move")
        logger.debug(f"move started from: ({from_.x}, {from_.y}) to: ({to_.x}, {to_.y} xpath: {to_.xpath})")
        if self.is_scroll_required(point=to_) and not never_scroll:
            logger.debug(f"move: scroll required")
            self.move_to_screen_center(*self.strategy.get_screen_center_offsets())
            self.scroll_to_element(to_.xpath)
            current_bottom_y = self.get_full_window_height() + self.get_scrolled_offset_y()
            to_.y = self.get_full_window_height() - (current_bottom_y - to_.y)
            from_ = self.get_current_mouse_position()
        super().move(from_, to_)

    def get_full_window_height(self):
        return self.inner_height + self.nav_height

    def is_scroll_required(self, point: WebPoint):
        if point.y > self.monitor_max_y:
            return True

    def random_wandering(self):
        logger.debug(f"random wandering started")
        again = random.choice((True, False))

        while again:
            current_position = self.get_current_mouse_position()
            destination = self.strategy.get_random_wandering_destination(current_position=current_position)
            self.random_sleep()
            self.move(from_=current_position, to_=destination, never_scroll=True)
            again = random.choice((True, False))

        logger.debug(f"random wandering finished")
        self.random_sleep()


