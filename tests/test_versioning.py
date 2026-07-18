from monitoring.golden_set.versioning import content_hash, golden_set_hash


def test_content_hash_string():
    hash1 = content_hash("test prompt")
    hash2 = content_hash("test prompt")
    hash3 = content_hash("different prompt")

    assert hash1 == hash2
    assert hash1 != hash3


def test_content_hash_dict_sorting():
    dict1 = {"b": 2, "a": 1}
    dict2 = {"a": 1, "b": 2}

    # Should hash to the exact same value due to sort_keys=True
    assert content_hash(dict1) == content_hash(dict2)


def test_golden_set_hash_ordering():
    hashes1 = ["hashA", "hashB", "hashC"]
    hashes2 = ["hashC", "hashA", "hashB"]

    # Order independent hashing
    assert golden_set_hash(hashes1) == golden_set_hash(hashes2)
