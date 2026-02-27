from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, List


# =========================
# Immutable Value Object
# =========================

@dataclass(frozen=True)
class CoffeeOrder:
    base: str
    size: str
    milk: str
    syrups: Tuple[str, ...]
    sugar: int
    iced: bool
    price: float
    description: str

    def __str__(self) -> str:
        return self.description if self.description else f"{self.base} ({self.size}) - {self.price:.2f} ₽"


# =========================
# Builder
# =========================

class CoffeeOrderBuilder:
    """
    Fluent Builder для заказа кофе.

    Правила:
    - base и size обязательны
    - сиропов максимум MAX_SYRUPS
    - сахар в диапазоне 0..MAX_SUGAR
    - дубликаты сиропов игнорируются
    - build() возвращает новый CoffeeOrder
    - билдер можно переиспользовать
    """

    BASE_PRICES = {
        "espresso": 200.0,
        "americano": 250.0,
        "latte": 300.0,
        "cappuccino": 320.0,
    }

    SIZE_MULTIPLIERS = {
        "small": 1.0,
        "medium": 1.2,
        "large": 1.4,
    }

    MILK_PRICES = {
        "none": 0.0,
        "whole": 30.0,
        "skim": 30.0,
        "oat": 60.0,
        "soy": 50.0,
    }

    SYRUP_PRICE = 40.0
    ICED_PRICE = 20.0

    MAX_SUGAR = 5
    MAX_SYRUPS = 4

    def __init__(self) -> None:
        self._base: str | None = None
        self._size: str | None = None
        self._milk: str = "none"
        self._syrups: List[str] = []
        self._sugar: int = 0
        self._iced: bool = False

    # ===== Fluent methods =====

    def set_base(self, base: str) -> "CoffeeOrderBuilder":
        if base not in self.BASE_PRICES:
            raise ValueError("Недопустимая база")
        self._base = base
        return self

    def set_size(self, size: str) -> "CoffeeOrderBuilder":
        if size not in self.SIZE_MULTIPLIERS:
            raise ValueError("Недопустимый размер")
        self._size = size
        return self

    def set_milk(self, milk: str) -> "CoffeeOrderBuilder":
        if milk not in self.MILK_PRICES:
            raise ValueError("Недопустимый тип молока")
        self._milk = milk
        return self

    def add_syrup(self, name: str) -> "CoffeeOrderBuilder":
        if name in self._syrups:
            return self
        if len(self._syrups) >= self.MAX_SYRUPS:
            raise ValueError("Превышен лимит сиропов")
        self._syrups.append(name)
        return self

    def set_sugar(self, teaspoons: int) -> "CoffeeOrderBuilder":
        if not (0 <= teaspoons <= self.MAX_SUGAR):
            raise ValueError("Сахар должен быть 0..5")
        self._sugar = teaspoons
        return self

    def set_iced(self, iced: bool = True) -> "CoffeeOrderBuilder":
        self._iced = iced
        return self

    def clear_extras(self) -> "CoffeeOrderBuilder":
        self._milk = "none"
        self._syrups = []
        self._sugar = 0
        self._iced = False
        return self

    # ===== Build =====

    def build(self) -> CoffeeOrder:
        if self._base is None:
            raise ValueError("Не задана база")
        if self._size is None:
            raise ValueError("Не задан размер")

        price = self._calculate_price()
        description = self._build_description(price)

        return CoffeeOrder(
            base=self._base,
            size=self._size,
            milk=self._milk,
            syrups=tuple(self._syrups),
            sugar=self._sugar,
            iced=self._iced,
            price=price,
            description=description,
        )

    # ===== Internal helpers =====

    def _calculate_price(self) -> float:
        base_price = self.BASE_PRICES[self._base]  # type: ignore
        size_mult = self.SIZE_MULTIPLIERS[self._size]  # type: ignore
        milk_price = self.MILK_PRICES[self._milk]
        syrup_total = len(self._syrups) * self.SYRUP_PRICE
        iced_price = self.ICED_PRICE if self._iced else 0.0

        return (base_price * size_mult) + milk_price + syrup_total + iced_price

    def _build_description(self, price: float) -> str:
        parts = [f"{self._size} {self._base}"]

        if self._milk != "none":
            parts.append(f"with {self._milk} milk")

        if self._syrups:
            parts.append("+" + ", ".join(self._syrups))

        if self._iced:
            parts.append("(iced)")

        if self._sugar > 0:
            parts.append(f"{self._sugar} tsp sugar")

        desc = " ".join(parts)
        return f"{desc} - {price:.2f} ₽"


# =========================
# Tests (assert)
# =========================

if __name__ == "__main__":
    builder = CoffeeOrderBuilder()

    # Базовый заказ
    order = (
        builder
        .set_base("latte")
        .set_size("medium")
        .set_milk("oat")
        .add_syrup("vanilla")
        .set_sugar(2)
        .set_iced()
        .build()
    )

    assert isinstance(order.price, float)
    assert order.price > 0
    assert "latte" in order.description
    assert "vanilla" in order.description

    # Переиспользование билдера
    order1 = builder.build()
    order2 = builder.set_sugar(0).build()

    assert order1 != order2
    assert order1.sugar == 2
    assert order2.sugar == 0

    # Валидация обязательных полей
    try:
        CoffeeOrderBuilder().set_size("small").build()
        assert False
    except ValueError:
        pass

    try:
        CoffeeOrderBuilder().set_base("espresso").build()
        assert False
    except ValueError:
        pass

    # Лимиты
    try:
        CoffeeOrderBuilder().set_base("espresso").set_size("small").set_sugar(6)
        assert False
    except ValueError:
        pass

    # Дубликаты сиропов
    b = CoffeeOrderBuilder().set_base("espresso").set_size("small")
    b.add_syrup("caramel").add_syrup("caramel")
    o = b.build()
    assert len(o.syrups) == 1

    # iced увеличивает цену
    b = CoffeeOrderBuilder().set_base("espresso").set_size("small")
    price_no_ice = b.build().price
    price_ice = b.set_iced(True).build().price
    assert price_ice > price_no_ice

    print("Все тесты пройдены ✅")
