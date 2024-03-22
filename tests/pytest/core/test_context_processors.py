from benefits.core.context_processors import unique_values


def test_unique_values():
    original_list = ["a", "b", "c", "a", "a", "zzz", "b", "c", "d", "b"]

    new_list = unique_values(original_list)

    assert new_list == ["a", "b", "c", "zzz", "d"]
