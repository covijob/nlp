from duomenys import EVAL, nuskaityti_jsonl

FRAZES = EVAL / "frazes.jsonl"
TEISINGI = EVAL / "teisingi.jsonl"


def nuskaityti_frazes(kelias=FRAZES):
    return nuskaityti_jsonl(kelias)


def nuskaityti_teisingus(kelias=TEISINGI):
    return {irasas["frazes_id"]: set(irasas["fragmentai"]) for irasas in nuskaityti_jsonl(kelias)}


def precision_at_k(rezultatu_id, teisingi_id, k=5):
    if k <= 0:
        return 0.0
    return sum(1 for i in rezultatu_id[:k] if i in teisingi_id) / k


def rakto_tikslumas(frazes):
    raise NotImplementedError


def ivertinti(metodai, k=5):
    raise NotImplementedError
