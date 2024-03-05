#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Самостоятельно изучите работу с пакетом click
# для построения интерфейса командной строки (CLI). 
# Для своего варианта лабораторной работы 2.16 
# необходимо реализовать интерфейс командной 
# строки с использованием пакета click.

import bisect
import json
import os

import click
from jsonschema import ValidationError, validate


def add_route(routes, start, end, number):
    """
    Добавить данные о маршруте.
    """
    is_dirty = False
    route = {
        "начальный пункт": start.lower(),
        "конечный пункт": end.lower(),
        "номер маршрута": number,
    }
    if route not in routes:
        bisect.insort(
            routes,
            route,
            key=lambda item: item.get("номер маршрута"),
        )
        is_dirty = True
    else:
        print("Данный маршрут уже добавлен.")
    return routes, is_dirty


def display_routes(routes):
    """
    Отобразить список маршрутов.
    """
    if routes:
        line = "+-{}-+-{}-+-{}-+".format("-" * 30, "-" * 20, "-" * 8)
        print(line)
        print("| {:^30} | {:^20} | {:^8} |".format("Начало", "Конец", "Номер"))
        print(line)
        for route in routes:
            print(
                "| {:<30} | {:<20} | {:>8} |".format(
                    route.get("начальный пункт", ""),
                    route.get("конечный пункт", ""),
                    route.get("номер маршрута", ""),
                )
            )
        print(line)
    else:
        print("Список маршрутов пуст.")


def select_routes(routes, name_point):
    """
    Выбрать маршруты с заданным пунктом отправления или прибытия.
    """
    selected = []
    for route in routes:
        if (
            route["начальный пункт"] == name_point
            or route["конечный пункт"] == name_point
        ):
            selected.append(route)

    return selected


def save_routes(file_name, routes):
    """
    Сохранить все маршруты в файл JSON.
    """
    # Открыть файл с заданным именем для записи.
    with open(file_name, "w") as file_out:
        # Записать данные из словаря в формат JSON и сохранить их
        # в открытый файл.
        json.dump(routes, file_out, ensure_ascii=False, indent=4)


def load_routes(file_name):
    """
    Загрузить все маршруты из файла JSON.
    """
    schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "начальный пункт": {"type": "string"},
                "конечный пункт": {"type": "string"},
                "номер маршрута": {"type": "integer"},
            },
            "required": [
                "начальный пункт",
                "конечный пункт",
                "номер маршрута",
            ],
        },
    }
    if not os.path.exists(file_name):
        return []
    # Открыть файл с заданным именем и прочитать его содержимое.
    with open(file_name, "r") as file_in:
        data = json.load(file_in)  # Прочитать данные из файла

    try:
        # Валидация
        validate(instance=data, schema=schema)
        print("JSON валиден по схеме.")
        return data
    except ValidationError as e:
        print(f"Ошибка валидации: {e.message}")
        return []


@click.group()
def command():
    pass


# Команда для добавления нового маршрута в базу данных.


@command.command()
@click.argument("filename")
@click.option("-s", "--start", required=True, help="The route start")
@click.option("-e", "--end", required=True, help="The route endpoint")
@click.option(
    "-n", "--number", required=True, type=int, help="The number of route"
)
def add(filename, start, end, number):
    """
    Add a new route.
    """
    routes = load_routes(filename)

    routes, is_dirty = add_route(routes, start.lower(), end.lower(), number)
    if is_dirty:
        save_routes(filename, routes)


@command.command()
@click.argument("filename")
@click.option(
    "-p",
    "--point",
    required=True,
    help="Routes starting or ending at this point",
)
def select(filename, point):
    """
    Select the routes
    """
    point = point.lower()
    routes = load_routes(filename)
    selected_routes = select_routes(routes, point)
    display_routes(selected_routes)


@command.command()
@click.argument("filename")
def display(filename):
    """
    Display all routes
    """
    routes = load_routes(filename)
    display_routes(routes)


if __name__ == "__main__":
    command()
