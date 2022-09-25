from core.geometry import WebPoint
from core.human import WebHuman
from core.instruction import Instruction
from core.strategy import HumanLikeStrategy


class AutoDrawInstruction(Instruction):
    @staticmethod
    def perform(human: WebHuman):
        human.driver.get(url=human.start_url)
        for _ in range(3):
            human.random_wandering()
        current_point = human.get_current_mouse_position
        human.random_wandering()
        button_green = human.get_element_center("//div[@class='button green']")
        human.random_sleep()
        human.move(current_point(), button_green)
        human.click()
        human.random_wandering()
        pencil = human.get_element_center("//div[@class='tool pencil']")
        human.move(current_point(), pencil)
        human.click()
        human.random_wandering()
        canvas = human.get_element_center("//canvas[@id='main-canvas']")
        human.move(current_point(), canvas)
        for _ in range(3):
            for i in range(10):
                human.mouse_down()
                last = current_point()
                last_point = WebPoint.get_point_near_another(last, 100, 100)
                human.move(current_point(), last_point)
                human.random_click_sleep()
                human.mouse_up()
                human.random_click_sleep()
            human.random_wandering()


human = WebHuman(
    start_url="https://www.autodraw.com/",
    strategy=HumanLikeStrategy,
    instruction=AutoDrawInstruction,
)
human.follow_instruction()
