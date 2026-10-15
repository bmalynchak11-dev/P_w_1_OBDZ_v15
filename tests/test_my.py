import pytest
from conftest import load
from helpers import entity, model, rel

M = load(5)

@pytest.mark.parametrize("args, expected", [
    # Випадок 1: Коректна модель без порушень
    (
        (model([
            entity("DEPARTMENT", "int id PK", "string name"),
            entity("EMPLOYEE", "int id PK", "int department_id FK", "string name")
        ], [
            rel("DEPARTMENT", "one", "EMPLOYEE", "zero_many", "працює", False)
        ]),),
        []
    ),
    # Випадок 2: Сутність без PK та невідомий FK атрибут
    (
        (model([
            entity("AUDIENCE", "string number"),
            entity("LESSON", "int id PK", "int fake_key FK")
        ], []),),
        ["BAD_FK LESSON.fake_key", "NO_PK AUDIENCE"]
    ),
    # Випадок 3: Зв'язок 1:1, де в жодній сутності немає FK
    (
        (model([
            entity("CITIZEN", "int id PK"),
            entity("PASSPORT", "int id PK")
        ], [
            rel("CITIZEN", "one", "PASSPORT", "zero_one", "має", False)
        ]),),
        ["ONE_TO_ONE_NO_FK CITIZEN PASSPORT"]
    ),
    # Випадок 4: Зв'язок N:1 без FK у дочірній сутності (зворотний напрямок зв'язку)
    (
        (model([
            entity("STUDENT", "int id PK"),
            entity("STUDY_GROUP", "int id PK")
        ], [
            rel("STUDENT", "zero_many", "STUDY_GROUP", "one", "належить", False)
        ]),),
        ["MISSING_FK STUDENT STUDY_GROUP"]
    )
])
def test_my_cases(args, expected):
    assert M.validate_keys(*args) == expected