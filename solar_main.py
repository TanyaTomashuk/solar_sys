# coding: utf-8
# license: GPLv3

import pygame as pg
from solar_vis import *
from solar_model import *
from solar_input import *
from solar_objects import *
import thorpy
import time
import numpy as np


class Container:
    def __init__(self):
        self.model_time = 0
        """Физическое время от начала расчёта.
        Тип: float"""
        self.displayed_time = 0
        self.perform_execution = False
        """Флаг цикличности выполнения расчёта"""
        self.alive = True
        self.browser = 0
        self.time_scale = 1000.0
        """Шаг по времени при моделировании.
        Тип: float"""
        self.physical_time = 0
        self.time_step = 0
        self.time_speed = 0
        self.space = 0
        self.start_button = 0
        self.space_objects = []
        """Список космических объектов."""
        self.timer = None
        self.path = 'initial_system'
        self.file =''
        """Путь до файла с симуляцией"""


c = Container()


def execution(delta):
    """
    Функция исполнения -- выполняется циклически, вызывая обработку всех небесных тел,
    а также обновляя их положение на экране.
    Цикличность выполнения зависит от значения глобальной переменной perform_execution.
    При perform_execution == True функция запрашивает вызов самой себя по таймеру через от 1 мс до 100 мс.
    """
    recalculate_space_objects_positions([dr.obj for dr in c.space_objects], delta)
    c.model_time += delta


def start_execution():
    """Обработчик события нажатия на кнопку Start.
    Запускает циклическое исполнение функции execution.
    """
    c.perform_execution = True


def pause_execution():
    c.perform_execution = False


def stop_execution():
    """Обработчик события нажатия на кнопку Start.
    Останавливает циклическое исполнение функции execution.
    """
    c.alive = False


def open_file():
    """Открывает диалоговое окно выбора имени файла и вызывает
    функцию считывания параметров системы небесных тел из данного файла.
    Считанные объекты сохраняются в глобальный список c.space_objects
    """
    c.model_time = 0.0
    in_filename = c.file
    c.space_objects = read_space_objects_data_from_file(in_filename)
    max_distance = max([max(abs(obj.obj.x), abs(obj.obj.y)) for obj in c.space_objects])
    calculate_scale_factor(max_distance)


def handle_events(events, menu):
    for event in events:
        menu.react(event)
        if event.type == pg.QUIT:
            c.alive = False


def slider_to_real(val):
    return np.exp(5 + val)


def slider_reaction(event):
    c.time_scale = slider_to_real(event.el.get_value())


def init_ui(screen):
    slider = thorpy.SliderX(100, (-10, 10), "Simulation speed")
    slider.user_func = slider_reaction
    button_stop = thorpy.make_button("Quit", func=stop_execution)
    button_pause = thorpy.make_button("Pause", func=pause_execution)
    button_play = thorpy.make_button("Play", func=start_execution)
    timer = thorpy.OneLineText("Seconds passed")

    button_load = thorpy.make_button(text="Load a file", func=open_file)

    box = thorpy.Box(elements=[
        slider,
        button_pause,
        button_stop,
        button_play,
        button_load,
        timer])
    reaction1 = thorpy.Reaction(reacts_to=thorpy.constants.THORPY_EVENT,
                                reac_func=slider_reaction,
                                event_args={"id": thorpy.constants.EVENT_SLIDE},
                                params={},
                                reac_name="slider reaction")
    box.add_reaction(reaction1)

    menu = thorpy.Menu(box)
    for element in menu.get_population():
        element.surface = screen

    box.set_topleft((0, 0))
    box.blit()
    box.update()
    return menu, box, timer


def main():
    """Главная функция главного модуля.
    Создаёт объекты графического дизайна библиотеки tkinter: окно, холст, фрейм с кнопками, кнопки.
    """
    print('Modelling started!')
    c.file = choose_path(c.path)
    c.physical_time = 0

    pg.init()

    width = 1000
    height = 900
    screen = pg.display.set_mode((width, height))
    last_time = time.perf_counter()
    drawer = Drawer(screen)
    menu, box, timer = init_ui(screen)
    c.perform_execution = True

    while c.alive:
        handle_events(pg.event.get(), menu)
        cur_time = time.perf_counter()
        if c.perform_execution:
            execution((cur_time - last_time) * c.time_scale)
            text = "%d seconds passed" % (int(c.model_time))
            timer.set_text(text)

        last_time = cur_time
        drawer.update(c.space_objects, box)
        time.sleep(1.0 / 60)

    print('Modelling finished!')


if __name__ == "__main__":
    main()
