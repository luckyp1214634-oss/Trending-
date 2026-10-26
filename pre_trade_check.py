"""Trade se pehle 25-point checklist - computer version.
Har point ko True/False me bharo, phir ye batayega TRADE ya NO TRADE.
"""
MANDATORY = [
    "Trend daily chart par clear hai",
    "Stop-loss level clear hai",
    "Risk:Reward >= 1.5 hai",
    "Ek trade ka risk <= 1% hai",
    "Aaj ka total loss < 2% hai",
    "Volume normal se kam nahi hai",
    "Aaj koi bada news/earnings nahi hai",
    "Market trend ke against nahi ja rahe",
    "Entry level clear hai",
    "Exit plan clear hai",
]


def run_checklist(answers):
    """answers: dict {point_number (1-25): True/False}"""
    fails = [n for n in range(1, 11) if not answers.get(n, False)]
    passed = sum(1 for v in answers.values() if v)
    if fails:
        return {"final": "NO TRADE", "passed": passed,
                "reason": f"Mandatory points FAIL: {fails}"}
    if passed < 16:
        return {"final": "NO TRADE", "passed": passed,
                "reason": "Total PASS 16 se kam hai, confirmation kamzor hai."}
    return {"final": "TRADE (risk rules ke saath)",
            "passed": passed, "reason": "Checklist PASS hai."}


if __name__ == "__main__":
    # Example: sab pass
    example = {n: True for n in range(1, 26)}
    print(run_checklist(example))
    # Example: ek mandatory fail
    bad = {n: True for n in range(1, 26)}
    bad[3] = False
    print(run_checklist(bad))
