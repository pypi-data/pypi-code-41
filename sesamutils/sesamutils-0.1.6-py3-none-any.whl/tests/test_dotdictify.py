from sesamutils import Dotdictify

test_dict = {
    "key1": "value1",
    "key2": {
        "key3": "value3",
        "key4": "value4",
        "key5": {
            "key6": "value6"
        }
    }
}


def test_read_nested_dict_item():

    dotd = Dotdictify(test_dict)
    assert dotd.key2.key5 == {"key6": "value6"}
    assert dotd.key2.key3 == "value3"


def test_read_root_level_dict_item():

    dotd= Dotdictify(test_dict)
    assert dotd.key1 == "value1"


def test_set_nested_dict_item():

    dotd = Dotdictify(test_dict)

    dotd.key2.key3 = "new_value"
    test_dict["key2"]["key3"] = "new_value"

    assert dotd.key2.key3 == "new_value"
    assert dotd == test_dict

