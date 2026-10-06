import json
import urllib.request
import urllib.error
from pathlib import Path

# ==========================================
# PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

SKILL_FILE = BASE_DIR / "skill" / "syllabusguard.md"
TEST_FILE = BASE_DIR / "evaluation" / "test_cases.json"
RESULT_FILE = BASE_DIR / "evaluation" / "results.json"

# ==========================================
# OLLAMA
# ==========================================

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2:3b"


# ==========================================
# LOAD FILES
# ==========================================

def load_skill():

    with open(
        SKILL_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        return file.read()


def load_tests():

    with open(
        TEST_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


# ==========================================
# ASK OLLAMA
# ==========================================

def ask_ollama(system_prompt, user_prompt):

    data = {
        "model": MODEL,

        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],

        "stream": False,

        "format": "json",

        "options": {
            "temperature": 0
        }
    }

    request_data = json.dumps(data).encode("utf-8")

    request = urllib.request.Request(
        OLLAMA_URL,
        data=request_data,
        headers={
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=300
        ) as response:

            result = json.loads(
                response.read().decode("utf-8")
            )

            return result["message"]["content"]

    except urllib.error.URLError as error:

        print()
        print("OLLAMA ERROR:")
        print(error)
        print()

        return None


# ==========================================
# CREATE USER INPUT
# ==========================================

def create_input(test_case):

    return f"""
OFFICIAL SYLLABUS:

{json.dumps(
    test_case["syllabus"],
    indent=2
)}

STUDY MATERIAL:

{json.dumps(
    test_case["study_material"],
    indent=2
)}

PREVIOUS-YEAR QUESTIONS:

{json.dumps(
    test_case["pyqs"],
    indent=2
)}
"""


# ==========================================
# RUN WITHOUT SKILL
# ==========================================

def run_without_skill(test_case):

    system_prompt = """
You are a general AI assistant.

Analyze the supplied syllabus, study material,
and previous-year questions.

Return ONLY valid JSON.

Use exactly this structure:

{
    "covered": [],
    "partially_covered": [],
    "missing": [],
    "out_of_syllabus": [],
    "coverage_percentage": 0,
    "priority_order": [],
    "recommended_study_order": [],
    "warnings": []
}

Do not invent information.
"""


    return ask_ollama(
        system_prompt,
        create_input(test_case)
    )


# ==========================================
# RUN WITH SKILL
# ==========================================

def run_with_skill(test_case, skill):

    system_prompt = f"""
You are an AI agent using the SyllabusGuard Agent Skill.

Follow the Skill carefully.

==============================
SYLLABUSGUARD SKILL
==============================

{skill}

==============================
END OF SKILL
==============================

STRICT CLASSIFICATION:

COVERED:
A topic from the official syllabus that is
reasonably covered by the study material.

PARTIALLY COVERED:
A topic from the official syllabus where only
part of the topic is covered.

MISSING:
ONLY topics that are present in the official
syllabus but are not adequately covered.

OUT_OF_SYLLABUS:
ONLY topics present in the study material that
do not correspond to an official syllabus topic.

IMPORTANT:

A topic MUST NOT appear in both MISSING and
OUT_OF_SYLLABUS.

For example:

Syllabus:
Matrices
Determinants
Differential Equations

Study material:
Matrices
Determinants
Probability

Correct:

covered:
Matrices
Determinants

missing:
Differential Equations

out_of_syllabus:
Probability

Probability must NOT be classified as missing.

Return ONLY valid JSON.

Use exactly:

{{
    "covered": [],
    "partially_covered": [],
    "missing": [],
    "out_of_syllabus": [],
    "coverage_percentage": 0,
    "priority_order": [],
    "recommended_study_order": [],
    "warnings": []
}}

Never invent information.
Preserve official syllabus wording.
Prefer accuracy over guessing.
"""

    return ask_ollama(
        system_prompt,
        create_input(test_case)
    )


# ==========================================
# PARSE JSON
# ==========================================

def parse_result(raw):

    if raw is None:
        return None

    try:

        return json.loads(raw)

    except json.JSONDecodeError:

        return None


# ==========================================
# NORMALIZE LIST
# ==========================================

def normalize_list(value):

    if not isinstance(value, list):
        return set()

    return {
        str(item).strip().lower()
        for item in value
    }


# ==========================================
# SCORE RESULT
# ==========================================

def score_result(result, expected):

    if result is None:
        return {
            "score": 0,
            "maximum": 4,
            "accuracy": 0
        }

    fields = [
        "covered",
        "partially_covered",
        "missing",
        "out_of_syllabus"
    ]

    correct = 0

    for field in fields:

        actual = normalize_list(
            result.get(field, [])
        )

        target = normalize_list(
            expected.get(field, [])
        )

        if actual == target:
            correct += 1

    maximum = len(fields)

    accuracy = round(
        (correct / maximum) * 100,
        2
    )

    return {
        "score": correct,
        "maximum": maximum,
        "accuracy": accuracy
    }


# ==========================================
# FIND EXPECTED ANSWER
# ==========================================

def get_expected(test_case):

    expected = test_case.get("expected")

    if expected is None:

        return {
            "covered": [],
            "partially_covered": [],
            "missing": [],
            "out_of_syllabus": []
        }

    return expected


# ==========================================
# MAIN BENCHMARK
# ==========================================

def main():

    print()
    print("==========================================")
    print("       SYLLABUSGUARD BENCHMARK")
    print("==========================================")
    print()

    print("Loading Skill...")

    skill = load_skill()

    print("Skill loaded.")
    print()

    print("Loading test cases...")

    test_cases = load_tests()

    print(
        f"Loaded {len(test_cases)} test cases."
    )

    print()

    results = []

    skill_total = 0
    baseline_total = 0

    skill_max = 0
    baseline_max = 0

    # ======================================
    # RUN ALL TEST CASES
    # ======================================

    for index, test_case in enumerate(
        test_cases,
        start=1
    ):

        test_id = test_case["id"]

        print("------------------------------------------")
        print(
            f"[{index}/{len(test_cases)}] {test_id}"
        )
        print("------------------------------------------")

        print("Running WITHOUT Skill...")

        baseline_raw = run_without_skill(
            test_case
        )

        baseline_result = parse_result(
            baseline_raw
        )

        print("Running WITH Skill...")

        skill_raw = run_with_skill(
            test_case,
            skill
        )

        skill_result = parse_result(
            skill_raw
        )

        # ----------------------------------
        # Expected answer
        # ----------------------------------

        expected = get_expected(
            test_case
        )

        # ----------------------------------
        # Scores
        # ----------------------------------

        baseline_score = score_result(
            baseline_result,
            expected
        )

        skill_score = score_result(
            skill_result,
            expected
        )

        baseline_total += baseline_score["score"]
        baseline_max += baseline_score["maximum"]

        skill_total += skill_score["score"]
        skill_max += skill_score["maximum"]

        improvement = round(
            skill_score["accuracy"]
            - baseline_score["accuracy"],
            2
        )

        print(
            f"Without Skill: {baseline_score['accuracy']}%"
        )

        print(
            f"With Skill:    {skill_score['accuracy']}%"
        )

        print(
            f"Improvement:   {improvement:+.2f}%"
        )

        print()

        results.append(
            {
                "id": test_id,

                "without_skill": {
                    "result": baseline_result,
                    "score": baseline_score
                },

                "with_skill": {
                    "result": skill_result,
                    "score": skill_score
                },

                "expected": expected,

                "improvement": improvement
            }
        )

    # ======================================
    # OVERALL RESULTS
    # ======================================

    baseline_accuracy = round(
        (baseline_total / baseline_max) * 100,
        2
    ) if baseline_max else 0

    skill_accuracy = round(
        (skill_total / skill_max) * 100,
        2
    ) if skill_max else 0

    overall_improvement = round(
        skill_accuracy - baseline_accuracy,
        2
    )

    # ======================================
    # COUNT EFFECT
    # ======================================

    helped = 0
    same = 0
    hurt = 0

    for result in results:

        improvement = result["improvement"]

        if improvement > 0:
            helped += 1

        elif improvement < 0:
            hurt += 1

        else:
            same += 1

    # ======================================
    # FINAL REPORT
    # ======================================

    report = {

        "project": "SyllabusGuard",

        "model": MODEL,

        "test_cases": len(test_cases),

        "baseline": {
            "accuracy": baseline_accuracy
        },

        "with_skill": {
            "accuracy": skill_accuracy
        },

        "improvement": overall_improvement,

        "skill_effect": {
            "helped": helped,
            "no_change": same,
            "hurt": hurt
        },

        "results": results
    }

    # ======================================
    # SAVE RESULTS
    # ======================================

    with open(
        RESULT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=4,
            ensure_ascii=False
        )

    # ======================================
    # PRINT SUMMARY
    # ======================================

    print()
    print()
    print("==========================================")
    print("          FINAL BENCHMARK")
    print("==========================================")
    print()

    print(
        f"Test Cases:        {len(test_cases)}"
    )

    print(
        f"Without Skill:     {baseline_accuracy}%"
    )

    print(
        f"With Skill:        {skill_accuracy}%"
    )

    print(
        f"Improvement:       {overall_improvement:+.2f}%"
    )

    print()

    print(
        f"Skill helped:      {helped}"
    )

    print(
        f"No major effect:   {same}"
    )

    print(
        f"Skill hurt:        {hurt}"
    )

    print()

    print(
        "Results saved to:"
    )

    print(
        "evaluation/results.json"
    )

    print()

    print("==========================================")
    print("       BENCHMARK COMPLETED")
    print("==========================================")


# ==========================================
# START
# ==========================================

if __name__ == "__main__":
    main()
    