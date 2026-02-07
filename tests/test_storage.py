from tuda.storage import EncryptedDB


def test_insert_and_fetch_message(tmp_path):
    db = EncryptedDB(str(tmp_path / "messages.db"), "test-key")
    db.init_schema()

    db.insert_messages(
        [
            ("id-1", "subject", "sender@example.com", "snippet", "1000"),
        ]
    )

    row = db.fetch_message("id-1")
    assert row == ("subject", "sender@example.com", "snippet", "1000")


def test_list_messages_sorted(tmp_path):
    db = EncryptedDB(str(tmp_path / "messages.db"), "test-key")
    db.init_schema()
    db.insert_messages(
        [
            ("old", "s1", "a", "sn1", "1"),
            ("new", "s2", "b", "sn2", "2"),
        ]
    )

    rows = db.list_messages(limit=2)
    assert [r[0] for r in rows] == ["new", "old"]
