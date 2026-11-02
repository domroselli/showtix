import json

from tests.evals.runner import run


def test_runner_prints_one_line_per_case_and_score(tmp_path, capsys):
    cases = tmp_path / "cases.json"
    cases.write_text(json.dumps([
        {"name": "two plus two", "a": 2, "b": 2, "expected": 4},
        {"a": 1, "b": 1, "expected": 3},
        {"name": "crashes", "a": None, "b": 1, "expected": 1},
    ]))

    def check(case):
        got = case["a"] + case["b"]
        return got == case["expected"], f"got {got}"

    assert run(cases, check, argv=[]) == (1, 3)
    assert capsys.readouterr().out.splitlines() == [
        "PASS two plus two: got 4",
        "FAIL case 2: got 2",
        "FAIL crashes: error: TypeError: unsupported operand type(s) for +: 'NoneType' and 'int'",
        "Score: 1/3",
    ]


def test_runner_repeats_each_case(tmp_path, capsys):
    cases = tmp_path / "cases.json"
    cases.write_text(json.dumps([{"name": "steady"}, {"name": "flaky"}]))
    flaky_answers = iter([True, False, True])

    def check(case):
        if case["name"] == "steady":
            return True, "ok"
        ok = next(flaky_answers)
        return ok, "ok" if ok else "wrong answer"

    assert run(cases, check, argv=["--repeat", "3"]) == (5, 6)
    assert capsys.readouterr().out.splitlines() == [
        "PASS (3/3) steady: ok",
        "FAIL (2/3) flaky: wrong answer",
        "Score: 5/6",
    ]
