import datacraft


def test_priority_respected():
    examples = [
        {
            "id": "7e4cb372-78a4-4bda-96fb-22f5d9ed8ba4",
            "ts": "2023-10-15T19:48:37"
        },
        {
            "id": "bd6a9f17-59c2-45ee-808f-e7840f482949",
            "ts": "2023-10-14T17:38:51"
        }
    ]

    spec = datacraft.infer.from_examples(examples)
    assert spec["id"]["type"] == "uuid"
