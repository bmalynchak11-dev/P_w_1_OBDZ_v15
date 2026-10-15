"""Варіант 15 (Задача 5): Перевірка ключів."""
import copy

def validate_keys(model: dict) -> list[str]:
    # Захист від мутації вхідних даних
    m = copy.deepcopy(model)
    entities = m.get("entities", {})
    relationships = m.get("relationships", [])

    violations = set()

    # Збираємо інформацію про сутності та їхні первинні ключі
    entity_pks = {}
    for ent_name, attrs in entities.items():
        pks = [a["name"] for a in attrs if "PK" in a.get("keys", [])]
        entity_pks[ent_name] = pks
        if not pks:
            violations.add(f"NO_PK {ent_name}")

    # Множина всіх валідних пар (parent_entity, parent_pk_name)
    # Згідно з угодою: <parent малими>_<pk>
    valid_fk_targets = {}
    for parent_name, pks in entity_pks.items():
        for pk in pks:
            expected_fk = f"{parent_name.lower()}_{pk}"
            valid_fk_targets[expected_fk] = (parent_name, pk)

    # Перевірка BAD_FK для всіх атрибутів
    for ent_name, attrs in entities.items():
        for attr in attrs:
            if "FK" in attr.get("keys", []):
                attr_name = attr.get("name", "")
                if attr_name in valid_fk_targets:
                    target_ent, _ = valid_fk_targets[attr_name]
                    # Сутність не може посилатися сама на себе за угодою цієї перевірки
                    if target_ent == ent_name:
                        violations.add(f"BAD_FK {ent_name}.{attr_name}")
                else:
                    violations.add(f"BAD_FK {ent_name}.{attr_name}")

    # Допоміжна функція визначення сторони "багато"
    def is_many(card: str) -> bool:
        return card in ("zero_many", "one_many")

    # Перевірка зв'язків
    for rel in relationships:
        a = rel.get("a")
        b = rel.get("b")
        a_card = rel.get("a_card")
        b_card = rel.get("b_card")

        many_a = is_many(a_card)
        many_b = is_many(b_card)

        # M:N зв'язки у цій задачі не перевіряються
        if many_a and many_b:
            continue

        # Зв'язок 1:1
        if not many_a and not many_b:
            # Шукаємо, чи є FK в A на B, або в B на A
            has_fk = False

            # Перевірка FK у A на B
            b_pks = entity_pks.get(b, [])
            for pk in b_pks:
                expected_fk = f"{b.lower()}_{pk}"
                for attr in entities.get(a, []):
                    if attr.get("name") == expected_fk and "FK" in attr.get("keys", []):
                        has_fk = True
                        break

            # Перевірка FK у B на A
            a_pks = entity_pks.get(a, [])
            for pk in a_pks:
                expected_fk = f"{a.lower()}_{pk}"
                for attr in entities.get(b, []):
                    if attr.get("name") == expected_fk and "FK" in attr.get("keys", []):
                        has_fk = True
                        break

            if not has_fk:
                violations.add(f"ONE_TO_ONE_NO_FK {a} {b}")

        # Зв'язок 1:N або N:1 (рівно одна сторона "багато")
        else:
            # Якщо a_card - many, то A є дочірньою (багато A на один B), а B - батьківською
            # Якщо b_card - many, то B є дочірньою (багато B на один A), а A - батьківською
            if many_a:
                child, parent = a, b
            else:
                child, parent = b, a

            parent_pks = entity_pks.get(parent, [])
            # Шукаємо хоча б один валідний FK у дочірній сутності, що вказує на батьківську
            has_matching_fk = False
            for pk in parent_pks:
                expected_fk = f"{parent.lower()}_{pk}"
                for attr in entities.get(child, []):
                    if attr.get("name") == expected_fk and "FK" in attr.get("keys", []):
                        has_matching_fk = True
                        break

            if not has_matching_fk:
                violations.add(f"MISSING_FK {child} {parent}")

    return sorted(list(violations))